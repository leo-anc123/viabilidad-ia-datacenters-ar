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


def procesar_energia_sadi(df_ancla: pd.DataFrame, ruta_centrales: Path) -> pd.DataFrame:
    """
    Procesa las centrales eléctricas del SADI y genera la dimensión de energía.
    """
    print("\n[ETL ENERGÍA] Procesando centrales de generación del SADI...")

    df_cen = pd.read_csv(ruta_centrales, encoding="utf-8", low_memory=False)
    # Limpiar posibles BOM en nombres de columnas
    df_cen.columns = [c.replace("ï»¿", "").strip() for c in df_cen.columns]

    print(f"  Filas totales en dataset: {len(df_cen):,}")

    # Normalizar provincia
    df_cen["prov_norm"] = df_cen["provincia"].apply(_normalizar_texto)
    df_cen["jurisdiccion_id"] = df_cen["prov_norm"].map(_MAPA_PROVINCIA_A_INDEC)

    # Identificar energías renovables según Ley 27.191:
    # Solar Fotovoltaica, Eólica, Biomasa, Biogás, Hidroeléctrica <= 50 MW (mini-hidro)
    def es_renovable_ley_27191(etiqueta: str) -> bool:
        et_norm = _normalizar_texto(etiqueta)
        if any(term in et_norm for term in ["fotovoltaica", "solar", "eolica", "biogas", "biomasa"]):
            return True
        if "menor a 50 mw" in et_norm or "<=50" in et_norm or "<50" in et_norm:
            return True
        return False

    df_cen["es_renovable"] = df_cen["tecnologia_etiqueta"].apply(es_renovable_ley_27191)

    # Filtrar centrales con provincia identificada
    # (Nota: Yacyretá tiene provincia NaN por ser binacional AR-PY sobre río Paraná; su energía es asignada a nivel despacho)
    df_con_prov = df_cen.dropna(subset=["jurisdiccion_id"]).copy()
    df_con_prov["potencia_instalada_mw"] = pd.to_numeric(df_con_prov["potencia_instalada_mw"], errors="coerce").fillna(0.0)

    # Agregación por jurisdicción
    agrup = df_con_prov.groupby("jurisdiccion_id").apply(
        lambda g: pd.Series({
            "sadi_potencia_instalada_mw": round(g["potencia_instalada_mw"].sum(), 2),
            "sadi_mw_renovable": round(g.loc[g["es_renovable"], "potencia_instalada_mw"].sum(), 2),
            "n_centrales_sadi": len(g),
            "sadi_diversidad_tech": int(g["tecnologia"].nunique()),
        }),
        include_groups=False,
    ).reset_index()

    agrup["sadi_pct_renovable"] = np.where(
        agrup["sadi_potencia_instalada_mw"] > 0,
        (agrup["sadi_mw_renovable"] / agrup["sadi_potencia_instalada_mw"] * 100).round(2),
        0.0,
    )

    # Unir con la tabla ancla de las 24 jurisdicciones
    df_res = df_ancla[["jurisdiccion_id", "jurisdiccion_nombre"]].merge(
        agrup,
        on="jurisdiccion_id",
        how="left",
    )

    # Tratamiento explícito de Tierra del Fuego (jurisdiccion_id == "94"):
    # Tierra del Fuego no está conectada físicamente al SADI (sistema provincial aislado).
    # Su potencia SADI conectada es 0.0 MW y 0 tecnologías SADI.
    mask_tdf = df_res["jurisdiccion_id"] == "94"
    df_res.loc[mask_tdf, "sadi_potencia_instalada_mw"] = 0.0
    df_res.loc[mask_tdf, "sadi_mw_renovable"] = 0.0
    df_res.loc[mask_tdf, "sadi_pct_renovable"] = 0.0
    df_res.loc[mask_tdf, "n_centrales_sadi"] = 0
    df_res.loc[mask_tdf, "sadi_diversidad_tech"] = 0

    df_res["sadi_diversidad_tech"] = df_res["sadi_diversidad_tech"].fillna(0).astype(int)

    # Columnas con NaN explícito según contrato de datos
    df_res["sadi_uptime_index"]           = np.nan  # ENRE cubre AMBA; pendiente fuente nacional uniforme
    df_res["sadi_margen_disponible_mw"]   = np.nan  # Requiere Informe Anual CAMMESA PDF (descarga manual)
    df_res["proyeccion_potencia_2028_mw"] = np.nan  # Requiere Plan Federal de Transmisión MINEM
    df_res["proyeccion_potencia_2036_mw"] = np.nan  # Requiere Hoja de Ruta Energética MINEM
    df_res["potencial_offgrid_score"]     = np.nan  # Reservado Fase 3 (INENCO / CONICET)

    df_res["fuente_energia"]              = "Secretaría de Energía / CAMMESA — Centrales de Generación SADI"
    df_res["fecha_corte_energia"]         = "2024-01-01"

    cols_finales = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "sadi_potencia_instalada_mw",
        "sadi_pct_renovable",
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

    print("\n[QA] Resumen de variables energéticas:")
    print(df[["jurisdiccion_id", "jurisdiccion_nombre", "sadi_potencia_instalada_mw", "sadi_pct_renovable"]].to_string())


def main():
    parser = argparse.ArgumentParser(description="ETL Energía SADI — Bloque 2.2")
    parser.add_argument("--usar-raw-existente", action="store_true", help="Reutiliza archivos crudos en data/01_raw/ si existen")
    args = parser.parse_args()

    print("=" * 65)
    print("  ETL Energía SADI — Bloque 2.2")
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

    # 3. Procesar y generar tabla
    df_energia = procesar_energia_sadi(df_ancla, p_cen)

    # 4. Exportar
    exportar_dim_energia(df_energia)

    print("\n" + "=" * 65)
    print("  ✅ Módulo 2 (Energía SADI) completado.")
    print("=" * 65)


if __name__ == "__main__":
    main()
