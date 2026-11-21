"""
Generador de Feeds para Business Intelligence y Streamlit (Fase 3 — Bloque 3.2)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

Responsabilidades:
1. Construir el Modelo Estrella en data/04_outputs/pbi_ready/ en formato CSV con BOM (UTF-8-SIG):
   a) dim_jurisdicciones.csv:
      - Clave primaria jurisdiccion_id, nombres, región, lat/lon capital y arquetipo de cluster.
   b) fact_scores_perfiles.csv:
      - Tabla de hechos en formato largo con scores determinísticos, rankings y métricas de estabilidad Monte Carlo.
   c) fact_subscores_radar.csv:
      - Tabla de hechos en formato largo con los 5 sub-scores dimensionales para visualización radar.
   d) geo_centrales_sadi.csv:
      - Capa geoespacial limpia de las 474 centrales de generación SADI (CAMMESA) con coordenadas válidas EPSG:4326,
        potencia instalada MW, tecnología y asociación a jurisdiccion_id.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
import pandas as pd
import numpy as np

_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from src.modeling.mcda_engine import ANCHOR_COLUMNS, SUBSCORE_COLUMNS

# Mapeo de nombres de dimensión para visualización ejecutiva en gráficos de radar
DIMENSION_DISPLAY_NAMES: Dict[str, str] = {
    "subscore_energia": "Energía y Potencia SADI",
    "subscore_clima": "Clima y Eficiencia PUE",
    "subscore_conectividad": "Conectividad y Red Troncal",
    "subscore_fiscal": "Marco Fiscal y RIGI",
    "subscore_talento_riesgo": "Talento STEM y Seguridad Sísmica",
    "subscore_tier_readiness": "Aptitud Territorial Tier (Tier-Readiness)",
}

# Mapeo de provincias de CAMMESA a códigos INDEC estándar de 2 dígitos
CAMMESA_PROVINCIA_TO_ID: Dict[str, str] = {
    "BUENOS AIRES": "06",
    "CATAMARCA": "10",
    "CHACO": "22",
    "CHUBUT": "26",
    "CIUDAD AUTONOMA DE BUENOS": "02",
    "CORDOBA": "14",
    "CORRIENTES": "18",
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
}

# Bounding box oficial de territorio continental e insular argentino (EPSG:4326)
ARGENTINA_BBOX = {
    "min_lat": -56.0,
    "max_lat": -21.0,
    "min_lon": -74.0,
    "max_lon": -53.0,
}


def build_dim_jurisdicciones(
    scores_path: Path,
    clusters_path: Path,
) -> pd.DataFrame:
    """
    Construye la tabla de dimensión de jurisdicciones con coordenadas de capital
    y arquetipo de cluster asignado.
    """
    df_scores = pd.read_parquet(scores_path)
    df_clusters = pd.read_parquet(clusters_path)

    # Merge de metadata y arquetipo
    cluster_cols = ["jurisdiccion_id", "cluster_id", "cluster_nombre", "cluster_descripcion"]
    dim = pd.merge(
        df_scores[ANCHOR_COLUMNS],
        df_clusters[cluster_cols],
        on="jurisdiccion_id",
        how="left",
    )

    ordered_cols = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "jurisdiccion_corta",
        "region_argentina",
        "lat_capital",
        "lon_capital",
        "cluster_id",
        "cluster_nombre",
        "cluster_descripcion",
    ]
    return dim[ordered_cols].sort_values("jurisdiccion_id").reset_index(drop=True)


def build_fact_scores_perfiles(
    scores_path: Path,
    montecarlo_path: Path,
    config_path: Path,
) -> pd.DataFrame:
    """
    Construye la tabla de hechos consolidada con scores determinísticos y métricas de Monte Carlo
    en formato largo.
    """
    df_scores = pd.read_parquet(scores_path)
    df_mc = pd.read_parquet(montecarlo_path)
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    records = []
    # 1. Perfiles analizados en Monte Carlo (A y B)
    mc_profiles = df_mc["perfil_id"].unique().tolist()
    for profile_id in mc_profiles:
        df_p_mc = df_mc[df_mc["perfil_id"] == profile_id].copy()
        records.append(df_p_mc)

    # 2. Perfil Benchmark CABASE (deterministico)
    if "score_benchmark_cabase" in df_scores.columns:
        p_name = cfg.get("benchmark_cabase", {}).get("_nombre", "Perfil C — Benchmark CABASE")
        df_c = df_scores[["jurisdiccion_id", "jurisdiccion_nombre", "jurisdiccion_corta", "region_argentina"]].copy()
        df_c["perfil_id"] = "benchmark_cabase"
        df_c["perfil_nombre"] = p_name
        df_c["score_base"] = df_scores["score_benchmark_cabase"].values
        df_c["rank_base"] = df_scores["rank_benchmark_cabase"].values
        df_c["mc_score_mean"] = df_scores["score_benchmark_cabase"].values
        df_c["mc_score_std"] = 0.0
        df_c["mc_score_p5"] = df_scores["score_benchmark_cabase"].values
        df_c["mc_score_p95"] = df_scores["score_benchmark_cabase"].values
        df_c["mc_rank_median"] = df_scores["rank_benchmark_cabase"].values
        df_c["prob_top3_pct"] = np.where(df_scores["rank_benchmark_cabase"] <= 3, 100.0, 0.0)
        df_c["prob_top5_pct"] = np.where(df_scores["rank_benchmark_cabase"] <= 5, 100.0, 0.0)
        records.append(df_c)

    fact = pd.concat(records, ignore_index=True)
    return fact.sort_values(["perfil_id", "rank_base"]).reset_index(drop=True)


def build_fact_subscores_radar(scores_path: Path) -> pd.DataFrame:
    """
    Construye la tabla de hechos en formato largo de los 5 subscores por jurisdicción.
    """
    df_scores = pd.read_parquet(scores_path)
    id_vars = ["jurisdiccion_id", "jurisdiccion_corta"]

    melted = df_scores.melt(
        id_vars=id_vars,
        value_vars=SUBSCORE_COLUMNS,
        var_name="dimension_id",
        value_name="subscore_valor",
    )

    melted["dimension_nombre"] = melted["dimension_id"].map(DIMENSION_DISPLAY_NAMES)
    melted["subscore_valor"] = melted["subscore_valor"].round(2)

    ordered_cols = ["jurisdiccion_id", "jurisdiccion_corta", "dimension_id", "dimension_nombre", "subscore_valor"]
    return melted[ordered_cols].sort_values(["jurisdiccion_id", "dimension_id"]).reset_index(drop=True)


def build_geo_centrales_sadi(
    raw_cammesa_path: Path,
    dim_jurisdicciones: pd.DataFrame,
) -> pd.DataFrame:
    """
    Limpia, valida coordenadas EPSG:4326 y mapea las centrales de generación SADI
    conforme a las reglas de calidad de datos de AGENTS.md.
    """
    df_raw = pd.read_csv(raw_cammesa_path)

    # Extraer coordenadas de GeoJSON
    coords_lon = []
    coords_lat = []
    for _, row in df_raw.iterrows():
        try:
            gj = json.loads(row["geojson"])
            c = gj["coordinates"]
            coords_lon.append(float(c[0]))
            coords_lat.append(float(c[1]))
        except Exception:
            coords_lon.append(np.nan)
            coords_lat.append(np.nan)

    df_clean = df_raw.copy()
    df_clean["longitud"] = coords_lon
    df_clean["latitud"] = coords_lat

    # Validación estricta de Bounding Box argentino
    in_bbox = (
        df_clean["latitud"].between(ARGENTINA_BBOX["min_lat"], ARGENTINA_BBOX["max_lat"]) &
        df_clean["longitud"].between(ARGENTINA_BBOX["min_lon"], ARGENTINA_BBOX["max_lon"]) &
        (df_clean["latitud"] != 0.0) & (df_clean["longitud"] != 0.0) &
        df_clean["latitud"].notna() & df_clean["longitud"].notna()
    )

    invalid_count = (~in_bbox).sum()
    if invalid_count > 0:
        print(f"ADVERTENCIA: Se detectaron {invalid_count} centrales fuera del bounding box. Filtrando.")
        df_clean = df_clean[in_bbox].copy()

    # Mapeo a jurisdiccion_id
    id_map = CAMMESA_PROVINCIA_TO_ID.copy()
    jurisdiccion_ids = []
    for _, row in df_clean.iterrows():
        prov = str(row["provincia"]).strip().upper() if pd.notna(row["provincia"]) else ""
        nombre = str(row["nombre"]).strip().upper()

        # Caso especial Yacyretá (represa binacional sobre río Paraná, Ituzaingó, Corrientes)
        if "YACYRETA" in nombre and not prov:
            jurisdiccion_ids.append("18")  # Corrientes
        elif prov in id_map:
            jurisdiccion_ids.append(id_map[prov])
        else:
            jurisdiccion_ids.append("NaN")

    df_clean["jurisdiccion_id"] = jurisdiccion_ids

    # Cruzar con dim_jurisdicciones para asegurar nombre normalizado
    id_to_nombre = dict(zip(dim_jurisdicciones["jurisdiccion_id"], dim_jurisdicciones["jurisdiccion_nombre"]))
    df_clean["jurisdiccion_nombre"] = df_clean["jurisdiccion_id"].map(id_to_nombre).fillna("No Asignada")

    # Crear ID secuencial único de central
    df_clean["central_id"] = range(1, len(df_clean) + 1)

    export_cols = [
        "central_id",
        "nombre",
        "central",
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "tecnologia",
        "tecnologia_etiqueta",
        "potencia_instalada_mw",
        "latitud",
        "longitud",
        "fuente",
    ]

    return df_clean[export_cols].reset_index(drop=True)


def export_all_bi_feeds(
    scores_path: str = "data/04_outputs/scores_mcda_perfiles.parquet",
    clusters_path: str = "data/04_outputs/clusters_arquetipos.parquet",
    montecarlo_path: str = "data/04_outputs/montecarlo_sensibilidad.parquet",
    config_path: str = "config/weights_profiles.json",
    raw_cammesa_path: str = "data/01_raw/cammesa_centrales_generacion_sadi_raw.csv",
    output_dir: str = "data/04_outputs/pbi_ready",
) -> Dict[str, pd.DataFrame]:
    """
    Orquesta la generación y exportación del modelo estrella completo en CSV UTF-8-SIG.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scores_p = Path(scores_path)
    clusters_p = Path(clusters_path)
    mc_p = Path(montecarlo_path)
    cfg_p = Path(config_path)
    cammesa_p = Path(raw_cammesa_path)

    # 1. Dimensión Jurisdicciones
    dim_jurisdicciones = build_dim_jurisdicciones(scores_p, clusters_p)
    dim_path = out_dir / "dim_jurisdicciones.csv"
    dim_jurisdicciones.to_csv(dim_path, index=False, encoding="utf-8-sig")

    # 2. Hechos Scores y Monte Carlo
    fact_scores = build_fact_scores_perfiles(scores_p, mc_p, cfg_p)
    fact_scores_path = out_dir / "fact_scores_perfiles.csv"
    fact_scores.to_csv(fact_scores_path, index=False, encoding="utf-8-sig")

    # 3. Hechos Subscores Radar
    fact_radar = build_fact_subscores_radar(scores_p)
    fact_radar_path = out_dir / "fact_subscores_radar.csv"
    fact_radar.to_csv(fact_radar_path, index=False, encoding="utf-8-sig")

    # 4. Capa Geoespacial Centrales SADI
    geo_centrales = build_geo_centrales_sadi(cammesa_p, dim_jurisdicciones)
    geo_path = out_dir / "geo_centrales_sadi.csv"
    geo_centrales.to_csv(geo_path, index=False, encoding="utf-8-sig")

    return {
        "dim_jurisdicciones": dim_jurisdicciones,
        "fact_scores_perfiles": fact_scores,
        "fact_subscores_radar": fact_radar,
        "geo_centrales_sadi": geo_centrales,
    }


if __name__ == "__main__":
    tables = export_all_bi_feeds()
    print("=== MODELO ESTRELLA BI FEEDS GENERADO CON ÉXITO ===")
    for name, df in tables.items():
        print(f"- {name}: {len(df)} filas × {len(df.columns)} columnas.")
    print("\nDetalle de centrales SADI por tecnología principal:")
    print(tables["geo_centrales_sadi"]["tecnologia_etiqueta"].value_counts().to_string())
