"""
Clustering no supervisado de Jurisdicciones Argentinas (Fase 3 — Bloque 3.2)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

Responsabilidades:
1. Cargar sub-scores dimensionales normalizados (0-100) desde data/04_outputs/scores_mcda_perfiles.parquet.
2. Evaluar hiperparámetro k en [3, 6] calculando Silhouette Score e Inercia (método del codo).
3. Entrenar K-Means con k óptimo = 4 y semilla reproducible (random_state=42).
4. Asignar arquetipos de negocio interpretables a cada cluster basándose en sus centroides:
   - Hub Metropolitano & Conectividad Core
   - Polo Austral & Free-Cooling Extremo
   - Corredor Productivo & Energético SADI/Renovable
   - Brecha Fiscal e Infraestructura Rezagada
5. Exportar datasets consolidados en data/04_outputs/clusters_arquetipos.parquet y .csv.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

FEATURE_COLUMNS: List[str] = [
    "subscore_energia",
    "subscore_clima",
    "subscore_conectividad",
    "subscore_fiscal",
    "subscore_talento_riesgo",
    "subscore_tier_readiness",
]

ARCHETYPE_DEFINITIONS: Dict[str, Dict[str, str]] = {
    "hub_metropolitano": {
        "cluster_nombre": "Hub Metropolitano & Conectividad Core",
        "cluster_descripcion": "Máxima conectividad troncal, cercanía a cables submarinos (Las Toninas), IXPs de alto tráfico y densidad de talento IT/software. Clima templado y moderado consumo energético.",
    },
    "polo_austral": {
        "cluster_nombre": "Polo Austral & Free-Cooling Extremo",
        "cluster_descripcion": "Condiciones climáticas de frío extremo ideales para free-cooling natural continuo (PUE < 1.15). Menor densidad de conectividad y restricción de red eléctrica en áreas aisladas.",
    },
    "corredor_energetico": {
        "cluster_nombre": "Corredor Productivo & Energético SADI/Renovable",
        "cluster_descripcion": "Fuerte adhesión a regímenes de incentivo (RIGI), matriz de potencia eléctrica instalada diversificada (hidro/térmica/renovable) y equilibrio entre conectividad y territorio.",
    },
    "brecha_infraestructura": {
        "cluster_nombre": "Brecha Fiscal e Infraestructura Rezagada",
        "cluster_descripcion": "Baja cobertura de incentivos fiscales específicos (no adhesión al RIGI o alícuotas elevadas), temperaturas estivales elevadas y menor capilaridad de fibra óptica.",
    },
}


def evaluate_k_range(
    df: pd.DataFrame,
    features: List[str] = FEATURE_COLUMNS,
    k_range: range = range(3, 7),
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Evalúa la calidad del agrupamiento para distintos valores de k
    utilizando Silhouette Score e Inercia.
    """
    X = df[features].values
    results = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels)
        inertia = km.inertia_
        results.append({
            "k": k,
            "silhouette_score": round(float(sil), 4),
            "inercia": round(float(inertia), 2),
        })

    return pd.DataFrame(results)


def fit_archetypes_kmeans(
    df: pd.DataFrame,
    n_clusters: int = 4,
    features: List[str] = FEATURE_COLUMNS,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, KMeans]:
    """
    Entrena K-Means para k=4 y asigna nombres de arquetipo unívocos
    e interpretables basados en las propiedades diagnósticas de los centroides.
    """
    X = df[features].values
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(X)

    centroids_df = pd.DataFrame(km.cluster_centers_, columns=features)
    centroids_df["raw_cluster_id"] = centroids_df.index

    # Mapeo semántico determinístico basado en reglas de negocio sobre los centroides
    cluster_mapping: Dict[int, str] = {}
    for idx, row in centroids_df.iterrows():
        if row["subscore_clima"] > 70.0:
            cluster_mapping[idx] = "polo_austral"
        elif row["subscore_conectividad"] > 70.0:
            cluster_mapping[idx] = "hub_metropolitano"
        elif row["subscore_fiscal"] < 30.0:
            cluster_mapping[idx] = "brecha_infraestructura"
        else:
            cluster_mapping[idx] = "corredor_energetico"

    if len(set(cluster_mapping.values())) != n_clusters:
        raise ValueError(f"Conflicto en la asignación semántica de clusters: {cluster_mapping}")

    # Asignar metadata a los resultados
    df_out = df.copy()
    df_out["raw_cluster_id"] = labels
    df_out["cluster_key"] = df_out["raw_cluster_id"].map(cluster_mapping)
    df_out["cluster_nombre"] = df_out["cluster_key"].map(lambda k: ARCHETYPE_DEFINITIONS[k]["cluster_nombre"])
    df_out["cluster_descripcion"] = df_out["cluster_key"].map(lambda k: ARCHETYPE_DEFINITIONS[k]["cluster_descripcion"])

    # ID de cluster ordenado de 1 a 4 por coherencia ejecutiva
    cluster_order = {
        "hub_metropolitano": 1,
        "polo_austral": 2,
        "corredor_energetico": 3,
        "brecha_infraestructura": 4,
    }
    df_out["cluster_id"] = df_out["cluster_key"].map(cluster_order).astype(int)

    # DataFrame con resumen de centroides
    centroids_summary = centroids_df.copy()
    centroids_summary["cluster_key"] = centroids_summary["raw_cluster_id"].map(cluster_mapping)
    centroids_summary["cluster_id"] = centroids_summary["cluster_key"].map(cluster_order).astype(int)
    centroids_summary["cluster_nombre"] = centroids_summary["cluster_key"].map(lambda k: ARCHETYPE_DEFINITIONS[k]["cluster_nombre"])
    centroids_summary = centroids_summary.sort_values("cluster_id").reset_index(drop=True)

    return df_out, centroids_summary, km


def run_clustering_pipeline(
    input_path: str = "data/04_outputs/scores_mcda_perfiles.parquet",
    output_dir: str = "data/04_outputs",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta el pipeline de clustering, evaluación y persistencia.
    """
    in_file = Path(input_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_file.exists():
        raise FileNotFoundError(f"Archivo de scores no encontrado: {in_file}")

    df_scores = pd.read_parquet(in_file)

    # 1. Evaluación k en [3, 6]
    metrics_k = evaluate_k_range(df_scores)

    # 2. Fit k=4
    df_clustered, centroids_summary, _ = fit_archetypes_kmeans(df_scores, n_clusters=4)

    # 3. Exportar resultados
    parquet_path = out_dir / "clusters_arquetipos.parquet"
    csv_path = out_dir / "clusters_arquetipos.csv"

    # Seleccionar columnas clave para la exportación de arquetipos
    cols_to_export = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "jurisdiccion_corta",
        "region_argentina",
        "cluster_id",
        "cluster_nombre",
        "cluster_descripcion",
        "subscore_energia",
        "subscore_clima",
        "subscore_conectividad",
        "subscore_fiscal",
        "subscore_talento_riesgo",
        "subscore_tier_readiness",
        "score_campus_ia_training",
        "rank_campus_ia_training",
        "score_nodo_inferencia_edge",
        "rank_nodo_inferencia_edge",
        "score_benchmark_cabase",
        "rank_benchmark_cabase",
    ]

    df_export = df_clustered[cols_to_export].copy()
    df_export.to_parquet(parquet_path, engine="pyarrow", compression="snappy", index=False)
    df_export.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return df_export, centroids_summary, metrics_k


if __name__ == "__main__":
    df_res, centroids, metrics = run_clustering_pipeline()
    print("=== EVALUACIÓN DE HIPERPARÁMETRO K ===")
    print(metrics.to_string(index=False))
    print("\n=== CENTROIDES DE ARQUETIPOS (k=4) ===")
    print(centroids[["cluster_id", "cluster_nombre", "subscore_energia", "subscore_clima", "subscore_conectividad", "subscore_fiscal", "subscore_talento_riesgo"]].to_string(index=False))
    print("\n=== DISTRIBUCIÓN POR ARQUETIPO ===")
    print(df_res.groupby(["cluster_id", "cluster_nombre"])["jurisdiccion_corta"].apply(list).to_string())
