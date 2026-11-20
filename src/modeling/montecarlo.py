"""
Simulación de Sensibilidad Monte Carlo (Fase 3 — Bloque 3.2)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

Responsabilidades:
1. Cargar sub-scores calculados y configuración de pesos de perfiles.
2. Ejecutar 1.000 iteraciones estocásticas reproducibles (seed=42) por perfil:
   - campus_ia_training (Perfil A)
   - nodo_inferencia_edge (Perfil B)
3. Aplicar perturbación aleatoria simétrica (+/- 20%) sobre cada peso base y renormalizar a suma 1.0.
4. Computar vectorizadamente scores (24 x 1000) y rankings ordinales unívocos.
5. Calcular métricas de estabilidad y riesgo:
   - score medio y desviación estándar
   - intervalo P5-P95 (confianza 90%)
   - ranking mediano
   - probabilidad (%) de calificar en Top 3 y Top 5
6. Exportar resultados consolidados a Parquet y CSV en data/04_outputs/montecarlo_sensibilidad.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
import numpy as np
import pandas as pd

_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from src.modeling.mcda_engine import (
    DIMENSION_TO_SUBSCORE_MAP,
    validate_weights,
    ANCHOR_COLUMNS,
)

EVALUATED_PROFILES: List[str] = [
    "campus_ia_training",
    "nodo_inferencia_edge",
]


def run_montecarlo_for_profile(
    df_subscores: pd.DataFrame,
    profile_id: str,
    base_weights: Dict[str, float],
    n_iterations: int = 1000,
    perturbation_pct: float = 0.20,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Ejecuta la simulación de Monte Carlo vectorizada para un perfil dado.
    """
    rng = np.random.default_rng(seed)

    # Validar pesos base
    validate_weights(base_weights)

    dims = list(base_weights.keys())
    base_w_arr = np.array([base_weights[d] for d in dims], dtype=float)

    # Generar matriz de perturbación U(1 - pct, 1 + pct)
    low_bound = 1.0 - perturbation_pct
    high_bound = 1.0 + perturbation_pct
    perturbations = rng.uniform(low_bound, high_bound, size=(n_iterations, len(base_w_arr)))

    # Perturbar y renormalizar estrictamente para que cada iteración sume 1.0
    sim_weights = base_w_arr * perturbations
    sim_weights = sim_weights / sim_weights.sum(axis=1, keepdims=True)

    # Validar que todas las filas sumen 1.0 con tolerancia 1e-6
    sums = sim_weights.sum(axis=1)
    if not np.allclose(sums, 1.0, atol=1e-6):
        raise ValueError("Error numérico: Pesos simulados no suman 1.0 tras normalización.")

    # Mapear dimensiones a columnas de subscores
    subscore_cols = [DIMENSION_TO_SUBSCORE_MAP.get(d, d) for d in dims]
    S = df_subscores[subscore_cols].values.astype(float)  # Dim: (24, n_dims)

    # Multiplicación matricial vectorizada: (24, n_dims) @ (n_dims, n_iterations) -> (24, n_iterations)
    scores_sim = S @ sim_weights.T

    # Calcular rankings por columna (1 = mayor score)
    ranks_sim = np.zeros_like(scores_sim, dtype=int)
    for i in range(n_iterations):
        ranks_sim[:, i] = pd.Series(scores_sim[:, i]).rank(ascending=False, method="min").values

    # Extraer métricas estadísticas
    score_mean = np.mean(scores_sim, axis=1)
    score_std = np.std(scores_sim, axis=1)
    score_p5 = np.percentile(scores_sim, 5, axis=1)
    score_p95 = np.percentile(scores_sim, 95, axis=1)
    rank_median = np.median(ranks_sim, axis=1).astype(int)

    prob_top3 = np.mean(ranks_sim <= 3, axis=1) * 100.0
    prob_top5 = np.mean(ranks_sim <= 5, axis=1) * 100.0

    # Construir DataFrame con resultados
    res = df_subscores[ANCHOR_COLUMNS].copy()
    res["perfil_id"] = profile_id
    res["mc_score_mean"] = np.round(score_mean, 2)
    res["mc_score_std"] = np.round(score_std, 2)
    res["mc_score_p5"] = np.round(score_p5, 2)
    res["mc_score_p95"] = np.round(score_p95, 2)
    res["mc_rank_median"] = rank_median
    res["prob_top3_pct"] = np.round(prob_top3, 1)
    res["prob_top5_pct"] = np.round(prob_top5, 1)

    return res


def run_montecarlo_pipeline(
    scores_path: str = "data/04_outputs/scores_mcda_perfiles.parquet",
    config_path: str = "config/weights_profiles.json",
    output_dir: str = "data/04_outputs",
    n_iterations: int = 1000,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta la simulación de Monte Carlo para todos los perfiles evaluados
    y exporta los resultados en formatos largo y consolidado.
    """
    scores_file = Path(scores_path)
    cfg_file = Path(config_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not scores_file.exists():
        raise FileNotFoundError(f"Archivo de scores no encontrado: {scores_file}")
    if not cfg_file.exists():
        raise FileNotFoundError(f"Configuración de pesos no encontrada: {cfg_file}")

    df_scores = pd.read_parquet(scores_file)
    with open(cfg_file, "r", encoding="utf-8") as f:
        profiles_cfg = json.load(f)

    long_results = []
    for profile_id in EVALUATED_PROFILES:
        if profile_id not in profiles_cfg:
            continue

        profile_data = profiles_cfg[profile_id]
        profile_name = profile_data.get("_nombre", profile_id)
        base_weights = {k: v for k, v in profile_data.items() if not k.startswith("_")}

        df_mc = run_montecarlo_for_profile(
            df_subscores=df_scores,
            profile_id=profile_id,
            base_weights=base_weights,
            n_iterations=n_iterations,
            perturbation_pct=0.20,
            seed=seed,
        )

        df_mc["perfil_nombre"] = profile_name

        # Incorporar score y ranking determinístico base
        base_score_col = f"score_{profile_id}"
        base_rank_col = f"rank_{profile_id}"
        if base_score_col in df_scores.columns:
            df_mc["score_base"] = df_scores[base_score_col].values
            df_mc["rank_base"] = df_scores[base_rank_col].values
        else:
            df_mc["score_base"] = np.nan
            df_mc["rank_base"] = np.nan

        long_results.append(df_mc)

    df_long = pd.concat(long_results, ignore_index=True)

    # Reordenar columnas para legibilidad ejecutiva
    ordered_cols = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "jurisdiccion_corta",
        "region_argentina",
        "perfil_id",
        "perfil_nombre",
        "score_base",
        "rank_base",
        "mc_score_mean",
        "mc_score_std",
        "mc_score_p5",
        "mc_score_p95",
        "mc_rank_median",
        "prob_top3_pct",
        "prob_top5_pct",
    ]
    df_long = df_long[ordered_cols]

    # Crear versión wide para consolidación directa
    pivoted = df_long.pivot(
        index=["jurisdiccion_id", "jurisdiccion_nombre", "jurisdiccion_corta", "region_argentina"],
        columns="perfil_id",
        values=["mc_score_mean", "mc_score_std", "mc_score_p5", "mc_score_p95", "mc_rank_median", "prob_top3_pct", "prob_top5_pct"],
    )
    pivoted.columns = [f"{col[1]}_{col[0]}" for col in pivoted.columns]
    df_wide = pivoted.reset_index()

    # Exportar
    parquet_path = out_dir / "montecarlo_sensibilidad.parquet"
    csv_path = out_dir / "montecarlo_sensibilidad.csv"

    df_long.to_parquet(parquet_path, engine="pyarrow", compression="snappy", index=False)
    df_long.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return df_long, df_wide


if __name__ == "__main__":
    df_long, df_wide = run_montecarlo_pipeline()
    print("=== MONTE CARLO SENSITIVITY PIPELINE ===")
    print(f"Total registros simulados: {len(df_long)}")
    print("\nTop 5 - Perfil A (Campus IA Training) ordenado por Probabilidad Top 3:")
    cols_show = ["jurisdiccion_corta", "score_base", "mc_score_mean", "mc_score_std", "mc_score_p5", "mc_score_p95", "prob_top3_pct", "prob_top5_pct"]
    top_a = df_long[df_long["perfil_id"] == "campus_ia_training"].sort_values("prob_top3_pct", ascending=False)
    print(top_a[cols_show].head(5).to_string(index=False))

    print("\nTop 5 - Perfil B (Nodo Inferencia Edge) ordenado por Probabilidad Top 3:")
    top_b = df_long[df_long["perfil_id"] == "nodo_inferencia_edge"].sort_values("prob_top3_pct", ascending=False)
    print(top_b[cols_show].head(5).to_string(index=False))
