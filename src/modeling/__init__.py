"""
Módulo de Modelado, Preprocesamiento Estadístico y Motor MCDA
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina
"""

from .preprocessing import preprocess_features, EXCLUDED_NAN_COLUMNS, FEATURE_CONFIG
from .mcda_engine import (
    calculate_dimensional_subscores,
    calculate_composite_score,
    evaluate_all_profiles,
    run_mcda_pipeline,
)

__all__ = [
    "preprocess_features",
    "EXCLUDED_NAN_COLUMNS",
    "FEATURE_CONFIG",
    "calculate_dimensional_subscores",
    "calculate_composite_score",
    "evaluate_all_profiles",
    "run_mcda_pipeline",
]
