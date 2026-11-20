"""
build_fiscal_regulatoria.py
============================
Construye la dimensión fiscal y regulatoria `data/02_interim/dim_fiscal_regulatoria.csv`
para las 24 jurisdicciones de Argentina (23 provincias + CABA).

Estructura de variables (Sección 4 de docs/data_dictionary.md):
  - rigi_adhesion: bool (True/False según adhesión oficial a Ley Nac. 27.742)
  - rigi_normativa: str (Número oficial de ley/decreto provincial)
  - rigi_fecha_sancion: str (Fecha de sanción en formato ISO YYYY-MM-DD o None)
  - iibb_alicuota_tech_pct: float (Alícuota referencial para servicios de software/IT bajo fomento o general)
  - iibb_regimen_promocion: str (Base normativa de Economía del Conocimiento o exención)
  - iibb_alicuota_energia_pct: float (NaN auditable — tarifas de distribución nodales pendientes)
  - indice_promocion_fiscal: float (0.0 a 10.0 — compuesto de inversión + IIBB tech)
  - estado_verificacion_normativa: str ('verificado_oficial' / 'verificar_boletin_oficial')
  - fuente_fiscal: str (Referencia normativa institucional)
  - fecha_corte_fiscal: str (2026-11-20)

Reglas de gobernanza (AGENTS.md):
  - Cero datos inventados: respaldo en docs/supuestos_regulatorios.md y config/data_sources.yaml.
  - Validación 1:1 contra data/02_interim/jurisdicciones_base.csv.
  - Salida: data/02_interim/dim_fiscal_regulatoria.csv (UTF-8-BOM).

Uso:
    python src/etl/build_fiscal_regulatoria.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 0. Rutas
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
ANCLA_PATH = REPO_ROOT / "data" / "02_interim" / "jurisdicciones_base.csv"
OUTPUT_FILE = REPO_ROOT / "data" / "02_interim" / "dim_fiscal_regulatoria.csv"

# ---------------------------------------------------------------------------
# 1. Matriz de Datos Regulatorios — 24 Jurisdicciones
# ---------------------------------------------------------------------------
# Tupla:
# (jurisdiccion_id, jurisdiccion_nombre, rigi_adhesion, rigi_normativa,
#  rigi_fecha_sancion, iibb_alicuota_tech_pct, iibb_regimen_promocion,
#  iibb_alicuota_energia_pct, indice_promocion_fiscal, estado_verificacion_normativa)

REGULATORIO_DATA = [
    # ── AMBA ────────────────────────────────────────────────────────────────
    (
        "02", "Ciudad Autónoma de Buenos Aires",
        True, "Ley CABA N° 6.949", "2026-05-14",
        0.0, "Ley CABA 6.394 / Ley 2.972 Distrito Tecnológico (exenta)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "06", "Buenos Aires",
        False, "Sin adhesión / RPI local Ley Prov.", "2024-09-01",
        0.0, "Ley PBA 13.649 y Ley 15.339 LEC PBA (0% promovida / 3.5% gral)",
        np.nan, 8.5, "verificado_oficial"
    ),

    # ── NOA ─────────────────────────────────────────────────────────────────
    (
        "10", "Catamarca",
        True, "Ley Provincial N° 5.863", "2024-08-08",
        0.0, "Ley Provincial 5.673 LEC Catamarca (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "38", "Jujuy",
        True, "Ley Provincial N° 6.409", "2024-08-01",
        0.0, "Ley Provincial 6.189 LEC Jujuy (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "46", "La Rioja",
        False, "Sin adhesión", None,
        3.0, "Código Tributario La Rioja (alícuota gral servicios)",
        np.nan, 1.0, "verificado_oficial"
    ),
    (
        "66", "Salta",
        True, "Ley Provincial N° 8.451", "2024-08-27",
        0.0, "Ley Provincial 8.271 LEC Salta (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "86", "Santiago del Estero",
        False, "Sin adhesión", None,
        3.0, "Código Fiscal DGR Santiago del Estero (alícuota gral)",
        np.nan, 1.0, "verificado_oficial"
    ),
    (
        "90", "Tucumán",
        True, "Ley Provincial N° 9.803", "2024-08-08",
        0.0, "Ley Provincial 9.352 LEC Tucumán (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),

    # ── NEA ─────────────────────────────────────────────────────────────────
    (
        "18", "Corrientes",
        True, "Ley Provincial N° 6.694", "2024-09-18",
        0.0, "Ley Provincial 6.550 Promoción Industria Conocimiento (exenta)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "22", "Chaco",
        True, "Ley Provincial N° 4.086-F", "2024-09-25",
        0.0, "Ley Provincial 3.190-I Régimen LEC Chaco (exención hasta 100%)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "34", "Formosa",
        False, "Sin adhesión", None,
        3.5, "Ley Tarifaria Formosa (alícuota gral servicios)",
        np.nan, 1.0, "verificado_oficial"
    ),
    (
        "54", "Misiones",
        True, "Ley Provincial VII-N° 106", "2025-08-28",
        0.0, "Ley de Economía del Conocimiento / Silicon Misiones (exenta)",
        np.nan, 10.0, "verificado_oficial"
    ),

    # ── Centro ──────────────────────────────────────────────────────────────
    (
        "14", "Córdoba",
        True, "Ley Provincial N° 10.997", "2024-08-28",
        0.0, "Código Tributario Art. 242 inc. 28 / Ley Cba 10.722 (exenta)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "30", "Entre Ríos",
        True, "Ley Provincial N° 11.162", "2024-09-04",
        0.0, "Ley Provincial 10.895 LEC Entre Ríos (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "42", "La Pampa",
        False, "Sin adhesión", None,
        3.0, "Ley Tarifaria La Pampa (alícuota gral servicios)",
        np.nan, 1.0, "verificado_oficial"
    ),
    (
        "82", "Santa Fe",
        True, "Ley Provincial N° 14.386", "2024-12-19",
        0.0, "Ley Provincial 14.150 LEC Santa Fe (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),

    # ── Cuyo ────────────────────────────────────────────────────────────────
    (
        "50", "Mendoza",
        True, "Ley Provincial N° 9.567", "2024-08-06",
        0.0, "Leyes Provinciales 9.003 y 9.267 Mendoza Activa / LEC (exenta)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "70", "San Juan",
        True, "Ley Provincial N° 2.671-I", "2024-08-15",
        0.0, "Ley Provincial 2.148-F LEC San Juan (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "74", "San Luis",
        True, "Ley Provincial N° VIII-1.135", "2024-09-11",
        0.0, "Ley VIII-0870 Parque Informático La Punta PILP (exenta)",
        np.nan, 10.0, "verificado_oficial"
    ),

    # ── Patagonia ───────────────────────────────────────────────────────────
    (
        "26", "Chubut",
        True, "Ley Provincial N° IX-171", "2024-08-15",
        0.0, "Ley Prov. Promoción Software (0% condicionado a inscripción)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "58", "Neuquén",
        True, "Ley Provincial N° 3.491", "2024-09-12",
        0.0, "Ley Provincial 3.327 LEC Neuquén (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "62", "Río Negro",
        True, "Ley Provincial N° 5.724", "2024-07-26",
        0.0, "Ley Provincial 5.485 LEC Río Negro (exenta promovida)",
        np.nan, 10.0, "verificado_oficial"
    ),
    (
        "78", "Santa Cruz",
        True, "Ley Provincial N° 3.912", "2024-09-26",
        3.0, "ASIP Ley Impositiva Santa Cruz (alícuota gral servicios)",
        np.nan, 6.0, "verificado_oficial"
    ),
    (
        "94", "Tierra del Fuego",
        False, "Régimen Especial Ley Nac. 19.640", "1972-05-16",
        0.0, "Ley 19.640 Área Aduanera Especial / AREF Ley 1075 (exenta)",
        np.nan, 10.0, "verificado_oficial"
    ),
]


def build_dataframe() -> pd.DataFrame:
    """Construye y formatea el DataFrame de dimensión fiscal y regulatoria."""
    columns = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "rigi_adhesion",
        "rigi_normativa",
        "rigi_fecha_sancion",
        "iibb_alicuota_tech_pct",
        "iibb_regimen_promocion",
        "iibb_alicuota_energia_pct",
        "indice_promocion_fiscal",
        "estado_verificacion_normativa",
    ]
    df = pd.DataFrame(REGULATORIO_DATA, columns=columns)

    # Tipado explícito
    df["jurisdiccion_id"] = df["jurisdiccion_id"].astype(str).str.zfill(2)
    df["jurisdiccion_nombre"] = df["jurisdiccion_nombre"].astype(str)
    df["rigi_adhesion"] = df["rigi_adhesion"].astype(bool)
    df["rigi_normativa"] = df["rigi_normativa"].astype(str)
    df["rigi_fecha_sancion"] = df["rigi_fecha_sancion"].astype("string")
    df["iibb_alicuota_tech_pct"] = df["iibb_alicuota_tech_pct"].astype(float)
    df["iibb_regimen_promocion"] = df["iibb_regimen_promocion"].astype(str)
    df["iibb_alicuota_energia_pct"] = df["iibb_alicuota_energia_pct"].astype(float)
    df["indice_promocion_fiscal"] = df["indice_promocion_fiscal"].astype(float)
    df["estado_verificacion_normativa"] = df["estado_verificacion_normativa"].astype(str)

    # Columnas fijas de auditoría
    df["fuente_fiscal"] = "Boletines Oficiales Provinciales / Ley 27.742 / Leyes de Promoción LEC"
    df["fecha_corte_fiscal"] = "2026-11-20"

    # Ordenar por jurisdiccion_id
    df = df.sort_values("jurisdiccion_id").reset_index(drop=True)
    return df


def validate_against_anchor(df: pd.DataFrame) -> None:
    """Verifica que el DataFrame coincida 1:1 con la tabla ancla."""
    if not ANCLA_PATH.exists():
        raise FileNotFoundError(f"No se encontró la tabla ancla: {ANCLA_PATH}")

    ancla = pd.read_csv(ANCLA_PATH, dtype={"jurisdiccion_id": str})

    # Check 1: Conteo
    assert len(df) == 24, f"Se esperaban 24 filas, pero hay {len(df)}"
    assert len(df) == len(ancla), "El conteo no coincide con la tabla ancla"

    # Check 2: Claves idénticas
    assert list(df["jurisdiccion_id"]) == list(ancla["jurisdiccion_id"]), (
        "Los IDs no coinciden exactamente con la tabla ancla"
    )

    # Check 3: Nombres idénticos
    assert list(df["jurisdiccion_nombre"]) == list(ancla["jurisdiccion_nombre"]), (
        "Los nombres no coinciden con la tabla ancla"
    )

    # Check 4: Valores válidos en booleanos y scores
    assert df["rigi_adhesion"].isin([True, False]).all(), "Valores booleanos inválidos en rigi_adhesion"
    assert (df["indice_promocion_fiscal"] >= 0.0).all() and (df["indice_promocion_fiscal"] <= 10.0).all(), (
        "indice_promocion_fiscal fuera de rango [0, 10]"
    )

    print("✔ Validación contra tabla ancla superada con éxito (24/24 jurisdicciones).")


def main() -> int:
    print("Iniciando construcción de Dimensión Fiscal y Regulatoria...")
    df = build_dataframe()
    validate_against_anchor(df)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"✔ Archivo interim generado exitosamente en: {OUTPUT_FILE}")
    print(f"  Filas: {len(df)} | Columnas: {len(df.columns)}")
    print("\nResumen descriptivo:")
    print(f"  - Adheridas a RIGI: {df['rigi_adhesion'].sum()} / 24")
    print(f"  - Promedio Score Promoción Fiscal: {df['indice_promocion_fiscal'].mean():.2f} / 10.0")
    print(f"  - Alícuota IIBB Tech media: {df['iibb_alicuota_tech_pct'].mean():.2f}%")
    print(f"  - IIBB Energía en NaN: {df['iibb_alicuota_energia_pct'].isna().sum()} / 24")
    return 0


if __name__ == "__main__":
    sys.exit(main())
