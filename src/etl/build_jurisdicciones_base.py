"""
build_jurisdicciones_base.py
============================
Genera la tabla ancla territorial `data/02_interim/jurisdicciones_base.csv`
con las 24 jurisdicciones argentinas (23 provincias + CABA).

Fuentes:
  - Códigos INDEC: Nomenclador Geográfico Único (NGU) — INDEC.
    https://www.indec.gob.ar/indec/web/Nivel3-Tema-1-39
  - Coordenadas capitales: IGN — Instituto Geográfico Nacional.
    https://www.ign.gob.ar/NuestrasActividades/Geografia/DatosArgentina/Capitales

Reglas de gobernanza (AGENTS.md §4):
  - Solo escribe en data/02_interim/. Nunca en data/01_raw/.
  - Cero datos inventados: coordenadas son datos cartográficos fijos (IGN).
  - Proyección: EPSG:4326 (WGS84).
  - Encoding de salida: UTF-8-BOM (compatible con Excel y Power BI).

Uso:
    python src/etl/build_jurisdicciones_base.py

Salida:
    data/02_interim/jurisdicciones_base.csv
"""

import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# 0. Rutas
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "data" / "02_interim"
OUTPUT_FILE = OUTPUT_DIR / "jurisdicciones_base.csv"

# ---------------------------------------------------------------------------
# 1. Datos fuente — 24 jurisdicciones argentinas
#    Fuente códigos : INDEC — NGU (código de 2 dígitos)
#    Fuente coords  : IGN — Capitales provinciales (EPSG:4326 / WGS84)
#
#    Formato de cada tupla:
#    (jurisdiccion_id, jurisdiccion_nombre, jurisdiccion_corta,
#     region_argentina, lat_capital, lon_capital)
# ---------------------------------------------------------------------------
JURISDICCIONES = [
    # ── AMBA ────────────────────────────────────────────────────────────────
    ("02", "Ciudad Autónoma de Buenos Aires", "CABA",             "AMBA",      -34.6037, -58.3816),
    ("06", "Buenos Aires",                    "Buenos Aires",     "AMBA",      -34.9205, -57.9536),
    # ── NOA ─────────────────────────────────────────────────────────────────
    ("10", "Catamarca",                       "Catamarca",        "NOA",       -28.4696, -65.7852),
    ("38", "Jujuy",                           "Jujuy",            "NOA",       -24.1858, -65.2995),
    ("46", "La Rioja",                        "La Rioja",         "NOA",       -29.4131, -66.8558),
    ("66", "Salta",                           "Salta",            "NOA",       -24.7821, -65.4232),
    ("86", "Santiago del Estero",             "Stgo. Estero",     "NOA",       -27.7951, -64.2615),
    ("90", "Tucumán",                         "Tucumán",          "NOA",       -26.8083, -65.2176),
    # ── NEA ─────────────────────────────────────────────────────────────────
    ("18", "Corrientes",                      "Corrientes",       "NEA",       -27.4806, -58.8341),
    ("22", "Chaco",                           "Chaco",            "NEA",       -27.4514, -58.9868),
    ("34", "Formosa",                         "Formosa",          "NEA",       -26.1775, -58.1781),
    ("54", "Misiones",                        "Misiones",         "NEA",       -27.3671, -55.8963),
    # ── Cuyo ────────────────────────────────────────────────────────────────
    ("50", "Mendoza",                         "Mendoza",          "Cuyo",      -32.8908, -68.8272),
    ("70", "San Juan",                        "San Juan",         "Cuyo",      -31.5375, -68.5364),
    ("74", "San Luis",                        "San Luis",         "Cuyo",      -33.3022, -66.3375),
    # ── Centro ──────────────────────────────────────────────────────────────
    ("14", "Córdoba",                         "Córdoba",          "Centro",    -31.4201, -64.1888),
    ("30", "Entre Ríos",                      "Entre Ríos",       "Centro",    -31.7413, -60.5238),
    ("42", "La Pampa",                        "La Pampa",         "Centro",    -36.6167, -64.2833),
    ("82", "Santa Fe",                        "Santa Fe",         "Centro",    -31.6333, -60.7000),
    # ── Patagonia ───────────────────────────────────────────────────────────
    ("26", "Chubut",                          "Chubut",           "Patagonia", -43.3002, -65.1023),
    ("58", "Neuquén",                         "Neuquén",          "Patagonia", -38.9516, -68.0591),
    ("62", "Río Negro",                       "Río Negro",        "Patagonia", -40.8135, -62.9967),
    ("78", "Santa Cruz",                      "Santa Cruz",       "Patagonia", -51.6230, -69.2184),
    ("94", "Tierra del Fuego",                "Tierra del Fuego", "Patagonia", -54.8019, -68.3030),
]

COLUMNAS = [
    "jurisdiccion_id",
    "jurisdiccion_nombre",
    "jurisdiccion_corta",
    "region_argentina",
    "lat_capital",
    "lon_capital",
]

# Rango válido WGS84 para Argentina continental + insular
LAT_MIN, LAT_MAX = -55.5, -21.0
LON_MIN, LON_MAX = -74.0, -53.0


# ---------------------------------------------------------------------------
# 2. Validaciones internas
# ---------------------------------------------------------------------------

def _validar(df: pd.DataFrame) -> None:
    """Ejecuta 7 checks de integridad. Lanza ValueError ante cualquier fallo."""
    errores = []

    # Check 1 — exactamente 24 filas
    if len(df) != 24:
        errores.append(f"[CHECK 1] Filas esperadas: 24. Encontradas: {len(df)}.")

    # Check 2 — columnas obligatorias presentes
    for col in COLUMNAS:
        if col not in df.columns:
            errores.append(f"[CHECK 2] Columna obligatoria ausente: '{col}'.")

    if errores:
        raise ValueError("\n".join(errores))

    # Check 3 — IDs únicos
    duplicados = df[df["jurisdiccion_id"].duplicated()]["jurisdiccion_id"].tolist()
    if duplicados:
        errores.append(f"[CHECK 3] jurisdiccion_id duplicados: {duplicados}.")

    # Check 4 — IDs son strings de exactamente 2 dígitos numéricos
    invalidos = df[~df["jurisdiccion_id"].str.match(r"^\d{2}$")]["jurisdiccion_id"].tolist()
    if invalidos:
        errores.append(f"[CHECK 4] jurisdiccion_id con formato inválido: {invalidos}.")

    # Check 5 — sin valores nulos en columnas de ancla
    nulos = df[COLUMNAS].isnull().sum()
    nulos_detectados = nulos[nulos > 0].to_dict()
    if nulos_detectados:
        errores.append(f"[CHECK 5] Nulos en columnas ancla: {nulos_detectados}.")

    # Check 6 — latitud en rango Argentina
    fuera_lat = df[~df["lat_capital"].between(LAT_MIN, LAT_MAX)]["jurisdiccion_nombre"].tolist()
    if fuera_lat:
        errores.append(
            f"[CHECK 6] Latitudes fuera de rango [{LAT_MIN}, {LAT_MAX}]: {fuera_lat}."
        )

    # Check 7 — longitud en rango Argentina
    fuera_lon = df[~df["lon_capital"].between(LON_MIN, LON_MAX)]["jurisdiccion_nombre"].tolist()
    if fuera_lon:
        errores.append(
            f"[CHECK 7] Longitudes fuera de rango [{LON_MIN}, {LON_MAX}]: {fuera_lon}."
        )

    if errores:
        raise ValueError("\n".join(errores))


# ---------------------------------------------------------------------------
# 3. Construcción y exportación
# ---------------------------------------------------------------------------

def build() -> pd.DataFrame:
    """Construye, valida y exporta jurisdicciones_base.csv. Retorna el DataFrame."""

    print("=" * 60)
    print("build_jurisdicciones_base.py")
    print("Bloque 2.1 — Ancla Territorial (24 jurisdicciones AR)")
    print("=" * 60)

    # Construir DataFrame
    df = pd.DataFrame(JURISDICCIONES, columns=COLUMNAS)

    # Garantizar tipos correctos
    df["jurisdiccion_id"] = df["jurisdiccion_id"].astype(str).str.zfill(2)
    df["jurisdiccion_nombre"] = df["jurisdiccion_nombre"].astype(str)
    df["jurisdiccion_corta"] = df["jurisdiccion_corta"].astype(str)
    df["region_argentina"] = df["region_argentina"].astype(str)
    df["lat_capital"] = pd.to_numeric(df["lat_capital"], errors="raise")
    df["lon_capital"] = pd.to_numeric(df["lon_capital"], errors="raise")

    # Ordenar por jurisdiccion_id ascendente (02 → 94)
    df = df.sort_values("jurisdiccion_id").reset_index(drop=True)

    print(f"\n[INFO] DataFrame construido: {len(df)} filas × {len(df.columns)} columnas.")

    # Validar
    print("[INFO] Ejecutando 7 checks de integridad...")
    try:
        _validar(df)
        print("[OK]   Todos los checks pasaron exitosamente.")
    except ValueError as e:
        print(f"[ERROR] Validación fallida:\n{e}")
        sys.exit(1)

    # Distribución por región
    print("\n[INFO] Distribución por región:")
    for region, count in df["region_argentina"].value_counts().sort_index().items():
        print(f"       {region:<12} → {count} jurisdicción(es)")

    # Exportar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")  # utf-8-sig = UTF-8 BOM

    print(f"\n[OK]   Archivo exportado: {OUTPUT_FILE}")
    print(f"       Encoding: UTF-8-BOM | Separador: coma | Sin índice")
    print("=" * 60)

    return df


# ---------------------------------------------------------------------------
# 4. Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build()
