"""
fetch_talento_riesgo.py
=======================
Módulo ETL para la dimensión Capital Humano y Riesgo Territorial del proyecto
"Viabilidad de Data Centers y Campus de IA en Argentina".

Ingesta y procesa:
1. Empleo Registrado en Software y Sector TIC (CEP XXI - Ministerio de Economía):
   - Puestos registrados en software (CLAE 62: programación y consultoría informática)
   - Puestos registrados en sector TIC integral (CLAE 61-63: telecomunicaciones, software, info)
   - Total de puestos de trabajo privados registrados por provincia
   - Tasa relativa pct_empleo_tic_privado (% sobre total empleo formal privado)
   - Densidad de talento IT escalada (densidad_stem_it_score, CABA = 10.0)
2. Riesgo Sísmico Oficial (INPRES - Reglamento INPRES-CIRSOC 103):
   - Consulta automatizada al servicio oficial de zonificación sísmica del INPRES
     (zonas_result.php) para cada capital provincial según coordenadas WGS84.
   - Pausa prudencial entre llamadas y reintentos automáticos para evitar bloqueos.
   - Almacenamiento del payload crudo completo en JSON para trazabilidad y auditoría.
   - Extracción de la zona sísmica oficial (riesgo_sismico_zona, escala 0 a 4).
3. Variables pendientes documentadas en NaN:
   - graduados_stem_anual (SPU: no existe desagregación provincial abierta)
   - riesgo_climatico_score y riesgo_combinado_score (reservados a Bloque 5.x)

Salidas:
- `data/01_raw/cepxxi_puestos_trabajo_clae2_provincias_raw.csv`
- `data/01_raw/inpres_zonificacion_24_raw.json`
- `data/02_interim/dim_talento_riesgo.csv`
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

# Rutas del repositorio
REPO_ROOT = Path(__file__).resolve().parents[2]
PATH_ANCLA = REPO_ROOT / "data" / "02_interim" / "jurisdicciones_base.csv"
DIR_RAW = REPO_ROOT / "data" / "01_raw"
DIR_INTERIM = REPO_ROOT / "data" / "02_interim"
PATH_SALIDA = DIR_INTERIM / "dim_talento_riesgo.csv"

# URLs oficiales
URL_CEP_XXI_PUESTOS = (
    "https://cdn.produccion.gob.ar/cdn-cep/datos-por-provincia/"
    "por-provincia-clae2/puestos/puestos_priv.csv"
)
URL_INPRES_ZONAS = "https://www.inpres.gob.ar/zonas_result.php"

# Mapeo exhaustivo de nombres provinciales de CEP XXI a jurisdiccion_id oficial
MAPA_PROVINCIAS_CEP: Dict[str, str] = {
    "CAPITAL FEDERAL": "02",
    "BUENOS AIRES": "06",
    "CATAMARCA": "10",
    "CORDOBA": "14",
    "CORRIENTES": "18",
    "CHACO": "22",
    "CHUBUT": "26",
    "ENTRE RIOS": "30",
    "FORMOSA": "34",
    "JUJUY": "38",
    "LA PAMPA": "42",
    "LA RIOJA": "46",
    "MENDOZA": "50",
    "MISIONES": "54",
    "NEUQUEN": "58",
    "RIO NEGRO": "62",
    "SALTA": "66",
    "SAN JUAN": "70",
    "SAN LUIS": "74",
    "SANTA CRUZ": "78",
    "SANTA FE": "82",
    "SANTIAGO DEL ESTERO": "86",
    "TUCUMAN": "90",
    "TIERRA DEL FUEGO": "94",
}


def descargar_crudo_cepxxi() -> Path:
    """Descarga el panel mensual completo de puestos privados de CEP XXI con fallback a snapshot."""
    DIR_RAW.mkdir(parents=True, exist_ok=True)
    destino = DIR_RAW / "cepxxi_puestos_trabajo_clae2_provincias_raw.csv"

    print(f"[TALENTO] Descargando panel CEP XXI desde {URL_CEP_XXI_PUESTOS}...")
    try:
        req = urllib.request.Request(
            URL_CEP_XXI_PUESTOS,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()

        with open(destino, "wb") as f:
            f.write(content)

        print(f"  -> Guardado crudo CEP XXI: {destino} ({len(content):,} bytes)")
        return destino
    except Exception as exc:
        if destino.exists() and destino.stat().st_size > 0:
            print(f"  [CACHED_FALLBACK] Error al descargar CEP XXI: {exc}. Utilizando snapshot previo en {destino}")
            return destino
        raise RuntimeError(f"Fallo al descargar CEP XXI y no existe snapshot local: {exc}") from exc


def procesar_empleo_cepxxi(path_csv: Path) -> Tuple[pd.DataFrame, str]:
    """
    Procesa el archivo crudo de puestos de trabajo del CEP XXI:
    Filtra al período más reciente, calcula empleo en CLAE 62 (Software),
    CLAE 61-63 (TIC), total provincial, y la tasa relativa pct_empleo_tic_privado.
    """
    print("[TALENTO] Procesando panel de puestos registrados del CEP XXI...")
    df = pd.read_csv(path_csv)
    max_fecha = str(df["fecha"].max())
    print(f"[TALENTO] Período más reciente de empleo formal privado: {max_fecha}")

    df_latest = df[df["fecha"] == max_fecha].copy()
    df_latest["jurisdiccion_id"] = df_latest["zona_prov"].map(MAPA_PROVINCIAS_CEP)

    if df_latest["jurisdiccion_id"].isnull().any():
        nulos = df_latest[df_latest["jurisdiccion_id"].isnull()]["zona_prov"].unique()
        raise ValueError(f"Provincias de CEP XXI no mapeadas: {nulos}")

    # Totales por jurisdicción
    totales = (
        df_latest.groupby("jurisdiccion_id")["puestos"]
        .sum()
        .rename("puestos_privados_totales")
        .astype(int)
    )

    # CLAE 62: Servicios de programación y consultoría informática
    soft_62 = (
        df_latest[df_latest["clae2"] == 62]
        .groupby("jurisdiccion_id")["puestos"]
        .sum()
        .rename("puestos_software_clae62")
        .astype(int)
    )

    # CLAE 61, 62, 63: Sector TIC y Servicios de Información Integral
    tic_61_63 = (
        df_latest[df_latest["clae2"].isin([61, 62, 63])]
        .groupby("jurisdiccion_id")["puestos"]
        .sum()
        .rename("puestos_tic_clae61_63")
        .astype(int)
    )

    df_res = pd.concat([totales, soft_62, tic_61_63], axis=1).fillna(0)
    df_res["puestos_software_clae62"] = df_res["puestos_software_clae62"].astype(int)
    df_res["puestos_tic_clae61_63"] = df_res["puestos_tic_clae61_63"].astype(int)

    # Tasa relativa de empleo TIC sobre total empleo formal privado de la provincia
    df_res["pct_empleo_tic_privado"] = (
        (df_res["puestos_tic_clae61_63"] / df_res["puestos_privados_totales"]) * 100.0
    ).round(2)

    # Score normalizado 0 a 10 relativo al máximo provincial (CABA = 10.0)
    max_pct = df_res["pct_empleo_tic_privado"].max()
    df_res["densidad_stem_it_score"] = (
        (df_res["pct_empleo_tic_privado"] / max_pct) * 10.0
    ).round(2)

    return df_res.reset_index(), max_fecha


def consultar_inpres_zona(lat: float, lon: float, max_intentos: int = 4) -> Tuple[int, str]:
    """
    Consulta al servicio oficial del INPRES (zonas_result.php) por lat/lon
    y extrae la zona sísmica oficial (0 a 4).
    Implementa reintentos exponenciales y pausa prudencial.
    """
    # INPRES espera coordenadas en valor absoluto (latitud sur, longitud oeste)
    lat_pos = abs(lat)
    lon_pos = abs(lon)
    payload = urllib.parse.urlencode({"latitud": f"{lat_pos:.4f}", "longitud": f"{lon_pos:.4f}"}).encode("utf-8")

    req = urllib.request.Request(
        URL_INPRES_ZONAS,
        data=payload,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    for intento in range(1, max_intentos + 1):
        try:
            with urllib.request.urlopen(req, timeout=18) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # Buscar patrón de zona sísmica en la respuesta
            match = re.search(r'Zona\s+[sS]ísmica\s+["\']?([0-4])["\']?', html)
            if match:
                zona = int(match.group(1))
                return zona, html
            else:
                # Búsqueda alternativa por texto simple
                if 'zona sísmica "0"' in html.lower() or "zona sismica 0" in html.lower():
                    return 0, html
                raise ValueError(f"No se pudo parsear zona sísmica del HTML retornado (longitud {len(html)})")

        except Exception as exc:
            if intento == max_intentos:
                raise RuntimeError(
                    f"Fallo definitivo al consultar INPRES tras {max_intentos} intentos ({lat}, {lon}): {exc}"
                )
            espera = 2.0 * intento
            print(f"    [AVISO] Reintento {intento}/{max_intentos} tras error: {exc}. Esperando {espera:.1f}s...")
            time.sleep(espera)

    raise RuntimeError("Estado inalcanzable en consulta_inpres_zona")


def procesar_riesgo_inpres(df_base: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Itera sobre las 24 capitales consultando INPRES con pausas de cortesía,
    guardando el crudo consolidado en data/01_raw/inpres_zonificacion_24_raw.json.
    """
    DIR_RAW.mkdir(parents=True, exist_ok=True)
    path_raw_inpres = DIR_RAW / "inpres_zonificacion_24_raw.json"

    print("[RIESGO] Consultando servicio oficial INPRES (zonas_result.php) para las 24 capitales...")
    resultados = []
    payloads_raw: Dict[str, Any] = {}

    # Intentar cargar caché local para fallback seguro
    cached_payloads = None
    if path_raw_inpres.exists() and path_raw_inpres.stat().st_size > 0:
        try:
            with open(path_raw_inpres, "r", encoding="utf-8") as f:
                cached_payloads = json.load(f)
        except Exception:
            cached_payloads = None

    try:
        for idx, row in df_base.iterrows():
            jid = str(row["jurisdiccion_id"]).zfill(2)
            nombre = str(row["jurisdiccion_nombre"])
            lat = float(row["lat_capital"])
            lon = float(row["lon_capital"])

            print(f"  [{idx+1:02d}/24] {nombre:<32} ({lat:.4f}, {lon:.4f})...", end=" ", flush=True)
            zona, html_raw = consultar_inpres_zona(lat, lon)
            print(f"-> Zona Sísmica {zona}")

            resultados.append({
                "jurisdiccion_id": jid,
                "riesgo_sismico_zona": zona,
            })
            payloads_raw[jid] = {
                "jurisdiccion_nombre": nombre,
                "lat_capital": lat,
                "lon_capital": lon,
                "zona_detectada": zona,
                "html_response": html_raw,
            }

            # Pausa de cortesía para no saturar el servidor del INPRES
            time.sleep(0.8)

        # Persistir crudo completo
        with open(path_raw_inpres, "w", encoding="utf-8") as f:
            json.dump(payloads_raw, f, ensure_ascii=False, indent=2)
        print(f"  -> Guardado crudo INPRES: {path_raw_inpres} ({path_raw_inpres.stat().st_size:,} bytes)")
        return pd.DataFrame(resultados), payloads_raw

    except Exception as exc:
        if cached_payloads and len(cached_payloads) == 24:
            print(f"\n  [CACHED_FALLBACK] Error al consultar INPRES: {exc}. Utilizando snapshot previo en {path_raw_inpres}")
            fallback_res = []
            for jid, item in cached_payloads.items():
                fallback_res.append({
                    "jurisdiccion_id": jid,
                    "riesgo_sismico_zona": item["zona_detectada"],
                })
            return pd.DataFrame(fallback_res), cached_payloads
        raise RuntimeError(f"Fallo al consultar INPRES y no existe snapshot completo: {exc}") from exc


def procesar_talento_riesgo() -> pd.DataFrame:
    """Orquestador principal de la dimensión Talento y Riesgo."""
    if not PATH_ANCLA.exists():
        raise FileNotFoundError(f"No se encontró la tabla ancla: {PATH_ANCLA}")

    df_base = pd.read_csv(PATH_ANCLA, dtype={"jurisdiccion_id": str})
    print(f"[TALENTO/RIESGO] Ancla territorial cargada: {len(df_base)} jurisdicciones.")

    # 1. Ingesta y cálculo de empleo CEP XXI
    path_raw_cep = descargar_crudo_cepxxi()
    df_talento, fecha_corte_cep = procesar_empleo_cepxxi(path_raw_cep)

    # 2. Ingesta oficial INPRES por capital provincial
    df_riesgo, _ = procesar_riesgo_inpres(df_base)

    # 3. Consolidación
    df_merged = df_base[["jurisdiccion_id", "jurisdiccion_nombre"]].merge(
        df_talento, on="jurisdiccion_id", how="left"
    )
    df_merged = df_merged.merge(df_riesgo, on="jurisdiccion_id", how="left")

    # 4. Columnas en NaN explícito conforme a diccionario y reglas de calidad
    df_merged["graduados_stem_anual"] = np.nan        # SPU: pendiente desagregación provincial
    df_merged["riesgo_climatico_score"] = np.nan       # Pendiente Bloque 5.x
    df_merged["riesgo_combinado_score"] = np.nan       # Pendiente Bloque 5.x

    # 5. Metadatos de trazabilidad
    df_merged["fuente_talento"] = "CEP XXI — Puestos Registrados CLAE2"
    df_merged["fecha_corte_talento"] = fecha_corte_cep
    df_merged["fuente_riesgo_sismico"] = "INPRES — CIRSOC 103"
    df_merged["fecha_corte_riesgo_sismico"] = "2024-01-01"

    # Selección y orden de columnas
    cols_salida = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "puestos_privados_totales",
        "puestos_software_clae62",
        "puestos_tic_clae61_63",
        "pct_empleo_tic_privado",
        "densidad_stem_it_score",
        "graduados_stem_anual",
        "riesgo_sismico_zona",
        "riesgo_climatico_score",
        "riesgo_combinado_score",
        "fuente_talento",
        "fecha_corte_talento",
        "fuente_riesgo_sismico",
        "fecha_corte_riesgo_sismico",
    ]
    df_salida = df_merged[cols_salida].copy()

    # Formato de salida UTF-8-BOM
    DIR_INTERIM.mkdir(parents=True, exist_ok=True)
    df_salida.to_csv(PATH_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\n[TALENTO/RIESGO] ✅ Archivo generado exitosamente: {PATH_SALIDA}")
    print(f"[TALENTO/RIESGO] Dimensiones: {df_salida.shape[0]} filas × {df_salida.shape[1]} columnas.")

    return df_salida


if __name__ == "__main__":
    try:
        procesar_talento_riesgo()
    except Exception as exc:
        print(f"[ERROR] Falló la ejecución de fetch_talento_riesgo.py: {exc}", file=sys.stderr)
        sys.exit(1)
