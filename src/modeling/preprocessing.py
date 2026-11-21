"""
Preprocesamiento Estadístico y Normalización de Features (Fase 3 — Bloque 3.1)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina

Responsabilidades:
1. Aislar las 14 features operativas y completas de las 24 jurisdicciones.
2. Excluir explícitamente las 13 columnas 100% NaN identificadas en Fase 2 sin imputar sintéticos.
3. Mitigar la asimetría extrema mediante transformación logarítmica (log1p).
4. Escalar todas las variables a [0, 100] respetando la dirección de optimización (invertir donde menor es mejor).
5. Manejar rigurosamente el caso físico de Tierra del Fuego (sistema aislado SADI = 0.0 MW).
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd

# Lista explícita de columnas 100% NaN documentadas en Fase 2 (auditoría docs/qa_report_fase2.md)
# Regla innegociable: CERO DATOS INVENTADOS. No imputar ni rellenar sintéticamente.
EXCLUDED_NAN_COLUMNS: List[str] = [
    "sadi_uptime_index",
    "sadi_margen_disponible_mw",
    "proyeccion_potencia_2028_mw",
    "proyeccion_potencia_2036_mw",
    "potencial_offgrid_score",
    "indice_estres_hidrico",
    "fuente_hidrica",
    "ixp_cabase_nodos",
    "fibra_troncal_cobertura_score",
    "iibb_alicuota_energia_pct",
    "graduados_stem_anual",
    "riesgo_climatico_score",
    "riesgo_combinado_score",
]

# Configuración de Features Operativas para el Scoring Multicriterio (MCDA)
# Cada elemento define:
# - source_col: nombre de la columna en master_24_jurisdicciones
# - norm_col: nombre de la feature normalizada resultante [0, 100]
# - dimension: dimensión analítica a la que pertenece
# - transform: 'log1p' para mitigar asimetría extrema o None
# - direction: 'maximize' (↑ mayor es mejor) o 'minimize' (↓ menor es mejor)
# - description: fundamento metodológico
FEATURE_CONFIG: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # Dimensión 1: Energía y Red SADI
    # -------------------------------------------------------------
    {
        "source_col": "sadi_potencia_instalada_mw",
        "norm_col": "norm_potencia_sadi",
        "dimension": "dimension_energia",
        "transform": "log1p",
        "direction": "maximize",
        "description": "Potencia instalada de generación SADI (MW). log1p mitiga el outlier de Buenos Aires (10.2 GW). TDF es 0.0 MW (red aislada).",
    },
    {
        "source_col": "sadi_pct_renovable",
        "norm_col": "norm_pct_renovable",
        "dimension": "dimension_energia",
        "transform": None,
        "direction": "maximize",
        "description": "Porcentaje de generación renovable Ley 27.191 (solar, eólica, biomasa, mini-hidro).",
    },
    # -------------------------------------------------------------
    # Dimensión 2: Clima y Eficiencia PUE
    # -------------------------------------------------------------
    {
        "source_col": "pue_climatologico_estimado",
        "norm_col": "norm_pue_climatologico",
        "dimension": "dimension_clima",
        "transform": None,
        "direction": "minimize",
        "description": "PUE climatológico derivado de horas free-cooling ERA5 (1.10 a 1.58). Menor PUE implica mayor eficiencia.",
    },
    {
        "source_col": "temp_max_verano_prom_c",
        "norm_col": "norm_temp_max_verano",
        "dimension": "dimension_clima",
        "transform": None,
        "direction": "minimize",
        "description": "Temperatura máxima estival promedio (°C, meses DJF). Menor temperatura reduce el pico de estrés de refrigeración.",
    },
    # -------------------------------------------------------------
    # Dimensión 3: Conectividad y Redes
    # -------------------------------------------------------------
    {
        "source_col": "distancia_las_toninas_km",
        "norm_col": "norm_distancia_las_toninas",
        "dimension": "dimension_conectividad",
        "transform": None,
        "direction": "minimize",
        "description": "Distancia geodésica WGS84 al punto de amarre de cables submarinos internacionales. Proxy de latencia mínima.",
    },
    {
        "source_col": "velocidad_media_bajada_mbps",
        "norm_col": "norm_velocidad_bajada",
        "dimension": "dimension_conectividad",
        "transform": None,
        "direction": "maximize",
        "description": "Velocidad media de descarga en internet fijo (Mbps, ENACOM 2026-T2).",
    },
    {
        "source_col": "penetracion_hogares_pct",
        "norm_col": "norm_penetracion_hogares",
        "dimension": "dimension_conectividad",
        "transform": None,
        "direction": "maximize",
        "description": "Penetración de accesos fijos por cada 100 hogares (ENACOM).",
    },
    {
        "source_col": "fibra_optica_pct",
        "norm_col": "norm_fibra_optica_pct",
        "dimension": "dimension_conectividad",
        "transform": None,
        "direction": "maximize",
        "description": "Porcentaje de accesos sobre fibra óptica sobre el total de conexiones fijas (ENACOM).",
    },
    # -------------------------------------------------------------
    # Dimensión 4: Fiscal y Regulatorio
    # -------------------------------------------------------------
    {
        "source_col": "indice_promocion_fiscal",
        "norm_col": "norm_indice_promocion_fiscal",
        "dimension": "dimension_fiscal",
        "transform": None,
        "direction": "maximize",
        "description": "Índice fiscal compuesto (0-10) que combina incentivos a grandes inversiones (RIGI/TDF/RPI) y fomento IIBB tech.",
    },
    {
        "source_col": "rigi_adhesion",
        "norm_col": "norm_rigi_adhesion",
        "dimension": "dimension_fiscal",
        "transform": None,
        "direction": "maximize",
        "description": "Adhesión formal sancionada al RIGI Ley 27.742 (True = 100 pts, False = 0 pts).",
    },
    {
        "source_col": "iibb_alicuota_tech_pct",
        "norm_col": "norm_iibb_alicuota_tech",
        "dimension": "dimension_fiscal",
        "transform": None,
        "direction": "minimize",
        "description": "Alícuota de IIBB sobre software/IT (0.0% promovida a 3.5% general). Menor alícuota impositiva es preferible.",
    },
    # -------------------------------------------------------------
    # Dimensión 5: Capital Humano y Riesgo
    # -------------------------------------------------------------
    {
        "source_col": "densidad_stem_it_score",
        "norm_col": "norm_densidad_stem",
        "dimension": "dimension_talento_riesgo",
        "transform": None,
        "direction": "maximize",
        "description": "Densidad de talento TIC relativo al empleo privado provincial (normalizado 0-10 a CABA).",
    },
    {
        "source_col": "puestos_software_clae62",
        "norm_col": "norm_puestos_software",
        "dimension": "dimension_talento_riesgo",
        "transform": "log1p",
        "direction": "maximize",
        "description": "Masa crítica absoluta de programadores y consultores IT (CLAE 62, CEP XXI). log1p mitiga el outlier de CABA.",
    },
    {
        "source_col": "riesgo_sismico_zona",
        "norm_col": "norm_seguridad_sismica",
        "dimension": "dimension_talento_riesgo",
        "transform": None,
        "direction": "minimize",
        "description": "Zonificación sísmica oficial INPRES CIRSOC 103 (0 a 4). Invertida: Zona 0 = 100 (seguridad máxima), Zona 4 = 0.",
    },
    # -------------------------------------------------------------
    # Dimensión 6: Soporte de Aptitud Territorial Tier (Tier-Readiness)
    # -------------------------------------------------------------
    {
        "source_col": "n_centrales_sadi",
        "norm_col": "norm_n_centrales_sadi",
        "dimension": "dimension_tier_readiness",
        "transform": "log1p",
        "direction": "maximize",
        "description": "Cantidad de nodos y centrales de generación eléctrica SADI. log1p mitiga concentración. TDF = 0.0.",
    },
    {
        "source_col": "sadi_diversidad_tech",
        "norm_col": "norm_sadi_diversidad_tech",
        "dimension": "dimension_tier_readiness",
        "transform": None,
        "direction": "maximize",
        "description": "Cantidad de tecnologías de generación distintas en el territorio provincial para evitar punto único de falla (CAMMESA). TDF = 0.",
    },
]

# Columnas de anclaje territorial que deben preservarse sin alteración
ANCHOR_COLUMNS: List[str] = [
    "jurisdiccion_id",
    "jurisdiccion_nombre",
    "jurisdiccion_corta",
    "region_argentina",
    "lat_capital",
    "lon_capital",
]


def scale_min_max(
    series: pd.Series,
    direction: str = "maximize",
    eps: float = 1e-9,
) -> pd.Series:
    """
    Escala una serie numérica a [0.0, 100.0] según la dirección de optimización.
    - maximize (↑): 100 para el valor máximo, 0 para el valor mínimo.
    - minimize (↓): 100 para el valor mínimo, 0 para el valor máximo.
    """
    val_min = float(series.min())
    val_max = float(series.max())
    diff = val_max - val_min

    if abs(diff) < eps:
        # Si no hay dispersión, otorgar 100.0 uniforme
        return pd.Series(100.0, index=series.index, dtype=float)

    if direction == "maximize":
        scaled = (series - val_min) / diff * 100.0
    elif direction == "minimize":
        scaled = (val_max - series) / diff * 100.0
    else:
        raise ValueError(f"Dirección de optimización no reconocida: {direction}. Debe ser 'maximize' o 'minimize'.")

    # Asegurar cota estricta [0.0, 100.0] frente a redondeos de punto flotante
    return scaled.clip(lower=0.0, upper=100.0)


def preprocess_features(df_master: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Ejecuta el pipeline de preprocesamiento estadístico sobre la tabla maestra.

    Parámetros:
    - df_master: DataFrame con las 24 jurisdicciones oficiales.

    Retorna:
    - df_normalized: DataFrame con columnas de anclaje y las 14 features normalizadas en [0, 100].
    - metadata: Diccionario con estadísticas de transformación, min/max y parámetros de escala.
    """
    # 1. Verificación territorial
    if len(df_master) != 24:
        raise ValueError(f"La tabla de entrada contiene {len(df_master)} registros. Se requieren exactamente 24 jurisdicciones.")

    # 2. Inicializar DataFrame con anclas territoriales
    for col in ANCHOR_COLUMNS:
        if col not in df_master.columns:
            raise KeyError(f"Columna de anclaje obligatoria '{col}' ausente en el DataFrame de entrada.")

    df_input = df_master.copy()
    if "sadi_diversidad_tech" not in df_input.columns:
        from pathlib import Path
        geo_path = Path("data/04_outputs/pbi_ready/geo_centrales_sadi.csv")
        if geo_path.exists():
            geo_df = pd.read_csv(geo_path, dtype={"jurisdiccion_id": str})
            geo_df["jurisdiccion_id"] = geo_df["jurisdiccion_id"].str.zfill(2)
            tech_counts = geo_df.groupby("jurisdiccion_id")["tecnologia"].nunique().to_dict()
        else:
            tech_counts = {}
        df_input["sadi_diversidad_tech"] = df_input["jurisdiccion_id"].map(tech_counts).fillna(0).astype(int)

    df_norm = df_input[ANCHOR_COLUMNS].copy()
    metadata: Dict[str, Any] = {
        "n_jurisdicciones": len(df_input),
        "excluded_nan_columns": EXCLUDED_NAN_COLUMNS,
        "features": {},
    }

    # 3. Iterar y normalizar cada feature configurada
    for cfg in FEATURE_CONFIG:
        src = cfg["source_col"]
        tgt = cfg["norm_col"]
        dim = cfg["dimension"]
        transform = cfg["transform"]
        direction = cfg["direction"]

        if src not in df_input.columns:
            raise KeyError(f"Feature fuente requerida '{src}' ausente en la tabla maestra.")

        # Extraer serie y manejar tipos
        raw_series = df_input[src].copy()

        # Tratamiento especial para booleanos (ej. rigi_adhesion)
        if raw_series.dtype == bool or set(raw_series.dropna().unique()).issubset({True, False, 0, 1}):
            raw_numeric = raw_series.astype(float)
        else:
            raw_numeric = pd.to_numeric(raw_series, errors="raise")

        # Verificar nulos en feature operativa
        n_nulls = raw_numeric.isna().sum()
        if n_nulls > 0:
            raise ValueError(f"Feature operativa '{src}' contiene {n_nulls} valores nulos. Inconsistencia con auditoría Fase 2.")

        # Aplicar transformación funcional previa
        if transform == "log1p":
            # Verificar no-negatividad
            if (raw_numeric < 0).any():
                raise ValueError(f"Feature '{src}' tiene valores negativos no válidos para log1p.")
            transformed = np.log1p(raw_numeric)
        elif transform is None:
            transformed = raw_numeric
        else:
            raise ValueError(f"Transformación no soportada: {transform}")

        # Escalar a [0, 100] con polaridad de optimización
        scaled = scale_min_max(transformed, direction=direction)
        df_norm[tgt] = scaled.round(4)

        # Registrar metadata de trazabilidad
        metadata["features"][tgt] = {
            "source_col": src,
            "dimension": dim,
            "transform": transform,
            "direction": direction,
            "raw_min": float(raw_numeric.min()),
            "raw_max": float(raw_numeric.max()),
            "raw_mean": float(raw_numeric.mean()),
            "norm_min": float(scaled.min()),
            "norm_max": float(scaled.max()),
            "norm_mean": float(scaled.mean()),
        }

    return df_norm, metadata


if __name__ == "__main__":
    import json
    master_path = "data/03_processed/master_24_jurisdicciones.parquet"
    print(f"Cargando {master_path}...")
    df_raw = pd.read_parquet(master_path)
    df_proc, meta = preprocess_features(df_raw)
    print(f"Preprocesamiento exitoso: {df_proc.shape[0]} filas × {df_proc.shape[1]} columnas.")
    print("Columnas generadas:", df_proc.columns.tolist())
    print("\nResumen descriptivo de features normalizadas [0-100]:")
    norm_cols = [c for c in df_proc.columns if c.startswith("norm_")]
    print(df_proc[norm_cols].describe().round(2).T[["mean", "std", "min", "50%", "max"]])
