"""
fetch_clima_pue.py
==================
ETL de datos climáticos históricos para las 24 jurisdicciones de Argentina.

Fuente: Open-Meteo Historical Weather API (ERA5 / ERA5-Land, ECMWF)
Endpoint: https://archive-api.open-meteo.com/v1/archive
Sin autenticación. Fair-use: ~10.000 req/día. Uso no comercial.

Período de referencia: 2000-01-01 → 2023-12-31
(24 años; captura tendencia climática reciente para proyecciones 2028–2036.
Aprobado en Bloque 2.2 — decisión D4.)

Variables descargadas (daily):
  - temperature_2m_max   : temperatura máxima diaria a 2 m (°C)
  - temperature_2m_min   : temperatura mínima diaria a 2 m (°C)
  - temperature_2m_mean  : temperatura media diaria a 2 m (°C)

Variables derivadas calculadas en Python:
  - temp_media_anual_c         : promedio aritmético de temp media diaria (°C)
  - temp_max_verano_prom_c     : promedio de temp máx en meses DJF (°C)
  - horas_free_cooling_estimadas: proxy horario con T_exterior < 15 °C
  - pue_climatologico_estimado : PUE interpolado por fracción de free cooling

Fórmulas — aprobadas en Bloque 2.2:
  ─────────────────────────────────────────────────────────────────────────
  UMBRAL_FREE_COOLING_C  = 15.0  °C (dry-bulb, ASHRAE 90.4-2019, decisión D1)
  FACTOR_HORARIO         = 0.70  (proporción de horas frías/día; proxy nocturno)
  PUE_BASE_MECANICO      = 1.58  (benchmark LATAM Uptime Institute 2023, D3)
  PUE_MIN_FREE_COOLING   = 1.10  (PUE mínimo con 100 % free cooling ideal)

  horas_free_cooling = round( dias_con_T_media < 15°C × 24 × 0.70 )
  frac_fc            = horas_free_cooling / 8760
  pue_estimado       = PUE_BASE - frac_fc × (PUE_BASE - PUE_MIN_FC)
  pue_estimado       = max(pue_estimado, 1.10)   # límite técnico inferior
  ─────────────────────────────────────────────────────────────────────────

Estrés hídrico:
  Fuente: WRI Aqueduct 4.0 — indicador bws_score (Baseline Water Stress)
  Descarga CSV desde World Bank Data Catalog (Aqueduct 4.0 Province Rankings).
  Si la descarga falla → NaN explícito para las 24 jurisdicciones.
  Campo: indice_estres_hidrico (escala 0–5, 0=sin estrés, 5=estrés extremo)

Salidas:
  data/01_raw/clima_24_jurisdicciones_raw.json  — respuesta cruda Open-Meteo
  data/02_interim/dim_clima_agua.csv            — tabla limpia con jurisdiccion_id

Uso:
  python src/gis/fetch_clima_pue.py
  python src/gis/fetch_clima_pue.py --dry-run   (valida config sin llamar a la API)
  python src/gis/fetch_clima_pue.py --skip-aqueduct  (omite descarga WRI)
"""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# 0. Rutas y constantes del proyecto
# ─────────────────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[2]

ANCLA_CSV      = _REPO_ROOT / "data" / "02_interim" / "jurisdicciones_base.csv"
RAW_CLIMA_JSON = _REPO_ROOT / "data" / "01_raw" / "clima_24_jurisdicciones_raw.json"
OUT_CLIMA_CSV  = _REPO_ROOT / "data" / "02_interim" / "dim_clima_agua.csv"

# API Open-Meteo
OPEN_METEO_URL  = "https://archive-api.open-meteo.com/v1/archive"
FECHA_INICIO    = "2000-01-01"
FECHA_FIN       = "2023-12-31"
PERIODO_REF     = "2000–2023"
PAUSA_ENTRE_REQ = 2.0   # segundos entre llamadas (fair-use Open-Meteo)
TIMEOUT_SEG     = 60    # timeout por request (segundos)
MAX_REINTENTOS  = 4     # reintentos ante error de red o rate limit

# Variables climáticas solicitadas
VARIABLES_DAILY = "temperature_2m_max,temperature_2m_min,temperature_2m_mean"

# Fórmulas PUE — aprobadas Bloque 2.2 (decisiones D1, D3)
UMBRAL_FREE_COOLING_C = 15.0   # °C dry-bulb (ASHRAE 90.4-2019)
FACTOR_HORARIO        = 0.70   # proporción horas frías concentradas en noche
PUE_BASE_MECANICO     = 1.58   # PUE con 100 % enfriamiento mecánico (LATAM Uptime 2023)
PUE_MIN_FREE_COOLING  = 1.10   # PUE mínimo con 100 % free cooling ideal
HORAS_ANO             = 8760

# WRI Aqueduct 4.0 — Province Rankings CSV (World Bank Data Catalog)
# Dataset: https://datacatalog.worldbank.org/search/dataset/0038173
# Archivo de rankings provinciales: descarga directa del ZIP del WB
AQUEDUCT_CSV_URL = (
    "https://raw.githubusercontent.com/wri/Aqueduct40/master/"
    "routing/aqueduct40_waterrisk_directory_and_aggregation_labels_20230901.csv"
)
# URL alternativa — tabla de rankings por país/provincia (Aqueduct 4.0)
AQUEDUCT_RANKINGS_URL = (
    "https://www.wri.org/data/aqueduct-40-country-rankings"
)

# Meses de verano austral (DJF: diciembre, enero, febrero)
MESES_VERANO = {12, 1, 2}

# ─────────────────────────────────────────────────────────────────────────────
# 1. Carga de la tabla ancla
# ─────────────────────────────────────────────────────────────────────────────

def cargar_ancla() -> pd.DataFrame:
    """Carga jurisdicciones_base.csv y valida columnas mínimas."""
    if not ANCLA_CSV.exists():
        sys.exit(f"[ERROR] No se encuentra la tabla ancla: {ANCLA_CSV}")

    df = pd.read_csv(ANCLA_CSV, dtype={"jurisdiccion_id": str})

    cols_req = {"jurisdiccion_id", "jurisdiccion_nombre", "lat_capital", "lon_capital"}
    faltantes = cols_req - set(df.columns)
    if faltantes:
        sys.exit(f"[ERROR] Columnas faltantes en ancla: {faltantes}")

    if len(df) != 24:
        sys.exit(f"[ERROR] La ancla tiene {len(df)} filas; se esperan exactamente 24.")

    print(f"[OK] Ancla cargada: {len(df)} jurisdicciones.")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. Descarga Open-Meteo (ERA5)
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_una_jurisdiccion(
    client: httpx.Client,
    jid: str,
    nombre: str,
    lat: float,
    lon: float,
    dry_run: bool = False,
) -> dict:
    """
    Realiza la llamada a Open-Meteo para una jurisdicción.
    Retorna el dict JSON con los datos diarios o un dict de error.
    """
    params = {
        "latitude":    round(lat, 4),
        "longitude":   round(lon, 4),
        "start_date":  FECHA_INICIO,
        "end_date":    FECHA_FIN,
        "daily":       VARIABLES_DAILY,
        "timezone":    "America/Argentina/Buenos_Aires",
        "wind_speed_unit": "kmh",
    }

    if dry_run:
        # Simula respuesta vacía para verificar configuración sin llamar a la API
        return {
            "_jid": jid,
            "_nombre": nombre,
            "_dry_run": True,
            "latitude": lat,
            "longitude": lon,
            "daily": {
                "time": [],
                "temperature_2m_max": [],
                "temperature_2m_min": [],
                "temperature_2m_mean": [],
            },
        }

    ultimo_error = None
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            resp = client.get(OPEN_METEO_URL, params=params, timeout=TIMEOUT_SEG)
            if resp.status_code == 429:
                wait_time = 5 * intento
                time.sleep(wait_time)
                continue
            resp.raise_for_status()
            data = resp.json()
            data["_jid"]    = jid
            data["_nombre"] = nombre
            return data
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            ultimo_error = exc
            if intento < MAX_REINTENTOS:
                time.sleep(3 * intento)
    # Si agotó reintentos
    return {
        "_jid":    jid,
        "_nombre": nombre,
        "_error":  str(ultimo_error),
        "daily":   None,
    }


def descargar_clima_open_meteo(df_ancla: pd.DataFrame, dry_run: bool = False) -> dict:
    """
    Descarga datos climáticos diarios para las 24 jurisdicciones vía Open-Meteo.
    Si ya existe un raw parcial, reutiliza las jurisdicciones que ya se descargaron OK
    y solo consulta las faltantes o con error.
    Guarda la respuesta cruda en data/01_raw/clima_24_jurisdicciones_raw.json.

    Returns
    -------
    dict  Mapa jid → datos JSON de Open-Meteo (o error)
    """
    print(f"\n[CLIMA] Descargando ERA5 ({FECHA_INICIO} → {FECHA_FIN}) para 24 jurisdicciones...")
    if dry_run:
        print("[CLIMA] Modo dry-run activado — no se realizarán llamadas reales a la API.")

    resultados: dict = {}
    if RAW_CLIMA_JSON.exists():
        try:
            with open(RAW_CLIMA_JSON, "r", encoding="utf-8") as f:
                prev_raw = json.load(f)
                prev_jurs = prev_raw.get("jurisdicciones", {})
                for k, v in prev_jurs.items():
                    if "_error" not in v and v.get("daily") and v["daily"].get("time"):
                        resultados[k] = v
        except Exception:
            pass

    errores: list[str] = []

    with httpx.Client(follow_redirects=True) as client:
        for _, fila in tqdm(df_ancla.iterrows(), total=len(df_ancla), desc="Open-Meteo ERA5", unit="prov"):
            jid    = fila["jurisdiccion_id"]
            nombre = fila["jurisdiccion_nombre"]
            lat    = float(fila["lat_capital"])
            lon    = float(fila["lon_capital"])

            if jid in resultados:
                n_dias = len(resultados[jid].get("daily", {}).get("time", []))
                tqdm.write(f"  ⚡ {nombre:30s} → Reutilizado de raw ({n_dias:,} días)")
                continue

            datos = _fetch_una_jurisdiccion(client, jid, nombre, lat, lon, dry_run=dry_run)
            resultados[jid] = datos

            if "_error" in datos:
                errores.append(f"{nombre} ({jid}): {datos['_error']}")
            elif not dry_run:
                n_dias = len(datos.get("daily", {}).get("time", []))
                tqdm.write(f"  ✓ {nombre:30s} → {n_dias:,} días descargados")

            if not dry_run:
                time.sleep(PAUSA_ENTRE_REQ)

    # Guardar raw
    RAW_CLIMA_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_CLIMA_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {
                "_metadata": {
                    "fuente":        "Open-Meteo Historical API (ERA5 / ECMWF)",
                    "endpoint":      OPEN_METEO_URL,
                    "variables":     VARIABLES_DAILY,
                    "fecha_inicio":  FECHA_INICIO,
                    "fecha_fin":     FECHA_FIN,
                    "generado_en":   pd.Timestamp.now().isoformat(),
                    "dry_run":       dry_run,
                },
                "jurisdicciones": resultados,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\n[OK] Raw guardado → {RAW_CLIMA_JSON}")

    if errores:
        print(f"\n[ADVERTENCIA] {len(errores)} jurisdicción(es) con error de descarga:")
        for e in errores:
            print(f"  ✗ {e}")
    else:
        print(f"[OK] 0 errores de descarga.")

    return resultados


# ─────────────────────────────────────────────────────────────────────────────
# 3. Cálculo de variables climáticas y PUE
# ─────────────────────────────────────────────────────────────────────────────

def calcular_variables_clima(jid: str, nombre: str, datos_json: dict) -> dict:
    """
    Calcula las variables climáticas derivadas para una jurisdicción a partir
    de la respuesta JSON de Open-Meteo.

    Returns
    -------
    dict con las variables calculadas (NaN si datos insuficientes)
    """
    base = {
        "jurisdiccion_id":              jid,
        "jurisdiccion_nombre":          nombre,
        "temp_media_anual_c":           np.nan,
        "temp_max_verano_prom_c":       np.nan,
        "horas_free_cooling_estimadas": np.nan,
        "pue_climatologico_estimado":   np.nan,
        "n_dias_datos":                 0,
        "fuente_clima":                 "Open-Meteo ERA5 (ECMWF)",
        "periodo_referencia":           PERIODO_REF,
        "umbral_free_cooling_c":        UMBRAL_FREE_COOLING_C,
        "pue_base_mecanico":            PUE_BASE_MECANICO,
        "pue_min_free_cooling":         PUE_MIN_FREE_COOLING,
        "factor_horario_ajuste":        FACTOR_HORARIO,
    }

    if "_error" in datos_json or datos_json.get("daily") is None:
        base["_nota"] = datos_json.get("_error", "Sin datos")
        return base

    daily = datos_json.get("daily", {})
    fechas = daily.get("time", [])
    t_mean = daily.get("temperature_2m_mean", [])
    t_max  = daily.get("temperature_2m_max", [])

    if not fechas or not t_mean:
        return base

    # Construir DataFrame diario
    df_d = pd.DataFrame({
        "fecha":  pd.to_datetime(fechas),
        "t_mean": pd.to_numeric(t_mean, errors="coerce"),
        "t_max":  pd.to_numeric(t_max,  errors="coerce"),
    })
    df_d = df_d.dropna(subset=["t_mean"])

    if df_d.empty:
        return base

    # Variable A: temperatura media anual
    base["temp_media_anual_c"] = round(float(df_d["t_mean"].mean()), 2)
    base["n_dias_datos"]       = len(df_d)

    # Variable B: temperatura máxima promedio de verano (DJF)
    df_verano = df_d[df_d["fecha"].dt.month.isin(MESES_VERANO)]
    if not df_verano.empty:
        base["temp_max_verano_prom_c"] = round(float(df_verano["t_max"].mean()), 2)

    # Variable C: horas de free cooling estimadas (promedio anual)
    # Fórmula: días anuales promedio con T_media < UMBRAL × 24h × FACTOR_HORARIO
    # (aprobada en Bloque 2.2 — decisión D1)
    n_anios = max(1, df_d["fecha"].dt.year.nunique())
    dias_frios_totales = int((df_d["t_mean"] < UMBRAL_FREE_COOLING_C).sum())
    dias_frios_anuales = dias_frios_totales / n_anios
    horas_fc = round(dias_frios_anuales * 24 * FACTOR_HORARIO)
    base["horas_free_cooling_estimadas"] = float(horas_fc)

    # Variable D: PUE climatológico estimado
    # Fórmula: interpolación lineal entre PUE mecánico y PUE free-cooling
    # pue = PUE_BASE - frac_fc × (PUE_BASE - PUE_MIN_FC) ; min = 1.10
    # (aprobada en Bloque 2.2 — decisión D3)
    frac_fc = min(1.0, horas_fc / HORAS_ANO)
    pue_est = PUE_BASE_MECANICO - frac_fc * (PUE_BASE_MECANICO - PUE_MIN_FREE_COOLING)
    pue_est = max(pue_est, PUE_MIN_FREE_COOLING)
    base["pue_climatologico_estimado"] = round(pue_est, 4)

    return base


def calcular_todas_las_jurisdicciones(
    df_ancla: pd.DataFrame,
    resultados_raw: dict,
) -> pd.DataFrame:
    """
    Aplica calcular_variables_clima a las 24 jurisdicciones y devuelve un DataFrame.
    """
    print("\n[CLIMA] Calculando variables derivadas para las 24 jurisdicciones...")

    filas = []
    for _, fila in df_ancla.iterrows():
        jid    = fila["jurisdiccion_id"]
        nombre = fila["jurisdiccion_nombre"]
        datos  = resultados_raw.get(jid, {"_error": "Sin datos en raw"})
        fila_calc = calcular_variables_clima(jid, nombre, datos)
        filas.append(fila_calc)

    df = pd.DataFrame(filas)

    # Resumen rápido
    n_ok   = df["temp_media_anual_c"].notna().sum()
    n_null = df["temp_media_anual_c"].isna().sum()
    print(f"[OK] Variables calculadas: {n_ok}/24 con datos | {n_null}/24 con NaN")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4. Estrés hídrico — WRI Aqueduct 4.0
# ─────────────────────────────────────────────────────────────────────────────

def _normalizar_nombre_provincia(nombre: str) -> str:
    """Normalización básica para fuzzy match entre WRI y nomenclador INDEC."""
    import unicodedata
    nombre = nombre.lower().strip()
    nombre = unicodedata.normalize("NFD", nombre)
    nombre = "".join(c for c in nombre if unicodedata.category(c) != "Mn")
    # Remover artículos y preposiciones comunes
    for repl in [" de ", " del ", " la ", " el ", " los ", " las "]:
        nombre = nombre.replace(repl, " ")
    return nombre.strip()


# Tabla de mapeo manual WRI → INDEC para provincias con nombres divergentes
_MAPA_WRI_A_INDEC = {
    "ciudad de buenos aires": "02",
    "caba":                   "02",
    "buenos aires":           "06",
    "catamarca":              "10",
    "cordoba":                "14",
    "corrientes":             "18",
    "chaco":                  "22",
    "chubut":                 "26",
    "entre rios":             "30",
    "formosa":                "34",
    "jujuy":                  "38",
    "la pampa":               "42",
    "la rioja":               "46",
    "mendoza":                "50",
    "misiones":               "54",
    "neuquen":                "58",
    "rio negro":              "62",
    "salta":                  "66",
    "san juan":               "70",
    "san luis":               "74",
    "santa cruz":             "78",
    "santa fe":               "82",
    "santiago del estero":    "86",
    "tucuman":                "90",
    "tierra del fuego":       "94",
}


def descargar_indice_estres_hidrico(df_ancla: pd.DataFrame, skip: bool = False) -> pd.DataFrame:
    """
    Intenta descargar el índice de estrés hídrico WRI Aqueduct 4.0 (bws_score).
    Si falla, retorna DataFrame con NaN y documenta la fuente en el log.

    Returns
    -------
    pd.DataFrame con columnas: jurisdiccion_id, indice_estres_hidrico
    """
    df_base = df_ancla[["jurisdiccion_id", "jurisdiccion_nombre"]].copy()
    df_base["indice_estres_hidrico"] = np.nan
    df_base["fuente_hidrica"]        = np.nan

    if skip:
        print("[HÍDRICO] Omitido por flag --skip-aqueduct. indice_estres_hidrico = NaN (24 jur.)")
        return df_base

    print("\n[HÍDRICO] Intentando descarga WRI Aqueduct 4.0 (bws_score)...")

    # Intentar descarga del CSV de rankings provinciales Aqueduct 4.0
    # Fuente directa: GitHub wri/Aqueduct40 (tabla de etiquetas de agregación)
    # Nota: el CSV de rankings por país/provincia requiere formulario en wri.org;
    #       intentamos la tabla del repositorio público de WRI como primera opción.
    urls_a_probar = [
        # CSV de scores por cuenca/provincia del repositorio oficial WRI
        "https://raw.githubusercontent.com/wri/Aqueduct40/master/routing/"
        "aqueduct40_waterrisk_directory_and_aggregation_labels_20230901.csv",
        # Alternativa: versión 3.0 con cobertura provincial Argentina confirmada
        "https://wri-projects.s3.amazonaws.com/Aqueduct30/finalData/Y2019M07D12_RH_Aqueduct_Results_V01/"
        "Y2019M07D12_RH_Aqueduct30_V01.csv",
    ]

    df_wri = None
    url_usada = None

    for url in urls_a_probar:
        try:
            print(f"  → Probando: {url[:80]}...")
            with httpx.Client(follow_redirects=True, timeout=30) as client:
                resp = client.get(url)
                resp.raise_for_status()

            from io import StringIO
            df_wri = pd.read_csv(StringIO(resp.text), low_memory=False)
            url_usada = url
            print(f"  ✓ Descarga exitosa: {len(df_wri):,} filas × {len(df_wri.columns)} cols")
            break
        except Exception as exc:
            print(f"  ✗ Falló ({type(exc).__name__}): {exc}")

    if df_wri is None:
        print(
            "\n[ADVERTENCIA] No se pudo descargar WRI Aqueduct 4.0.\n"
            "  indice_estres_hidrico = NaN para las 24 jurisdicciones.\n"
            "  ACCIÓN MANUAL REQUERIDA:\n"
            "  1. Ir a: https://www.wri.org/applications/aqueduct/water-risk-atlas/\n"
            "  2. Descargar 'Aqueduct 4.0 Province Rankings' (CSV o GPKG)\n"
            "  3. Colocar en: data/01_raw/aqueduct40_province_rankings_arg.csv\n"
            "  4. Volver a ejecutar este script.\n"
        )
        return df_base

    # Detectar columna de estrés hídrico (bws_score o similar)
    col_bws = None
    for c in df_wri.columns:
        if "bws" in c.lower() and "score" in c.lower():
            col_bws = c
            break
    if col_bws is None:
        # buscar cualquier columna de water stress
        for c in df_wri.columns:
            if "bws" in c.lower() or "water_stress" in c.lower():
                col_bws = c
                break

    # Detectar columna de país y provincia
    col_pais    = next((c for c in df_wri.columns if c.lower() in {"gid_0", "iso_a3", "country", "pais"}), None)
    col_prov    = next((c for c in df_wri.columns if c.lower() in {"name_1", "provincia", "region", "state"}), None)

    if col_bws is None or col_pais is None or col_prov is None:
        print(
            f"[ADVERTENCIA] No se encontraron las columnas esperadas en WRI CSV.\n"
            f"  Columnas disponibles: {list(df_wri.columns[:20])}\n"
            f"  col_bws={col_bws}, col_pais={col_pais}, col_prov={col_prov}\n"
            f"  indice_estres_hidrico = NaN para las 24 jurisdicciones.\n"
        )
        return df_base

    # Filtrar Argentina
    df_arg = df_wri[df_wri[col_pais].astype(str).str.upper().isin({"ARG", "ARGENTINA"})]
    print(f"  → Filas para Argentina: {len(df_arg)}")

    if df_arg.empty:
        print("[ADVERTENCIA] No se encontraron registros de Argentina en el CSV WRI.")
        return df_base

    # Calcular score promedio por provincia (media ponderada simple)
    df_arg = df_arg.copy()
    df_arg[col_bws] = pd.to_numeric(df_arg[col_bws], errors="coerce")
    prom_prov = (
        df_arg.groupby(col_prov)[col_bws]
        .mean()
        .reset_index()
        .rename(columns={col_prov: "prov_wri", col_bws: "bws_score"})
    )

    # Join con ancla por nombre normalizado
    prom_prov["prov_norm"] = prom_prov["prov_wri"].apply(_normalizar_nombre_provincia)
    prom_prov["jid_match"] = prom_prov["prov_norm"].map(_MAPA_WRI_A_INDEC)

    df_match = prom_prov.dropna(subset=["jid_match"])
    n_match  = df_match["jid_match"].nunique()
    print(f"  → Provincias mapeadas: {n_match}/24")

    # Merge al DataFrame base
    score_map = df_match.set_index("jid_match")["bws_score"].to_dict()
    df_base["indice_estres_hidrico"] = df_base["jurisdiccion_id"].map(score_map).round(3)
    df_base.loc[df_base["indice_estres_hidrico"].notna(), "fuente_hidrica"] = (
        f"WRI Aqueduct 4.0 — bws_score — {url_usada[:60]}"
    )

    n_ok   = df_base["indice_estres_hidrico"].notna().sum()
    n_null = df_base["indice_estres_hidrico"].isna().sum()
    print(f"[OK] Estrés hídrico: {n_ok}/24 con datos | {n_null}/24 con NaN")

    return df_base


# ─────────────────────────────────────────────────────────────────────────────
# 5. Ensamblado y exportación final
# ─────────────────────────────────────────────────────────────────────────────

COLUMNAS_SALIDA = [
    "jurisdiccion_id",
    "jurisdiccion_nombre",
    "temp_media_anual_c",
    "temp_max_verano_prom_c",
    "horas_free_cooling_estimadas",
    "pue_climatologico_estimado",
    "indice_estres_hidrico",
    "n_dias_datos",
    "fuente_clima",
    "fuente_hidrica",
    "periodo_referencia",
    "umbral_free_cooling_c",
    "pue_base_mecanico",
    "pue_min_free_cooling",
    "factor_horario_ajuste",
]


def exportar_dim_clima_agua(df_clima: pd.DataFrame, df_hidrico: pd.DataFrame) -> pd.DataFrame:
    """
    Une dimensiones climáticas e hídricas y exporta dim_clima_agua.csv.
    """
    df = df_clima.merge(
        df_hidrico[["jurisdiccion_id", "indice_estres_hidrico", "fuente_hidrica"]],
        on="jurisdiccion_id",
        how="left",
    )

    # Seleccionar y ordenar columnas de salida
    cols_presentes = [c for c in COLUMNAS_SALIDA if c in df.columns]
    df = df[cols_presentes].sort_values("jurisdiccion_id").reset_index(drop=True)

    OUT_CLIMA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CLIMA_CSV, index=False, encoding="utf-8-sig")

    print(f"\n[OK] Exportado → {OUT_CLIMA_CSV}")
    print(f"     {len(df)} filas × {len(df.columns)} columnas")

    # Reporte de nulos
    print("\n[QA] Reporte de nulos por columna:")
    for col in ["temp_media_anual_c", "temp_max_verano_prom_c",
                "horas_free_cooling_estimadas", "pue_climatologico_estimado",
                "indice_estres_hidrico"]:
        if col in df.columns:
            n_null = df[col].isna().sum()
            pct    = round(n_null / len(df) * 100, 1)
            estado = "✅" if n_null == 0 else ("🟡" if n_null < 24 else "🔴")
            print(f"  {estado} {col}: {n_null}/24 NaN ({pct} %)")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 6. Main
# ─────────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="ETL Clima y PUE — Bloque 2.2 — Viabilidad IA Data Centers AR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida configuración sin llamar a la API real.",
    )
    p.add_argument(
        "--skip-aqueduct",
        action="store_true",
        help="Omite la descarga de WRI Aqueduct (indice_estres_hidrico = NaN).",
    )
    p.add_argument(
        "--usar-raw-existente",
        action="store_true",
        help=(
            "Reutiliza data/01_raw/clima_24_jurisdicciones_raw.json si existe, "
            "sin volver a llamar a Open-Meteo."
        ),
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    print("=" * 65)
    print("  ETL Clima y PUE — Bloque 2.2")
    print("  Viabilidad IA Data Centers AR")
    print("=" * 65)

    # 1. Cargar ancla territorial
    df_ancla = cargar_ancla()

    # 2. Descargar datos climáticos (o reutilizar raw existente)
    if args.usar_raw_existente and RAW_CLIMA_JSON.exists():
        print(f"\n[CLIMA] Reutilizando raw existente: {RAW_CLIMA_JSON}")
        with open(RAW_CLIMA_JSON, encoding="utf-8") as f:
            raw_data = json.load(f)
        resultados_raw = raw_data.get("jurisdicciones", {})
    else:
        resultados_raw = descargar_clima_open_meteo(df_ancla, dry_run=args.dry_run)

    # 3. Calcular variables climáticas y PUE
    df_clima = calcular_todas_las_jurisdicciones(df_ancla, resultados_raw)

    # 4. Descargar índice de estrés hídrico WRI
    df_hidrico = descargar_indice_estres_hidrico(df_ancla, skip=args.skip_aqueduct)

    # 5. Ensamblar y exportar
    df_final = exportar_dim_clima_agua(df_clima, df_hidrico)

    print("\n" + "=" * 65)
    print("  ✅ Módulo 1 (Clima y PUE) completado.")
    print(f"     Raw  → {RAW_CLIMA_JSON.relative_to(_REPO_ROOT)}")
    print(f"     Dim  → {OUT_CLIMA_CSV.relative_to(_REPO_ROOT)}")
    print("=" * 65)


if __name__ == "__main__":
    main()
