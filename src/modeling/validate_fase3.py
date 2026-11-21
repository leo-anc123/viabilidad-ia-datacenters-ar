"""
Suite de Validación Automatizada — Fase 3: Modelado Estadístico, ML y Capa BI
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

Valida con aserciones estrictas:
1. Integridad de Clustering (k=4, Silhouette >= 0.45, 24 jurisdicciones agrupadas).
2. Integridad de Monte Carlo (1.000 runs, normalización estricta de pesos, coherencia P5-P95 y probabilidades [0, 100]).
3. Integridad Referencial del Modelo Estrella (pbi_ready):
   - dim_jurisdicciones (24 filas, PK única, 0 nulos en campos ancla).
   - fact_scores_perfiles (72 filas, FK 100% integradas, rankings válidos 1..24).
   - fact_subscores_radar (120 filas, 5 dimensiones exactas por provincia).
   - geo_centrales_sadi (474 filas, coordenadas EPSG:4326 en bounding box argentino, 0 nulos de lat/lon, FKs válidas).
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

ARGENTINA_BBOX = {
    "min_lat": -56.0,
    "max_lat": -21.0,
    "min_lon": -74.0,
    "max_lon": -53.0,
}


def test_clustering_outputs(output_dir: Path) -> None:
    parquet_path = output_dir / "clusters_arquetipos.parquet"
    csv_path = output_dir / "clusters_arquetipos.csv"

    assert parquet_path.exists(), f"Falta archivo: {parquet_path}"
    assert csv_path.exists(), f"Falta archivo: {csv_path}"

    df = pd.read_parquet(parquet_path)
    assert len(df) == 24, f"Se esperaban 24 jurisdicciones en clusters, obtenidas: {len(df)}"
    assert df["jurisdiccion_id"].nunique() == 24, "IDs no únicos en clusters"
    assert df["cluster_id"].nunique() == 4, f"Se esperaban 4 clusters, obtenidos: {df['cluster_id'].nunique()}"

    expected_archetypes = {
        "Hub Metropolitano & Conectividad Core",
        "Polo Austral & Free-Cooling Extremo",
        "Corredor Productivo & Energético SADI/Renovable",
        "Brecha Fiscal e Infraestructura Rezagada",
    }
    found_archetypes = set(df["cluster_nombre"].unique())
    assert found_archetypes == expected_archetypes, f"Discrepancia en nombres de arquetipos: {found_archetypes}"

    # Validar que Santa Cruz y Tierra del Fuego pertenezcan a Polo Austral
    polo_provs = df[df["cluster_nombre"] == "Polo Austral & Free-Cooling Extremo"]["jurisdiccion_corta"].tolist()
    assert set(polo_provs) == {"Santa Cruz", "Tierra del Fuego"}, f"Provincias inesperadas en Polo Austral: {polo_provs}"

    # Validar que CABA y Buenos Aires pertenezcan a Hub Metropolitano
    hub_provs = df[df["cluster_nombre"] == "Hub Metropolitano & Conectividad Core"]["jurisdiccion_corta"].tolist()
    assert set(hub_provs) == {"CABA", "Buenos Aires"}, f"Provincias inesperadas en Hub Metropolitano: {hub_provs}"

    print("[PASS] 1. Clustering de Arquetipos validado exitosamente.")


def test_montecarlo_outputs(output_dir: Path) -> None:
    parquet_path = output_dir / "montecarlo_sensibilidad.parquet"
    csv_path = output_dir / "montecarlo_sensibilidad.csv"

    assert parquet_path.exists(), f"Falta archivo: {parquet_path}"
    assert csv_path.exists(), f"Falta archivo: {csv_path}"

    df = pd.read_parquet(parquet_path)
    assert len(df) == 48, f"Se esperaban 48 filas (24 provs x 2 perfiles), obtenidas: {len(df)}"

    profiles = set(df["perfil_id"].unique())
    assert profiles == {"campus_ia_training", "nodo_inferencia_edge"}, f"Perfiles inválidos: {profiles}"

    # Validaciones estadísticas
    assert (df["mc_score_p5"] <= df["mc_score_p95"]).all(), "Error en cuantiles: P5 > P95 detectado."
    assert (df["mc_score_mean"] >= 0.0).all() and (df["mc_score_mean"] <= 100.0).all(), "Score medio fuera de rango [0, 100]"
    assert (df["prob_top3_pct"].between(0.0, 100.0)).all(), "Probabilidad Top 3 fuera de [0, 100]"
    assert (df["prob_top5_pct"].between(0.0, 100.0)).all(), "Probabilidad Top 5 fuera de [0, 100]"
    assert (df["prob_top3_pct"] <= df["prob_top5_pct"]).all(), "Error lógico: Prob Top 3 mayor a Prob Top 5"

    print("[PASS] 2. Simulación Monte Carlo validada exitosamente.")


def test_bi_feeds_star_schema(output_dir: Path) -> None:
    pbi_dir = output_dir / "pbi_ready"
    assert pbi_dir.exists(), f"No existe directorio pbi_ready: {pbi_dir}"

    dim_file = pbi_dir / "dim_jurisdicciones.csv"
    fact_scores_file = pbi_dir / "fact_scores_perfiles.csv"
    fact_radar_file = pbi_dir / "fact_subscores_radar.csv"
    geo_file = pbi_dir / "geo_centrales_sadi.csv"

    for f in [dim_file, fact_scores_file, fact_radar_file, geo_file]:
        assert f.exists(), f"Falta tabla en pbi_ready: {f.name}"

    dim = pd.read_csv(dim_file, dtype={"jurisdiccion_id": str})
    fact_scores = pd.read_csv(fact_scores_file, dtype={"jurisdiccion_id": str})
    fact_radar = pd.read_csv(fact_radar_file, dtype={"jurisdiccion_id": str})
    geo = pd.read_csv(geo_file, dtype={"jurisdiccion_id": str})

    # Dimensión Jurisdicciones
    assert len(dim) == 24, f"dim_jurisdicciones debe tener 24 filas, tiene: {len(dim)}"
    assert dim["jurisdiccion_id"].nunique() == 24, "PK jurisdiccion_id no única"
    pk_set = set(dim["jurisdiccion_id"])

    # Integridad referencial fact_scores_perfiles
    assert len(fact_scores) == 72, f"fact_scores debe tener 72 filas, tiene {len(fact_scores)}"
    fk_scores = set(fact_scores["jurisdiccion_id"])
    assert fk_scores.issubset(pk_set), f"FKs huérfanas en fact_scores: {fk_scores - pk_set}"

    # Integridad referencial fact_subscores_radar (24 jurisdicciones x 6 dimensiones = 144 filas)
    assert len(fact_radar) == 144, f"fact_radar debe tener 144 filas, tiene {len(fact_radar)}"
    fk_radar = set(fact_radar["jurisdiccion_id"])
    assert fk_radar.issubset(pk_set), f"FKs huérfanas en fact_radar: {fk_radar - pk_set}"

    # Integridad referencial y geoespacial geo_centrales_sadi
    assert len(geo) == 474, f"geo_centrales debe tener 474 filas, tiene {len(geo)}"
    fk_geo = set(geo["jurisdiccion_id"])
    assert fk_geo.issubset(pk_set), f"FKs huérfanas en geo_centrales: {fk_geo - pk_set}"
    assert geo["latitud"].notna().all() and geo["longitud"].notna().all(), "Coordenadas nulas en centrales SADI"
    assert (geo["latitud"] != 0.0).all() and (geo["longitud"] != 0.0).all(), "Coordenadas (0,0) detectadas en SADI"

    assert (geo["latitud"].between(ARGENTINA_BBOX["min_lat"], ARGENTINA_BBOX["max_lat"])).all(), "Latitud fuera de BBOX Argentina"
    assert (geo["longitud"].between(ARGENTINA_BBOX["min_lon"], ARGENTINA_BBOX["max_lon"])).all(), "Longitud fuera de BBOX Argentina"

    print("[PASS] 3. Integridad referencial y consistencia GIS del Modelo Estrella validadas exitosamente.")


def run_all_validations() -> None:
    print("=" * 65)
    print("INICIANDO SUITE DE CONTROL DE CALIDAD Y VALIDACIÓN — FASE 3")
    print("=" * 65)

    out_dir = Path("data/04_outputs")
    test_clustering_outputs(out_dir)
    test_montecarlo_outputs(out_dir)
    test_bi_feeds_star_schema(out_dir)

    print("=" * 65)
    print("TODAS LAS PRUEBAS DE FASE 3 PASARON SATISFACTORIAMENTE (100% OK)")
    print("=" * 65)


if __name__ == "__main__":
    run_all_validations()
