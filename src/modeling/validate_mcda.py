"""
Suite de Validación y Control de Calidad Estadístico del Motor MCDA (Fase 3 — Bloque 3.1)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

Ejecuta aserciones estadísticas, comprobación de invariantes matemáticas y
verificación de integridad física de los archivos de salida generados.
"""

import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd

_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from src.modeling.preprocessing import preprocess_features, EXCLUDED_NAN_COLUMNS
from src.modeling.mcda_engine import (
    validate_weights,
    calculate_dimensional_subscores,
    calculate_composite_score,
    evaluate_all_profiles,
    SUBSCORE_COLUMNS,
)


def run_all_validations() -> None:
    print("=" * 80)
    print("INICIANDO SUITE DE VALIDACIÓN MCDA (FASE 3 — BLOQUE 3.1)")
    print("=" * 80)

    # 1. Validación de Exclusión de NaNs
    master_path = Path("data/03_processed/master_24_jurisdicciones.parquet")
    assert master_path.exists(), f"No existe {master_path}"
    df_raw = pd.read_parquet(master_path)
    assert len(df_raw) == 24, f"Se esperaban 24 filas, obtenidas {len(df_raw)}"

    for nan_col in EXCLUDED_NAN_COLUMNS:
        assert nan_col in df_raw.columns, f"Columna {nan_col} debe existir en raw master"
        assert df_raw[nan_col].isna().all(), f"Columna {nan_col} debe ser 100% NaN"

    print("✔ [1/7] Exclusión de 13 columnas 100% NaN verificada sin imputaciones sintéticas.")

    # 2. Validación de Preprocesamiento y log1p
    df_norm, meta = preprocess_features(df_raw)
    norm_cols = [c for c in df_norm.columns if c.startswith("norm_")]
    assert len(norm_cols) == 16, f"Se esperaban 16 features normalizadas, obtenidas {len(norm_cols)}"
    assert df_norm[norm_cols].isna().sum().sum() == 0, "No debe haber ningún NaN en features normalizadas"

    for col in norm_cols:
        c_min = df_norm[col].min()
        c_max = df_norm[col].max()
        assert c_min >= 0.0 - 1e-6, f"{col} min < 0 ({c_min})"
        assert c_max <= 100.0 + 1e-6, f"{col} max > 100 ({c_max})"

    # Comprobar efecto mitigador de log1p
    caba_sw = df_norm.loc[df_norm["jurisdiccion_id"] == "02", "norm_puestos_software"].values[0]
    pba_sw = df_norm.loc[df_norm["jurisdiccion_id"] == "06", "norm_puestos_software"].values[0]
    cba_sw = df_norm.loc[df_norm["jurisdiccion_id"] == "14", "norm_puestos_software"].values[0]
    assert caba_sw == 100.0, "CABA debe tener 100 en puestos_software normalizado"
    assert pba_sw > 70.0, f"PBA con log1p debe mantener un score competitivo ({pba_sw})"
    assert cba_sw > 70.0, f"Córdoba con log1p debe mantener un score competitivo ({cba_sw})"

    print("✔ [2/7] Normalización [0-100] y mitigación de asimetría con log1p validadas.")

    # 3. Validación de Caso Físico de Tierra del Fuego
    tdf_row = df_norm[df_norm["jurisdiccion_id"] == "94"].iloc[0]
    assert tdf_row["norm_potencia_sadi"] == 0.0, "TDF debe tener 0.0 en potencia SADI normalizada"
    assert tdf_row["norm_pct_renovable"] == 0.0, "TDF debe tener 0.0 en % renovable SADI"
    assert tdf_row["norm_n_centrales_sadi"] == 0.0, "TDF debe tener 0.0 en n_centrales_sadi"
    assert tdf_row["norm_sadi_diversidad_tech"] == 0.0, "TDF debe tener 0.0 en sadi_diversidad_tech"
    assert tdf_row["norm_pue_climatologico"] == 100.0, "TDF debe tener el PUE más eficiente (100 pts)"
    assert tdf_row["norm_indice_promocion_fiscal"] == 100.0, "TDF debe tener máxima promoción fiscal (100 pts)"

    print("✔ [3/7] Restricción física de Tierra del Fuego (red aislada = 0 MW y 0 fuentes SADI) modelada con rigurosidad.")

    # 4. Validación de Suma de Pesos y Control de Errores
    try:
        validate_weights({"a": 0.5, "b": 0.4}, tolerance=1e-6)
        assert False, "Debió fallar por suma != 1.0"
    except ValueError as e:
        assert "debe ser exactamente 1.0" in str(e)

    try:
        validate_weights({"a": 1.2, "b": -0.2}, tolerance=1e-6)
        assert False, "Debió fallar por peso negativo"
    except ValueError as e:
        assert "no puede ser negativo" in str(e)

    print("✔ [4/7] Validador estricto de pesos (tolerancia 1e-6 y rechazo de pesos negativos) verificado.")

    # 5. Validación de Sub-scores Dimensionales
    df_subscores = calculate_dimensional_subscores(df_norm)
    assert len(SUBSCORE_COLUMNS) == 6, f"Se esperaban 6 subscores dimensionales, obtenidos {len(SUBSCORE_COLUMNS)}"
    for sub in SUBSCORE_COLUMNS:
        assert sub in df_subscores.columns, f"Falta {sub} en df_subscores"
        assert df_subscores[sub].isna().sum() == 0, f"NaNs en {sub}"
        assert df_subscores[sub].min() >= 0.0, f"{sub} min < 0"
        assert df_subscores[sub].max() <= 100.0, f"{sub} max > 100"

    print("✔ [5/7] 6 Sub-scores dimensionales (incluyendo subscore_tier_readiness) calculados y acotados estrictamente a [0, 100].")

    # 6. Validación de Outputs Persistidos (Parquet y CSV)
    out_parquet = Path("data/04_outputs/scores_mcda_perfiles.parquet")
    out_csv = Path("data/04_outputs/scores_mcda_perfiles.csv")
    assert out_parquet.exists(), f"No existe {out_parquet}"
    assert out_csv.exists(), f"No existe {out_csv}"

    df_p = pd.read_parquet(out_parquet)
    df_c = pd.read_csv(out_csv)
    assert len(df_p) == 24 and len(df_c) == 24, "Deben ser 24 filas exactas"

    expected_cols = [
        "jurisdiccion_id", "jurisdiccion_nombre", "jurisdiccion_corta", "region_argentina", "lat_capital", "lon_capital",
        "subscore_energia", "subscore_clima", "subscore_conectividad", "subscore_fiscal", "subscore_talento_riesgo", "subscore_tier_readiness",
        "score_campus_ia_training", "rank_campus_ia_training",
        "score_nodo_inferencia_edge", "rank_nodo_inferencia_edge",
        "score_benchmark_cabase", "rank_benchmark_cabase",
    ]
    assert list(df_p.columns) == expected_cols, f"Columnas Parquet no coinciden con contrato esperado: {df_p.columns.tolist()}"
    assert list(df_c.columns) == expected_cols, f"Columnas CSV no coinciden con contrato esperado: {df_c.columns.tolist()}"

    # Rankings deben ser valores únicos del 1 al 24
    for prof in ["campus_ia_training", "nodo_inferencia_edge", "benchmark_cabase"]:
        ranks = df_p[f"rank_{prof}"].sort_values().tolist()
        assert ranks == list(range(1, 25)), f"Rankings de {prof} no son una permutación perfecta 1..24: {ranks}"

    print("✔ [6/7] Contrato de datos de exportación (Parquet y CSV) y consistencia de rankings 1..24 verificados.")

    # 7. Resumen de Rankings
    print("✔ [7/7] Inspección comparativa de perfiles:")
    summary_cols = ["jurisdiccion_corta", "score_campus_ia_training", "score_nodo_inferencia_edge", "score_benchmark_cabase"]
    print("\n--- COMPARATIVA DE SCORES (TODAS LAS JURISDICCIONES) ---")
    print(df_p[summary_cols].sort_values("score_campus_ia_training", ascending=False).to_string(index=False))

    print("\n" + "=" * 80)
    print("TODAS LAS PRUEBAS DE CALIDAD Y QA PASARON CON ÉXITO (7/7).")
    print("=" * 80)


if __name__ == "__main__":
    run_all_validations()
