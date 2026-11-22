"""
fetch_energia_sadi.py
=====================
ETL de datos energéticos del Sistema Argentino de Interconexión (SADI)
para las 24 jurisdicciones de Argentina.

Fuentes oficiales públicas (Datos Abiertos de Energía Argentina - datos.energia.gob.ar):
1. Centrales de Generación Eléctrica (Secretaría de Energía / CAMMESA):
   http://datos.energia.gob.ar/dataset/c62df6c6-73af-4039-b956-db081ff6eebe/resource/230fdf38-8f12-4017-a1e8-d7a1bc4a1c1c/download/generacin-elctrica-centrales-de-generacin.csv
2. Potencia Instalada Histórica CAMMESA:
   http://datos.energia.gob.ar/dataset/2b4dfee6-6fca-4e4d-9611-a12d65cd4aa8/resource/b05fbb16-7278-463f-8895-087e2495bfee/download/potencia-instalada.csv
3. Centrales y Proyectos RenovAr / MATER:
   http://datos.energia.gob.ar/dataset/7c30754f-7ee7-45c4-bbb8-fb853b20fe3a/resource/dc334eb4-3450-45c6-a340-37494c78e090/download/centrales-y-proyectos-de-centrales-de-energa-renovable.csv

Variables procesadas:
- sadi_potencia_instalada_mw : Potencia total en MW conectada al SADI por provincia (D6: todas las centrales del SADI)
- sadi_pct_renovable         : % de potencia renovable (Ley 27.191: solar, eólica, biomasa, biogás, mini-hidro <= 50 MW)

Variables no automatizables programáticamente (NaN explícito documentado):
- sadi_uptime_index          : NaN (ENRE solo cubre AMBA; pendiente fuente nacional uniforme CAMMESA/regional)
- sadi_margen_disponible_mw  : NaN (requiere informe anual CAMMESA PDF / descarga manual)
- proyeccion_potencia_2028_mw: NaN (requiere Plan Federal de Transmisión MINEM PDF)
- proyeccion_potencia_2036_mw: NaN (requiere Hoja de Ruta MINEM PDF)
- potencial_offgrid_score    : NaN (reservado para Fase 3 / GIS)

Salidas:
  data/01_raw/cammesa_centrales_generacion_sadi_raw.csv
  data/01_raw/cammesa_potencia_instalada_raw.csv
  data/01_raw/minem_renovar_mater_raw.csv
  data/02_interim/dim_energia_sadi.csv
"""

import argparse
import sys
import unicodedata
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# 0. Rutas del repositorio
# ─────────────────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[2]

ANCLA_CSV        = _REPO_ROOT / "data" / "02_interim" / "jurisdicciones_base.csv"
RAW_CENTRALES    = _REPO_ROOT / "data" / "01_raw" / "cammesa_centrales_generacion_sadi_raw.csv"
RAW_POTENCIA     = _REPO_ROOT / "data" / "01_raw" / "cammesa_potencia_instalada_raw.csv"
RAW_RENOVAR      = _REPO_ROOT / "data" / "01_raw" / "minem_renovar_mater_raw.csv"
OUT_ENERGIA_CSV  = _REPO_ROOT / "data" / "02_interim" / "dim_energia_sadi.csv"

# URLs de descarga oficial
URL_CENTRALES_SADI = (
    "http://datos.energia.gob.ar/dataset/c62df6c6-73af-4039-b956-db081ff6eebe/"
    "resource/230fdf38-8f12-4017-a1e8-d7a1bc4a1c1c/download/"
    "generacin-elctrica-centrales-de-generacin.csv"
)

URL_POTENCIA_CAMMESA = (
    "http://datos.energia.gob.ar/dataset/2b4dfee6-6fca-4e4d-9611-a12d65cd4aa8/"
    "resource/b05fbb16-7278-463f-8895-087e2495bfee/download/"
    "potencia-instalada.csv"
)

URL_RENOVAR_MATER = (
    "http://datos.energia.gob.ar/dataset/7c30754f-7ee7-45c4-bbb8-fb853b20fe3a/"
    "resource/dc334eb4-3450-45c6-a340-37494c78e090/download/"
    "centrales-y-proyectos-de-centrales-de-energa-renovable.csv"
)

URL_GAS_SESCO = (
    "http://datos.energia.gob.ar/dataset/590d1284-fd6d-4686-afd8-b3da5d90a6e9/"
    "resource/ad1b9472-a370-47e7-8de3-b742495ec7f1/download/"
    "produccin-gas-sesco-tight-y-shale-captulo-iv-por-provincia.csv"
)

RAW_GAS = _REPO_ROOT / "data" / "01_raw" / "secretaria_energia_produccion_gas_provincia_raw.csv"

# Mapeo normalizado a IDs INDEC oficiales
_MAPA_PROVINCIA_A_INDEC = {
    "ciudad autonoma de buenos": "02",
    "ciudad autonoma de buenos aires": "02",
    "caba": "02",
    "buenos aires": "06",
    "catamarca": "10",
    "cordoba": "14",
    "corrientes": "18",
    "chaco": "22",
    "chubut": "26",
    "entre rios": "30",
    "formosa": "34",
    "jujuy": "38",
    "la pampa": "42",
    "la rioja": "46",
    "mendoza": "50",
    "misiones": "54",
    "neuquen": "58",
    "rio negro": "62",
    "salta": "66",
    "san juan": "70",
    "san luis": "74",
    "santa cruz": "78",
    "santa fe": "82",
    "santiago del estero": "86",
    "tucuman": "90",
    "tierra del fuego": "94",
}


def _normalizar_texto(s: str) -> str:
    """Normaliza texto removiendo acentos y pasando a minúsculas."""
    if not isinstance(s, str):
        return ""
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s


def descargar_archivo_raw(url: str, destino: Path, descripcion: str, usar_existente: bool = False) -> Path:
    """Descarga un archivo crudo y lo guarda en data/01_raw/."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if usar_existente and destino.exists() and destino.stat().st_size > 100:
        print(f"[RAW] Reutilizando archivo existente: {destino.name} ({descripcion})")
        return destino

    print(f"[RAW] Descargando {descripcion} desde:\n      {url}")
    try:
        with httpx.Client(follow_redirects=True, timeout=60.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            with open(destino, "wb") as f:
                f.write(resp.content)
        print(f"      ✓ Guardado en {destino} ({destino.stat().st_size / 1024:.1f} KB)")
    except Exception as exc:
        print(f"      ✗ Error descargando {descripcion}: {exc}")
        if not destino.exists():
            raise
    return destino


def procesar_energia_sadi(df_ancla: pd.DataFrame, ruta_centrales: Path, ruta_gas: Path) -> pd.DataFrame:
    """
    Procesa las centrales eléctricas del SADI y la producción de gas natural operativa
    para generar la dimensión integral de energía (v2.1.0).
    """
    print("\n[ETL ENERGÍA] Procesando centrales de generación del SADI...")

    df_cen = pd.read_csv(ruta_centrales, encoding="utf-8", low_memory=False)
    # Limpiar posibles BOM en nombres de columnas
    df_cen.columns = [c.replace("ï»¿", "").strip() for c in df_cen.columns]

    print(f"  Filas totales en dataset de centrales: {len(df_cen):,}")

    # Normalizar provincia
    df_cen["prov_norm"] = df_cen["provincia"].apply(_normalizar_texto)

    # Identificar Yacyretá (represa binacional sobre río Paraná, Ituzaingó, Corrientes)
    # En el raw provincial de CAMMESA figura con provincia NaN. Se asigna formalmente a Corrientes (18).
    es_yacyreta = df_cen["nombre"].astype(str).str.contains("YACYRETA", case=False, na=False)
    df_cen.loc[es_yacyreta, "jurisdiccion_id"] = "18"

    # Mapear el resto de centrales a jurisdiccion_id INDEC
    mask_no_yacy = ~es_yacyreta
    df_cen.loc[mask_no_yacy, "jurisdiccion_id"] = df_cen.loc[mask_no_yacy, "prov_norm"].map(_MAPA_PROVINCIA_A_INDEC)

    # Convertir potencia instalada a numérico
    df_cen["potencia_instalada_mw"] = pd.to_numeric(df_cen["potencia_instalada_mw"], errors="coerce").fillna(0.0)

    # Clasificación tecnológica operativa:
    # 1. Potencia Firme Despachable (Nuclear + Hidroeléctrica + Ciclo Combinado + Bioenergía)
    def es_potencia_firme(row) -> bool:
        tec = str(row["tecnologia"]).strip().upper()
        et_norm = _normalizar_texto(str(row["tecnologia_etiqueta"]))
        # Ciclos combinados (CC, CC,TG)
        if tec in ["CC", "CC,TG"] or "ciclo combinado" in et_norm:
            return True
        # Hidroeléctricas (grandes y mini-hidro)
        if tec in ["HI", "HI>50", "HI<50"] or "hidroelectrica" in et_norm:
            return True
        # Nuclear
        if tec == "NUC" or "nuclear" in et_norm:
            return True
        # Bioenergía (Biomasa + Biogás)
        if tec in ["BIOM", "BIOG"] or "biomasa" in et_norm or "biogas" in et_norm:
            return True
        return False

    # 2. Matriz Libre de Carbono (Hidroeléctrica TOTAL + Eólica + Solar + Bioenergía + Nuclear)
    # Estándar ESG Data Centers: cero emisiones directas de GEI en generación 24/7
    def es_libre_carbono(row) -> bool:
        tec = str(row["tecnologia"]).strip().upper()
        et_norm = _normalizar_texto(str(row["tecnologia_etiqueta"]))
        if tec in ["HI", "HI>50", "HI<50"] or "hidroelectrica" in et_norm:
            return True
        if tec in ["EOL", "SOL", "BIOM", "BIOG"] or any(t in et_norm for t in ["eolica", "fotovoltaica", "solar", "biomasa", "biogas"]):
            return True
        if tec == "NUC" or "nuclear" in et_norm:
            return True
        return False

    # 3. Renovables según Ley 27.191 (solar, eólica, biomasa, biogás, mini-hidro <= 50 MW)
    def es_renovable_ley_27191(row) -> bool:
        tec = str(row["tecnologia"]).strip().upper()
        et_norm = _normalizar_texto(str(row["tecnologia_etiqueta"]))
        if tec in ["EOL", "SOL", "BIOM", "BIOG"] or any(t in et_norm for t in ["fotovoltaica", "solar", "eolica", "biogas", "biomasa"]):
            return True
        if tec == "HI<50" or "menor a 50 mw" in et_norm or "<=50" in et_norm or "<50" in et_norm:
            return True
        return False

    df_cen["es_firme"] = df_cen.apply(es_potencia_firme, axis=1)
    df_cen["es_limpia"] = df_cen.apply(es_libre_carbono, axis=1)
    df_cen["es_renovable_ley"] = df_cen.apply(es_renovable_ley_27191, axis=1)

    # Filtrar centrales con provincia identificada (las 474 centrales del dataset)
    df_con_prov = df_cen.dropna(subset=["jurisdiccion_id"]).copy()

    # Agregación eléctrica por jurisdicción
    agrup_elec = df_con_prov.groupby("jurisdiccion_id").apply(
        lambda g: pd.Series({
            "sadi_potencia_instalada_mw": round(g["potencia_instalada_mw"].sum(), 2),
            "sadi_potencia_firme_mw": round(g.loc[g["es_firme"], "potencia_instalada_mw"].sum(), 2),
            "sadi_mw_renovable": round(g.loc[g["es_renovable_ley"], "potencia_instalada_mw"].sum(), 2),
            "sadi_mw_limpia": round(g.loc[g["es_limpia"], "potencia_instalada_mw"].sum(), 2),
            "n_centrales_sadi": len(g),
            "sadi_diversidad_tech": int(g["tecnologia"].nunique()),
        }),
        include_groups=False,
    ).reset_index()

    agrup_elec["sadi_pct_renovable"] = np.where(
        agrup_elec["sadi_potencia_instalada_mw"] > 0,
        (agrup_elec["sadi_mw_renovable"] / agrup_elec["sadi_potencia_instalada_mw"] * 100).round(2),
        0.0,
    )
    agrup_elec["sadi_pct_limpia"] = np.where(
        agrup_elec["sadi_potencia_instalada_mw"] > 0,
        (agrup_elec["sadi_mw_limpia"] / agrup_elec["sadi_potencia_instalada_mw"] * 100).round(2),
        0.0,
    )

    # -------------------------------------------------------------------------
    # Ingesta y Agregación de Producción Operativa de Gas Natural (Año 2025)
    # Fuente oficial: Secretaría de Energía / SESCO Capítulo IV
    # -------------------------------------------------------------------------
    print("\n[ETL GAS] Procesando extracción operativa de gas natural (2025)...")
    df_gas = pd.read_csv(ruta_gas, encoding="utf-8", low_memory=False)
    df_gas.columns = [c.replace("ï»¿", "").strip() for c in df_gas.columns]

    # Filtrar año calendario completo 2025 (12 meses continuos)
    df_gas_2025 = df_gas[df_gas["anio"] == 2025].copy()

    # Exclusión explícita de registros extraterritoriales ("Estado Nacional" / offshore federal)
    # Documentado formalmente en docs/auditoria_energia_v2_1.md
    df_gas_prov = df_gas_2025[df_gas_2025["provincia"].astype(str).str.strip() != "Estado Nacional"].copy()

    df_gas_prov["prov_norm"] = df_gas_prov["provincia"].apply(_normalizar_texto)
    df_gas_prov["jurisdiccion_id"] = df_gas_prov["prov_norm"].map(_MAPA_PROVINCIA_A_INDEC)

    agrup_gas = df_gas_prov.groupby("jurisdiccion_id")["cantidad_mm3"].sum().round(2).reset_index()
    agrup_gas.rename(columns={"cantidad_mm3": "produccion_gas_operativa_mm3"}, inplace=True)

    # -------------------------------------------------------------------------
    # Unir ambas fuentes con la tabla ancla de las 24 jurisdicciones
    # -------------------------------------------------------------------------
    df_res = df_ancla[["jurisdiccion_id", "jurisdiccion_nombre"]].merge(
        agrup_elec,
        on="jurisdiccion_id",
        how="left",
    ).merge(
        agrup_gas,
        on="jurisdiccion_id",
        how="left",
    )

    # Rellenar provincias sin centrales ni producción de gas
    df_res["produccion_gas_operativa_mm3"] = df_res["produccion_gas_operativa_mm3"].fillna(0.0)
    df_res["sadi_potencia_instalada_mw"] = df_res["sadi_potencia_instalada_mw"].fillna(0.0)
    df_res["sadi_potencia_firme_mw"] = df_res["sadi_potencia_firme_mw"].fillna(0.0)
    df_res["sadi_mw_renovable"] = df_res["sadi_mw_renovable"].fillna(0.0)
    df_res["sadi_pct_renovable"] = df_res["sadi_pct_renovable"].fillna(0.0)
    df_res["sadi_mw_limpia"] = df_res["sadi_mw_limpia"].fillna(0.0)
    df_res["sadi_pct_limpia"] = df_res["sadi_pct_limpia"].fillna(0.0)
    df_res["n_centrales_sadi"] = df_res["n_centrales_sadi"].fillna(0).astype(int)
    df_res["sadi_diversidad_tech"] = df_res["sadi_diversidad_tech"].fillna(0).astype(int)

    # Tratamiento explícito de Tierra del Fuego (jurisdiccion_id == "94"):
    # Tierra del Fuego no está conectada físicamente al SADI (sistema provincial aislado).
    # Su potencia SADI conectada es 0.0 MW, pero conserva su producción de gas natural real de cuenca.
    mask_tdf = df_res["jurisdiccion_id"] == "94"
    df_res.loc[mask_tdf, "sadi_potencia_instalada_mw"] = 0.0
    df_res.loc[mask_tdf, "sadi_potencia_firme_mw"] = 0.0
    df_res.loc[mask_tdf, "sadi_mw_renovable"] = 0.0
    df_res.loc[mask_tdf, "sadi_pct_renovable"] = 0.0
    df_res.loc[mask_tdf, "sadi_mw_limpia"] = 0.0
    df_res.loc[mask_tdf, "sadi_pct_limpia"] = 0.0
    df_res.loc[mask_tdf, "n_centrales_sadi"] = 0
    df_res.loc[mask_tdf, "sadi_diversidad_tech"] = 0

    # Columnas con NaN explícito según contrato de datos
    df_res["sadi_uptime_index"]           = np.nan  # ENRE cubre AMBA; pendiente fuente nacional uniforme
    df_res["sadi_margen_disponible_mw"]   = np.nan  # Requiere Informe Anual CAMMESA PDF (descarga manual)
    df_res["proyeccion_potencia_2028_mw"] = np.nan  # Requiere Plan Federal de Transmisión MINEM
    df_res["proyeccion_potencia_2036_mw"] = np.nan  # Requiere Hoja de Ruta Energética MINEM
    df_res["potencial_offgrid_score"]     = np.nan  # Reservado Fase 3 (INENCO / CONICET)

    df_res["fuente_energia"]              = "Secretaría de Energía / CAMMESA SADI + SESCO Gas 2025"
    df_res["fecha_corte_energia"]         = "2025-12-31"

    cols_finales = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "sadi_potencia_instalada_mw",
        "sadi_potencia_firme_mw",
        "sadi_mw_renovable",
        "sadi_pct_renovable",
        "sadi_mw_limpia",
        "sadi_pct_limpia",
        "produccion_gas_operativa_mm3",
        "sadi_uptime_index",
        "sadi_margen_disponible_mw",
        "proyeccion_potencia_2028_mw",
        "proyeccion_potencia_2036_mw",
        "potencial_offgrid_score",
        "n_centrales_sadi",
        "sadi_diversidad_tech",
        "fuente_energia",
        "fecha_corte_energia",
    ]

    df_res = df_res[cols_finales].sort_values("jurisdiccion_id").reset_index(drop=True)
    return df_res


def exportar_dim_energia(df: pd.DataFrame) -> None:
    """Exporta la tabla procesada a data/02_interim/dim_energia_sadi.csv."""
    OUT_ENERGIA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_ENERGIA_CSV, index=False, encoding="utf-8-sig")
    print(f"\n[OK] Dimensión Energía exportada → {OUT_ENERGIA_CSV}")
    print(f"     {len(df)} filas × {len(df.columns)} columnas")

    print("\n[QA] Resumen de variables energéticas v2.1.0:")
    print(df[["jurisdiccion_id", "jurisdiccion_nombre", "sadi_potencia_instalada_mw", "sadi_potencia_firme_mw", "sadi_pct_limpia", "produccion_gas_operativa_mm3"]].to_string())


def main():
    parser = argparse.ArgumentParser(description="ETL Energía SADI & Gas Operativo — v2.1.0")
    parser.add_argument("--usar-raw-existente", action="store_true", help="Reutiliza archivos crudos en data/01_raw/ si existen")
    args = parser.parse_args()

    print("=" * 65)
    print("  ETL Energía SADI & Gas Operativo — v2.1.0")
    print("  Viabilidad IA Data Centers AR")
    print("=" * 65)

    # 1. Cargar ancla
    if not ANCLA_CSV.exists():
        sys.exit(f"[ERROR] No existe la tabla ancla: {ANCLA_CSV}")
    df_ancla = pd.read_csv(ANCLA_CSV, dtype={"jurisdiccion_id": str})

    # 2. Descargar archivos crudos a data/01_raw/
    p_cen = descargar_archivo_raw(
        URL_CENTRALES_SADI,
        RAW_CENTRALES,
        "Centrales de Generación Eléctrica SADI",
        usar_existente=args.usar_raw_existente,
    )
    descargar_archivo_raw(
        URL_POTENCIA_CAMMESA,
        RAW_POTENCIA,
        "Potencia Instalada Histórica CAMMESA",
        usar_existente=args.usar_raw_existente,
    )
    descargar_archivo_raw(
        URL_RENOVAR_MATER,
        RAW_RENOVAR,
        "Proyectos RenovAr / MATER",
        usar_existente=args.usar_raw_existente,
    )
    p_gas = descargar_archivo_raw(
        URL_GAS_SESCO,
        RAW_GAS,
        "Producción de Gas por Provincia (SESCO Capítulo IV)",
        usar_existente=args.usar_raw_existente,
    )

    # 3. Procesar y generar tabla
    df_energia = procesar_energia_sadi(df_ancla, p_cen, p_gas)

    # 4. Exportar
    exportar_dim_energia(df_energia)

    print("\n" + "=" * 65)
    print("  ✅ Módulo 2 (Energía SADI & Gas v2.1.0) completado.")
    print("=" * 65)


if __name__ == "__main__":
    main()
