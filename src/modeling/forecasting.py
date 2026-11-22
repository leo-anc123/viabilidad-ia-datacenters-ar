"""
Motor de Análisis Predictivo Prospectivo y Modelado de Escenarios (2026–2036)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina (Fase 3 — Bloque 2C)

Responsabilidades:
1. Proyectar la viabilidad de las 24 jurisdicciones en 7 puntos temporales:
   - 2026 (Base)
   - 2028 (+2 años, corto plazo)
   - 2030 (+4 años)
   - 2031 (+5 años, medio plazo)
   - 2032 (+6 años)
   - 2034 (+8 años)
   - 2036 (+10 años, largo plazo)
2. Evaluar 3 escenarios estructurales:
   - Acelerado (Inversión RIGI, Desregulación & Expansión Renovable)
   - Tendencial (Inercial / Histórico)
   - Conservador (Restricciones & Brechas de Infraestructura)
3. Reglas estrictas de rigor físico y cero datos inventados:
   - Expansión energética anclada en proyectos reales de minem_renovar_mater_raw.csv (1.852,7 MW en construcción).
   - Restricción física de Tierra del Fuego: 0.0 MW SADI salvo microrred off-grid documentada en Acelerado (>= 2031).
   - Deterioro térmico de PUE basado en pendientes empíricas observadas en Open-Meteo ERA5 (2000–2023), con PUE >= 1.10.
   - Conectividad y FTTH modeladas con curvas logísticas de saturación (sigmoides) acotadas a L <= 100%.
   - Normalización de indicadores fijada rígidamente a los límites del año base 2026 (Fixed Base Scaling).
   - Reutilización directa del cálculo multicriterio de src/modeling/mcda_engine.py (cero duplicación de fórmulas).
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import json
import unicodedata
import numpy as np
import pandas as pd
from scipy.stats import linregress

# Asegurar importación robusta
_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from src.modeling.preprocessing import FEATURE_CONFIG, ANCHOR_COLUMNS
from src.modeling.mcda_engine import (
    calculate_dimensional_subscores,
    calculate_composite_score,
    INTRA_DIMENSION_WEIGHTS,
    SUBSCORE_COLUMNS,
)

# Horizontes temporales analizados
FORECAST_YEARS: List[int] = [2026, 2028, 2030, 2031, 2032, 2034, 2036]

HORIZONTE_LABELS: Dict[int, str] = {
    2026: "Base (2026)",
    2028: "Corto Plazo (+2a)",
    2030: "Intermedio (+4a)",
    2031: "Medio Plazo (+5a)",
    2032: "Intermedio (+6a)",
    2034: "Intermedio (+8a)",
    2036: "Largo Plazo (+10a)",
}

# Configuración de Escenarios
SCENARIOS: Dict[str, Dict[str, Any]] = {
    "acelerado": {
        "nombre": "Acelerado (Inversión RIGI & Expansión)",
        "g_sadi_macro": 0.035,        # +3.5% anual de expansión SADI de fondo
        "lambda_clima": 0.85,         # Mitigación / enfriamiento avanzado
        "k_ftth": 0.25,               # Tasa de adopción logística rápida FTTH
        "ftth_asymptote_boost": 15.0, # Techo provincial ampliado
        "speed_growth": 0.14,         # +14% anual en Mbps
        "speed_ceiling": 1000.0,      # Techo velocidad 1 Gbps
        "puestos_growth": 0.05,       # +5% anual en puestos software
        "iibb_reduction": 0.04,       # Reducción anual de alícuota IIBB
        "promocion_boost": 2.5,       # Incremento anual índice de promoción
    },
    "tendencial": {
        "nombre": "Tendencial (Inercial / Histórico)",
        "g_sadi_macro": 0.015,        # +1.5% anual expansión SADI
        "lambda_clima": 1.00,         # Pendiente histórica ERA5 observada pura
        "k_ftth": 0.15,               # Tasa de adopción logística inercial
        "ftth_asymptote_boost": 8.0,  # Techo provincial moderado
        "speed_growth": 0.08,         # +8% anual en Mbps
        "speed_ceiling": 500.0,       # Techo velocidad 500 Mbps
        "puestos_growth": 0.02,       # +2% anual en puestos software
        "iibb_reduction": 0.00,       # Alícuotas IIBB estables
        "promocion_boost": 0.0,       # Sin cambios en promoción
    },
    "conservador": {
        "nombre": "Conservador (Restricciones & Brechas)",
        "g_sadi_macro": 0.005,        # +0.5% anual expansión SADI
        "lambda_clima": 1.25,         # Mayor estrés térmico / sin mitigación
        "k_ftth": 0.07,               # Adopción logística lenta
        "ftth_asymptote_boost": 0.0,  # Techo limitado a saturación baja
        "speed_growth": 0.03,         # +3% anual en Mbps
        "speed_ceiling": 250.0,       # Techo velocidad 250 Mbps
        "puestos_growth": 0.00,       # Estancamiento empleo software
        "iibb_reduction": -0.01,      # Ligero aumento de alícuotas efectivas
        "promocion_boost": -0.5,      # Deterioro leve incentivos
    },
}

# Factores de avance para proyectos en construcción según escenario y año
CONSTRUCCION_PROGRESS: Dict[str, Dict[int, float]] = {
    "acelerado":   {2026: 0.0, 2028: 1.0, 2030: 1.0, 2031: 1.0, 2032: 1.0, 2034: 1.0, 2036: 1.0},
    "tendencial":  {2026: 0.0, 2028: 0.6, 2030: 0.9, 2031: 1.0, 2032: 1.0, 2034: 1.0, 2036: 1.0},
    "conservador": {2026: 0.0, 2028: 0.3, 2030: 0.5, 2031: 0.6, 2032: 0.65, 2034: 0.7, 2036: 0.75},
}

# Factores de avance para proyectos no iniciados según escenario y año
NO_INICIADO_PROGRESS: Dict[str, Dict[int, float]] = {
    "acelerado":   {2026: 0.0, 2028: 0.3, 2030: 0.6, 2031: 0.8, 2032: 0.9, 2034: 1.0, 2036: 1.0},
    "tendencial":  {2026: 0.0, 2028: 0.0, 2030: 0.15, 2031: 0.25, 2032: 0.3, 2034: 0.35, 2036: 0.4},
    "conservador": {2026: 0.0, 2028: 0.0, 2030: 0.0, 2031: 0.0, 2032: 0.0, 2034: 0.05, 2036: 0.1},
}

# Supuesto explícito documentado de microrred off-grid para Data Centers en Tierra del Fuego (MW)
TDF_OFFGRID_MW: Dict[str, Dict[int, float]] = {
    "acelerado":   {2026: 0.0, 2028: 0.0, 2030: 0.0, 2031: 50.0, 2032: 75.0, 2034: 100.0, 2036: 150.0},
    "tendencial":  {2026: 0.0, 2028: 0.0, 2030: 0.0, 2031: 0.0, 2032: 0.0, 2034: 0.0, 2036: 0.0},
    "conservador": {2026: 0.0, 2028: 0.0, 2030: 0.0, 2031: 0.0, 2032: 0.0, 2034: 0.0, 2036: 0.0},
}


def _norm_str(txt: str) -> str:
    """Normaliza texto eliminando acentos, espacios y convirtiendo a mayúsculas."""
    if not isinstance(txt, str):
        return ""
    nfkd = unicodedata.normalize("NFD", txt.upper().strip())
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def load_climate_trends(
    clima_json_path: Path = _pkg_root / "data" / "01_raw" / "clima_24_jurisdicciones_raw.json",
) -> Dict[str, float]:
    """
    Calcula la pendiente empírica de calentamiento anual (°C/año) para cada una
    de las 24 jurisdicciones a partir de la serie diaria 2000-2023 de ERA5.
    Aplica cota inferior de 0.00 °C/año para evitar supuestos no conservadores.
    """
    if not clima_json_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de clima en: {clima_json_path}")

    with open(clima_json_path, "r", encoding="utf-8") as f:
        clima_data = json.load(f)

    slopes: Dict[str, float] = {}
    juris_dict = clima_data.get("jurisdicciones", {})

    for jid, data in juris_dict.items():
        daily = data.get("daily", {})
        if "time" in daily and "temperature_2m_mean" in daily:
            times = pd.to_datetime(daily["time"])
            means = np.array(daily["temperature_2m_mean"], dtype=float)
            df_temp = pd.DataFrame({"year": times.year, "temp": means})
            annual_mean = df_temp.groupby("year")["temp"].mean()
            res = linregress(annual_mean.index, annual_mean.values)
            # Acotado inferiormente a 0.0
            slopes[jid] = max(0.0, float(res.slope))
        else:
            slopes[jid] = 0.0406  # Media nacional como fallback

    return slopes


def load_renovar_pipeline(
    renovar_csv_path: Path = _pkg_root / "data" / "01_raw" / "minem_renovar_mater_raw.csv",
    master_path: Path = _pkg_root / "data" / "03_processed" / "master_24_jurisdicciones.parquet",
) -> Dict[str, Dict[str, float]]:
    """
    Agrupa los proyectos RenovAr / MATER con potencia registrada por provincia y estado.
    Retorna diccionario: {jurisdiccion_id: {'construccion_mw': float, 'no_iniciado_mw': float}}
    """
    from src.modeling.export_bi_feeds import CAMMESA_PROVINCIA_TO_ID

    cammesa_map = {_norm_str(k): v for k, v in CAMMESA_PROVINCIA_TO_ID.items()}
    cammesa_map["TIERRA DEL FUEGO"] = "94"
    cammesa_map["CABA"] = "02"
    cammesa_map["CIUDAD AUTONOMA DE BUENOS AIRES"] = "02"

    df_master = pd.read_parquet(master_path)
    pipeline_by_id: Dict[str, Dict[str, float]] = {
        jid: {"construccion_mw": 0.0, "no_iniciado_mw": 0.0} for jid in df_master["jurisdiccion_id"]
    }

    if not renovar_csv_path.exists():
        return pipeline_by_id

    df_ren = pd.read_csv(renovar_csv_path)
    valid_ren = df_ren.dropna(subset=["potencia_mw", "estado"]).copy()

    for _, row in valid_ren.iterrows():
        p_norm = _norm_str(str(row["provincia"]))
        jid = cammesa_map.get(p_norm)
        if jid and jid in pipeline_by_id:
            mw = float(row["potencia_mw"])
            est = str(row["estado"]).strip().lower()
            if "construc" in est:
                pipeline_by_id[jid]["construccion_mw"] += mw
            elif "no iniciado" in est:
                pipeline_by_id[jid]["no_iniciado_mw"] += mw

    return pipeline_by_id


def compute_fixed_base_limits(df_master: pd.DataFrame) -> Dict[str, Tuple[float, float]]:
    """
    Calcula los límites fijos empíricos (min, max) del año base 2026 para cada feature.
    Esto garantiza el 'Fixed Base Scaling' para medir progreso real intertemporal.
    """
    limits: Dict[str, Tuple[float, float]] = {}

    for f_cfg in FEATURE_CONFIG:
        src_col = f_cfg["source_col"]
        vals = df_master[src_col].astype(float).copy()
        if f_cfg["transform"] == "log1p":
            vals = np.log1p(vals)
        min_v = float(vals.min())
        max_v = float(vals.max())
        if abs(max_v - min_v) < 1e-12:
            max_v = min_v + 1.0
        limits[src_col] = (min_v, max_v)

    return limits


def scale_features_fixed_base(
    df_features: pd.DataFrame,
    fixed_limits: Dict[str, Tuple[float, float]],
) -> pd.DataFrame:
    """
    Normaliza el conjunto de features usando los límites fijos del año base 2026,
    recortando rígidamente a [0.0, 100.0].
    """
    df_norm = df_features[ANCHOR_COLUMNS].copy()

    for f_cfg in FEATURE_CONFIG:
        src_col = f_cfg["source_col"]
        norm_col = f_cfg["norm_col"]
        direction = f_cfg["direction"]
        transform = f_cfg["transform"]

        vals = df_features[src_col].astype(float).copy()
        if transform == "log1p":
            vals = np.log1p(vals)

        min_v, max_v = fixed_limits[src_col]

        if direction == "maximize":
            norm_series = (vals - min_v) / (max_v - min_v) * 100.0
        else:
            norm_series = (max_v - vals) / (max_v - min_v) * 100.0

        df_norm[norm_col] = norm_series.clip(lower=0.0, upper=100.0).round(4)

    return df_norm


def project_jurisdiction_features(
    df_base: pd.DataFrame,
    year: int,
    scenario_id: str,
    climate_slopes: Dict[str, float],
    renovar_pipeline: Dict[str, Dict[str, float]],
) -> pd.DataFrame:
    """
    Proyecta las 16 features operativas primarias de las 24 jurisdicciones
    para un año y escenario específicos.
    En year == 2026, devuelve idénticamente el DataFrame base sin modificaciones.
    """
    if year == 2026:
        return df_base.copy()

    delta_t = year - 2026
    scen_cfg = SCENARIOS[scenario_id]
    df_proj = df_base.copy()

    # Asegurar tipos flotantes para evitar advertencias de pandas en asignación
    numeric_cols_to_float = [
        "sadi_potencia_instalada_mw", "sadi_pct_renovable", "n_centrales_sadi",
        "sadi_diversidad_tech", "pue_climatologico_estimado", "temp_max_verano_prom_c",
        "fibra_optica_pct", "penetracion_hogares_pct", "velocidad_media_bajada_mbps",
        "rigi_adhesion", "iibb_alicuota_tech_pct", "indice_promocion_fiscal",
        "puestos_software_clae62", "densidad_stem_it_score"
    ]
    for c in numeric_cols_to_float:
        if c in df_proj.columns:
            df_proj[c] = df_proj[c].astype(float)

    for idx, row in df_proj.iterrows():
        jid = row["jurisdiccion_id"]

        # -------------------------------------------------------------
        # 1. Dimensión Energía
        # -------------------------------------------------------------
        p_base = float(row["sadi_potencia_instalada_mw"])
        pct_renov_base = float(row["sadi_pct_renovable"])
        n_cent_base = float(row["n_centrales_sadi"])
        div_tech_base = float(row["sadi_diversidad_tech"])

        if jid == "94":  # Tierra del Fuego (restricción física estricta)
            # Solo en escenario acelerado y >= 2031 se suma microrred off-grid documentada
            offgrid_mw = TDF_OFFGRID_MW[scenario_id].get(year, 0.0)
            p_proj = offgrid_mw
            pct_renov_proj = 100.0 if offgrid_mw > 0 else 0.0
            n_cent_proj = n_cent_base + (2.0 if offgrid_mw > 0 else 0.0)
            div_tech_proj = div_tech_base + (1.0 if offgrid_mw > 0 else 0.0)
        else:
            # Macro expansión SADI de fondo
            p_macro = p_base * ((1.0 + scen_cfg["g_sadi_macro"]) ** delta_t)

            # Aporte de cartera real RenovAr / MATER
            pipe = renovar_pipeline.get(jid, {"construccion_mw": 0.0, "no_iniciado_mw": 0.0})
            f_const = CONSTRUCCION_PROGRESS[scenario_id].get(year, 1.0)
            f_no_ini = NO_INICIADO_PROGRESS[scenario_id].get(year, 0.0)
            p_renovar = (pipe["construccion_mw"] * f_const) + (pipe["no_iniciado_mw"] * f_no_ini)

            p_proj = p_macro + p_renovar

            # Renovables: aumento proporcional al aporte renovable
            delta_renov_pts = (p_renovar / max(p_proj, 1.0)) * 50.0
            pct_renov_proj = min(100.0, pct_renov_base + delta_renov_pts)

            # Centrales y diversidad técnica (Tier-Readiness)
            nuevas_cent = (pipe["construccion_mw"] > 0) * (1.0 if delta_t >= 2 else 0.0) + (p_renovar > 50) * 1.0
            n_cent_proj = n_cent_base + nuevas_cent
            div_tech_proj = min(6.0, div_tech_base + (1.0 if p_renovar > 10.0 and div_tech_base < 4.0 else 0.0))

        df_proj.at[idx, "sadi_potencia_instalada_mw"] = round(p_proj, 2)
        df_proj.at[idx, "sadi_pct_renovable"] = round(pct_renov_proj, 2)
        df_proj.at[idx, "n_centrales_sadi"] = round(n_cent_proj, 1)
        df_proj.at[idx, "sadi_diversidad_tech"] = round(div_tech_proj, 1)

        # -------------------------------------------------------------
        # 2. Dimensión Clima / PUE
        # -------------------------------------------------------------
        beta_clim = climate_slopes.get(jid, 0.0406)
        delta_temp = beta_clim * delta_t * scen_cfg["lambda_clima"]

        pue_base = float(row["pue_climatologico_estimado"])
        tmax_base = float(row["temp_max_verano_prom_c"])

        # Deterioro térmico del PUE (~0.0045 por grado de incremento)
        delta_pue = delta_temp * 0.0045
        pue_proj = min(1.58, max(1.10, pue_base + delta_pue))
        tmax_proj = tmax_base + delta_temp

        df_proj.at[idx, "pue_climatologico_estimado"] = round(pue_proj, 4)
        df_proj.at[idx, "temp_max_verano_prom_c"] = round(tmax_proj, 2)

        # -------------------------------------------------------------
        # 3. Dimensión Conectividad (Curvas Logísticas)
        # -------------------------------------------------------------
        ftth_base = float(row["fibra_optica_pct"])
        pen_base = float(row["penetracion_hogares_pct"])
        speed_base = float(row["velocidad_media_bajada_mbps"])

        # Curva logística de saturación para FTTH
        l_ftth = min(100.0, max(ftth_base + scen_cfg["ftth_asymptote_boost"], 80.0))
        if ftth_base > 0 and ftth_base < l_ftth:
            k = scen_cfg["k_ftth"]
            denom = 1.0 + ((l_ftth - ftth_base) / ftth_base) * np.exp(-k * delta_t)
            ftth_proj = min(100.0, l_ftth / denom)
        else:
            ftth_proj = ftth_base

        # Penetración hogares (logística hacia techo 95%)
        l_pen = min(98.0, max(pen_base + 10.0, 85.0))
        if pen_base > 0 and pen_base < l_pen:
            k_p = scen_cfg["k_ftth"] * 0.8
            denom_p = 1.0 + ((l_pen - pen_base) / pen_base) * np.exp(-k_p * delta_t)
            pen_proj = min(100.0, l_pen / denom_p)
        else:
            pen_proj = pen_base

        # Velocidad de bajada (crecimiento compuesto hacia techo tecnológico)
        speed_proj = min(
            scen_cfg["speed_ceiling"],
            speed_base * ((1.0 + scen_cfg["speed_growth"]) ** delta_t)
        )

        df_proj.at[idx, "fibra_optica_pct"] = round(ftth_proj, 2)
        df_proj.at[idx, "penetracion_hogares_pct"] = round(pen_proj, 2)
        df_proj.at[idx, "velocidad_media_bajada_mbps"] = round(speed_proj, 2)

        # -------------------------------------------------------------
        # 4. Dimensión Fiscal y Regulatoria
        # -------------------------------------------------------------
        rigi_base = float(row["rigi_adhesion"])
        iibb_base = float(row["iibb_alicuota_tech_pct"])
        prom_base = float(row["indice_promocion_fiscal"])

        if scenario_id == "acelerado":
            # Adhesión progresiva de jurisdicciones remanentes
            if rigi_base == 0.0:
                if jid in ["02", "82"] and year >= 2028:  # CABA, Santa Fe
                    rigi_proj = 1.0
                elif jid == "06" and year >= 2030:       # Buenos Aires
                    rigi_proj = 1.0
                elif year >= 2031:                       # Resto
                    rigi_proj = 1.0
                else:
                    rigi_proj = 0.0
            else:
                rigi_proj = 1.0
            iibb_proj = max(0.5, iibb_base - (scen_cfg["iibb_reduction"] * delta_t))
            prom_proj = min(100.0, prom_base + (scen_cfg["promocion_boost"] * delta_t))
        elif scenario_id == "tendencial":
            rigi_proj = rigi_base
            iibb_proj = iibb_base
            prom_proj = prom_base
        else:  # conservador
            rigi_proj = rigi_base
            iibb_proj = min(5.0, iibb_base + 0.05 * delta_t)
            prom_proj = max(0.0, prom_base - 0.2 * delta_t)

        df_proj.at[idx, "rigi_adhesion"] = rigi_proj
        df_proj.at[idx, "iibb_alicuota_tech_pct"] = round(iibb_proj, 2)
        df_proj.at[idx, "indice_promocion_fiscal"] = round(prom_proj, 2)

        # -------------------------------------------------------------
        # 5. Dimensión Talento STEM y Riesgo Sísmico
        # -------------------------------------------------------------
        # Riesgo sísmico es invariante físico
        puestos_base = float(row["puestos_software_clae62"])
        dens_stem_base = float(row["densidad_stem_it_score"])

        puestos_proj = puestos_base * ((1.0 + scen_cfg["puestos_growth"]) ** delta_t)
        dens_stem_proj = min(100.0, dens_stem_base * ((1.0 + (scen_cfg["puestos_growth"] * 0.7)) ** delta_t))

        df_proj.at[idx, "puestos_software_clae62"] = round(puestos_proj, 1)
        df_proj.at[idx, "densidad_stem_it_score"] = round(dens_stem_proj, 2)

    return df_proj


def generate_all_forecasts(
    master_path: str = "data/03_processed/master_24_jurisdicciones.parquet",
    config_path: str = "config/weights_profiles.json",
    clima_path: str = "data/01_raw/clima_24_jurisdicciones_raw.json",
    renovar_path: str = "data/01_raw/minem_renovar_mater_raw.csv",
) -> pd.DataFrame:
    """
    Orquesta la generación completa de proyecciones para:
    24 jurisdicciones × 7 años × 3 escenarios = 504 combinaciones.
    Reutiliza directamente calculate_composite_score de mcda_engine.py.
    """
    df_master = pd.read_parquet(master_path)
    with open(config_path, "r", encoding="utf-8") as f:
        profiles_config = json.load(f)

    # 1. Cargar fuentes auxiliares y límites fijos del año base 2026
    climate_slopes = load_climate_trends(Path(clima_path))
    renovar_pipe = load_renovar_pipeline(Path(renovar_path), Path(master_path))
    fixed_limits = compute_fixed_base_limits(df_master)

    # Extraer pesos de los 3 perfiles oficiales
    profiles = {k: {dim: v for dim, v in data.items() if not dim.startswith("_")}
                for k, data in profiles_config.items() if not k.startswith("_")}

    # Almacenar primero los scores del año base 2026 para cálculo exacto de deltas
    base_scores_2026: Dict[str, Dict[str, float]] = {}  # {jid: {profile: score_2026}}
    base_ranks_2026: Dict[str, Dict[str, int]] = {}    # {jid: {profile: rank_2026}}

    # Pre-evaluación del año base
    df_norm_base = scale_features_fixed_base(df_master, fixed_limits)
    df_sub_base = calculate_dimensional_subscores(df_norm_base)
    for p_id, p_weights in profiles.items():
        s_base = calculate_composite_score(df_sub_base, p_weights)
        r_base = s_base.rank(ascending=False, method="min").astype(int)
        for i, jid in enumerate(df_master["jurisdiccion_id"]):
            if jid not in base_scores_2026:
                base_scores_2026[jid] = {}
                base_ranks_2026[jid] = {}
            base_scores_2026[jid][p_id] = float(s_base.iloc[i])
            base_ranks_2026[jid][p_id] = int(r_base.iloc[i])

    rows: List[Dict[str, Any]] = []

    for year in FORECAST_YEARS:
        for scen_id, scen_meta in SCENARIOS.items():
            # Proyectar features primarias de las 24 jurisdicciones
            df_proj_feat = project_jurisdiction_features(
                df_base=df_master,
                year=year,
                scenario_id=scen_id,
                climate_slopes=climate_slopes,
                renovar_pipeline=renovar_pipe,
            )

            # Normalizar con límites fijos de 2026
            df_norm = scale_features_fixed_base(df_proj_feat, fixed_limits)

            # Calcular sub-scores dimensionales
            df_sub = calculate_dimensional_subscores(df_norm)

            # Evaluar los 3 perfiles oficiales con MCDA Engine
            prof_scores: Dict[str, pd.Series] = {}
            prof_ranks: Dict[str, pd.Series] = {}
            for p_id, p_weights in profiles.items():
                s_series = calculate_composite_score(df_sub, p_weights)
                prof_scores[p_id] = s_series.round(4)
                prof_ranks[p_id] = s_series.rank(ascending=False, method="min").astype(int)

            # Construir registros
            for i, r in df_master.iterrows():
                jid = r["jurisdiccion_id"]
                row_dict: Dict[str, Any] = {
                    "jurisdiccion_id": jid,
                    "jurisdiccion_nombre": r["jurisdiccion_nombre"],
                    "jurisdiccion_corta": r["jurisdiccion_corta"],
                    "region_argentina": r["region_argentina"],
                    "anio": int(year),
                    "horizonte": HORIZONTE_LABELS[year],
                    "escenario_id": scen_id,
                    "escenario_nombre": scen_meta["nombre"],
                }

                # Subscores
                for sub_col in SUBSCORE_COLUMNS:
                    row_dict[sub_col] = float(df_sub.loc[i, sub_col])

                # Perfiles, scores, rankings y deltas vs 2026
                for p_id in profiles.keys():
                    cur_score = float(prof_scores[p_id].iloc[i])
                    cur_rank = int(prof_ranks[p_id].iloc[i])
                    b_score = base_scores_2026[jid][p_id]
                    b_rank = base_ranks_2026[jid][p_id]

                    row_dict[f"score_{p_id}"] = cur_score
                    row_dict[f"rank_{p_id}"] = cur_rank
                    if year == 2026:
                        row_dict[f"delta_score_{p_id}"] = 0.0
                        row_dict[f"delta_rank_{p_id}"] = 0
                    else:
                        row_dict[f"delta_score_{p_id}"] = round(cur_score - b_score, 4)
                        # Delta rank positivo significa ganancia de puestos hacia el #1
                        row_dict[f"delta_rank_{p_id}"] = int(b_rank - cur_rank)

                rows.append(row_dict)

    df_out = pd.DataFrame(rows)
    return df_out


def run_forecasting_pipeline(
    master_path: str = "data/03_processed/master_24_jurisdicciones.parquet",
    config_path: str = "config/weights_profiles.json",
    clima_path: str = "data/01_raw/clima_24_jurisdicciones_raw.json",
    renovar_path: str = "data/01_raw/minem_renovar_mater_raw.csv",
    output_dir: str = "data/04_outputs",
) -> pd.DataFrame:
    """
    Punto de entrada de ejecución del motor prospectivo.
    Exporta proyecciones_2026_2036.parquet y proyecciones_2026_2036.csv.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Iniciando generación de proyecciones prospectivas 2026–2036...")
    df_forecast = generate_all_forecasts(
        master_path=master_path,
        config_path=config_path,
        clima_path=clima_path,
        renovar_path=renovar_path,
    )

    parquet_path = out_dir / "proyecciones_2026_2036.parquet"
    csv_path = out_dir / "proyecciones_2026_2036.csv"

    df_forecast.to_parquet(parquet_path, engine="pyarrow", compression="snappy", index=False)
    df_forecast.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"✔ Proyecciones exportadas exitosamente a:")
    print(f"  - {parquet_path}")
    print(f"  - {csv_path}")
    print(f"Dimensiones: {df_forecast.shape[0]} filas × {df_forecast.shape[1]} columnas.")

    return df_forecast


if __name__ == "__main__":
    df_res = run_forecasting_pipeline()
