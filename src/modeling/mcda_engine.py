"""
Motor MCDA Jerárquico Multi-Perfil (Fase 3 — Bloque 3.1)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

Responsabilidades:
1. Calcular los 5 sub-scores dimensionales (0-100) a partir de las features normalizadas.
2. Validar con tolerancia estricta (1e-6) que la suma de pesos de entrada sume exactamente 1.0.
3. Computar el Score Compuesto Final (WSM) y rankings para cualquier perfil de ponderación arbitrario.
4. Evaluar en lote los perfiles definidos en config/weights_profiles.json:
   - campus_ia_training (Perfil A)
   - nodo_inferencia_edge (Perfil B)
   - benchmark_cabase (Perfil C)
5. Exportar los resultados consolidados con los 5 sub-scores, scores y rankings a Parquet y CSV.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import json
import numpy as np
import pandas as pd

# Asegurar importación robusta tanto como módulo como script CLI
_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from src.modeling.preprocessing import preprocess_features, ANCHOR_COLUMNS

# Pesos internos para el cálculo de cada sub-score dimensional
# Cada dimensión suma exactamente 1.0
INTRA_DIMENSION_WEIGHTS: Dict[str, Dict[str, float]] = {
    "subscore_energia": {
        "norm_potencia_sadi": 0.60,
        "norm_pct_renovable": 0.40,
    },
    "subscore_clima": {
        "norm_pue_climatologico": 0.65,
        "norm_temp_max_verano": 0.35,
    },
    "subscore_conectividad": {
        "norm_distancia_las_toninas": 0.35,
        "norm_velocidad_bajada": 0.25,
        "norm_penetracion_hogares": 0.20,
        "norm_fibra_optica_pct": 0.20,
    },
    "subscore_fiscal": {
        "norm_indice_promocion_fiscal": 0.50,
        "norm_rigi_adhesion": 0.30,
        "norm_iibb_alicuota_tech": 0.20,
    },
    "subscore_talento_riesgo": {
        "norm_densidad_stem": 0.40,
        "norm_puestos_software": 0.30,
        "norm_seguridad_sismica": 0.30,
    },
    "subscore_tier_readiness": {
        "norm_n_centrales_sadi": 0.15,
        "norm_sadi_diversidad_tech": 0.15,
        "norm_seguridad_sismica": 0.25,
        "norm_temp_max_verano": 0.25,
        "norm_fibra_optica_pct": 0.10,
        "norm_velocidad_bajada": 0.10,
    },
}

# Mapeo de dimensión conceptual a columna de subscore
DIMENSION_TO_SUBSCORE_MAP: Dict[str, str] = {
    "dimension_energia": "subscore_energia",
    "dimension_clima": "subscore_clima",
    "dimension_conectividad": "subscore_conectividad",
    "dimension_fiscal": "subscore_fiscal",
    "dimension_talento_riesgo": "subscore_talento_riesgo",
    "dimension_tier_readiness": "subscore_tier_readiness",
}

SUBSCORE_COLUMNS: List[str] = list(INTRA_DIMENSION_WEIGHTS.keys())


def validate_weights(
    weights: Dict[str, float],
    expected_dimensions: Optional[List[str]] = None,
    tolerance: float = 1e-6,
) -> None:
    """
    Comprueba que el diccionario de pesos contenga valores numéricos válidos,
    no negativos y cuya suma sea estrictamente igual a 1.0 (tolerancia 1e-6).
    """
    if not isinstance(weights, dict) or len(weights) == 0:
        raise ValueError("El parámetro de pesos debe ser un diccionario no vacío.")

    if expected_dimensions:
        missing = [d for d in expected_dimensions if d not in weights]
        if missing:
            raise KeyError(f"Faltan dimensiones requeridas en los pesos: {missing}")

    weight_sum = 0.0
    for dim, w in weights.items():
        if not isinstance(w, (int, float, np.number)):
            raise TypeError(f"El peso de la dimensión '{dim}' debe ser numérico. Obtenido: {type(w)}")
        if w < 0.0:
            raise ValueError(f"El peso de la dimensión '{dim}' no puede ser negativo ({w}).")
        weight_sum += float(w)

    diff = abs(weight_sum - 1.0)
    if diff > tolerance:
        raise ValueError(
            f"La suma de los pesos ({weight_sum:.8f}) debe ser exactamente 1.0 "
            f"(diferencia {diff:.2e} > tolerancia {tolerance:.2e})."
        )


def calculate_dimensional_subscores(df_norm: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula los 5 sub-scores dimensionales [0, 100] combinando linealmente
    las features normalizadas con los pesos intra-dimensión.

    Retorna un DataFrame con las columnas de anclaje más los 5 subscores:
    - subscore_energia
    - subscore_clima
    - subscore_conectividad
    - subscore_fiscal
    - subscore_talento_riesgo
    """
    df_res = df_norm[ANCHOR_COLUMNS].copy()

    for subscore_name, feat_weights in INTRA_DIMENSION_WEIGHTS.items():
        # Validar consistencia interna de pesos
        validate_weights(feat_weights, tolerance=1e-6)

        subscore_series = pd.Series(0.0, index=df_norm.index, dtype=float)
        for feat, weight in feat_weights.items():
            if feat not in df_norm.columns:
                raise KeyError(f"Feature normalizada '{feat}' ausente para calcular {subscore_name}.")
            subscore_series += df_norm[feat].astype(float) * float(weight)

        df_res[subscore_name] = subscore_series.clip(lower=0.0, upper=100.0).round(4)

    return df_res


def calculate_composite_score(
    df_subscores: pd.DataFrame,
    weights: Dict[str, float],
    tolerance: float = 1e-6,
) -> pd.Series:
    """
    Calcula el Score Compuesto Final (WSM, 0 a 100) para un conjunto de pesos dimensionales.

    Acepta claves con prefijo 'dimension_' (ej. 'dimension_energia') o
    directamente nombres de subscore (ej. 'subscore_energia').
    """
    # Mapear claves a nombres de columnas de subscore
    normalized_weights: Dict[str, float] = {}
    for k, v in weights.items():
        if k in DIMENSION_TO_SUBSCORE_MAP:
            normalized_weights[DIMENSION_TO_SUBSCORE_MAP[k]] = float(v)
        elif k in SUBSCORE_COLUMNS:
            normalized_weights[k] = float(v)
        elif not k.startswith("_"):  # Ignorar metadatos que empiecen con '_'
            raise KeyError(f"Dimensión de peso no reconocida: '{k}'")

    validate_weights(normalized_weights, expected_dimensions=SUBSCORE_COLUMNS, tolerance=tolerance)

    composite = pd.Series(0.0, index=df_subscores.index, dtype=float)
    for subscore_col, w in normalized_weights.items():
        composite += df_subscores[subscore_col].astype(float) * w

    return composite.clip(lower=0.0, upper=100.0).round(6)


def evaluate_all_profiles(
    df_subscores: pd.DataFrame,
    profiles_config: Dict[str, Any],
) -> pd.DataFrame:
    """
    Aplica el motor MCDA para cada perfil configurado en el archivo JSON.
    Genera para cada perfil su score compuesto (0-100) y su ranking ordinal (1 a 24).

    Preserva los 5 sub-scores dimensionales en la tabla de salida.
    """
    df_out = df_subscores.copy()

    for profile_id, profile_data in profiles_config.items():
        if profile_id.startswith("_"):
            continue  # Saltar metadatos como _meta

        # Extraer pesos excluyendo campos que inicien con '_'
        weights = {k: v for k, v in profile_data.items() if not k.startswith("_")}
        score_col = f"score_{profile_id}"
        rank_col = f"rank_{profile_id}"

        # Cálculo de score con precisión suficiente para desempate
        score_series = calculate_composite_score(df_subscores, weights)

        # Asignar primero score y luego ranking para mantener orden de columnas
        df_out[score_col] = score_series.round(4)
        df_out[rank_col] = score_series.rank(ascending=False, method="min").astype(int)

    return df_out


def run_mcda_pipeline(
    master_path: str = "data/03_processed/master_24_jurisdicciones.parquet",
    config_path: str = "config/weights_profiles.json",
    output_dir: str = "data/04_outputs",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Orquestador end-to-end de la Fase 3 — Bloque 3.1:
    1. Carga master table consolidada.
    2. Ejecuta preprocesamiento y normalización de features.
    3. Computa subscores dimensionales.
    4. Evalúa perfiles configurados.
    5. Exporta resultados en Parquet y CSV.
    """
    master_file = Path(master_path)
    config_file = Path(config_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not master_file.exists():
        raise FileNotFoundError(f"No se encontró la tabla maestra en: {master_file}")
    if not config_file.exists():
        raise FileNotFoundError(f"No se encontró la configuración de perfiles en: {config_file}")

    # 1. Cargar datos y configuración
    df_raw = pd.read_parquet(master_file)
    with open(config_file, "r", encoding="utf-8") as f:
        profiles_config = json.load(f)

    # 2. Preprocesamiento
    df_norm, _ = preprocess_features(df_raw)

    # 3. Subscores dimensionales
    df_subscores = calculate_dimensional_subscores(df_norm)

    # 4. Evaluación de perfiles
    df_scored = evaluate_all_profiles(df_subscores, profiles_config)

    # 5. Exportaciones
    parquet_path = out_dir / "scores_mcda_perfiles.parquet"
    csv_path = out_dir / "scores_mcda_perfiles.csv"

    # Exportación Parquet (Snappy)
    df_scored.to_parquet(parquet_path, engine="pyarrow", compression="snappy", index=False)

    # Exportación CSV (UTF-8-SIG para Excel / Power BI)
    df_scored.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return df_norm, df_scored


if __name__ == "__main__":
    df_norm, df_scored = run_mcda_pipeline()
    print("MCDA Pipeline ejecutado exitosamente.")
    print(f"Dimensiones de salida: {df_scored.shape[0]} filas × {df_scored.shape[1]} columnas.")
    print("Columnas:", df_scored.columns.tolist())
    print("\nTop 5 - Perfil A (Campus IA Training):")
    cols_a = ["jurisdiccion_corta", "score_campus_ia_training", "rank_campus_ia_training", "subscore_energia", "subscore_clima", "subscore_fiscal"]
    print(df_scored[cols_a].sort_values("rank_campus_ia_training").head(5).to_string(index=False))

    print("\nTop 5 - Perfil B (Nodo Inferencia Edge):")
    cols_b = ["jurisdiccion_corta", "score_nodo_inferencia_edge", "rank_nodo_inferencia_edge", "subscore_conectividad", "subscore_talento_riesgo", "subscore_fiscal"]
    print(df_scored[cols_b].sort_values("rank_nodo_inferencia_edge").head(5).to_string(index=False))
