"""
src/pipeline/export_web_payload.py
==================================
Consolidador del Contrato de Datos Unificado para la Aplicación Web
Proyecto: 'Viabilidad de Data Centers y Campus de IA en Argentina' (v2.0.0)

Genera:
    web/public/data/ivid_payload.json

Consolida:
    1. Metadatos de frescura y trazabilidad oficial (data_freshness.json).
    2. Pesos y configuración de perfiles multicriterio (weights_profiles.json).
    3. 24 jurisdicciones con sus 6 sub-scores auditados normalizados (0-100).
    4. Perfiles MCDA (Campus IA, Nodos Edge, Benchmark) con scores, rankings y simulación Monte Carlo.
    5. Arquetipos territoriales (K-Means k=4) con descripciones ejecutivas.
    6. 474 centrales SADI georreferenciadas con normalización de tecnologías para filtros.
    7. Series temporales de proyecciones 2026-2036 por escenario y horizonte.
    8. KPIs analíticos agregados para Vista 01 Dashboard.
"""

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
PBI_DIR = _REPO_ROOT / "data" / "04_outputs" / "pbi_ready"
OUTPUTS_DIR = _REPO_ROOT / "data" / "04_outputs"
CONFIG_DIR = _REPO_ROOT / "config"
TARGET_JSON = _REPO_ROOT / "web" / "public" / "data" / "ivid_payload.json"

DIMENSION_METADATA = [
    {
        "id": "subscore_energia",
        "key": "dimension_energia",
        "codigo": "01",
        "nombre": "Energía",
        "nombre_largo": "Energía y Potencia SADI",
        "descripcion": "Disponibilidad de potencia en barras SADI, proximidad a nodos y generación renovable.",
        "icono": "Zap"
    },
    {
        "id": "subscore_clima",
        "key": "dimension_clima",
        "codigo": "02",
        "nombre": "Clima",
        "nombre_largo": "Clima y Eficiencia PUE",
        "descripcion": "Horas anuales de free cooling térmico, bajo PUE y menor demanda de refrigeración.",
        "icono": "Thermometer"
    },
    {
        "id": "subscore_conectividad",
        "key": "dimension_conectividad",
        "codigo": "03",
        "nombre": "Conectividad",
        "nombre_largo": "Conectividad y Red Troncal",
        "descripcion": "Latencia a cables submarinos (Las Toninas), capilaridad FTTH y enlaces troncales.",
        "icono": "Network"
    },
    {
        "id": "subscore_fiscal",
        "key": "dimension_fiscal",
        "codigo": "04",
        "nombre": "Fiscal / RIGI",
        "nombre_largo": "Marco Fiscal y Adhesión RIGI",
        "descripcion": "Adhesión formal al RIGI (Ley 27.742), exenciones y estabilidad de IIBB tecnológico.",
        "icono": "Scale"
    },
    {
        "id": "subscore_talento_riesgo",
        "key": "dimension_talento_riesgo",
        "codigo": "05",
        "nombre": "Talento / Riesgo",
        "nombre_largo": "Talento STEM y Seguridad Sísmica",
        "descripcion": "Disponibilidad de empleo formal TIC/software y seguridad ante zonificación sísmica INPRES.",
        "icono": "ShieldCheck"
    },
    {
        "id": "subscore_tier_readiness",
        "key": "dimension_tier_readiness",
        "codigo": "06",
        "nombre": "Tier-Readiness",
        "nombre_largo": "Aptitud Territorial Tier",
        "descripcion": "Redundancia de acometidas eléctricas, resiliencia hídrica y aptitud física del suelo.",
        "icono": "Server"
    }
]

TECNOLOGIA_FILTRO_MAP = {
    "Térmica": "Térmica",
    "Biogas": "Bioenergía",
    "Biomasa": "Bioenergía",
    "Nuclear": "Nuclear",
    "Fotovoltaica": "Solar",
    "Eólica": "Eólica",
    "Hidroeléctrica": "Hidroeléctrica",
    "Hidroeléctrica (Menor a 50 Mw)": "Hidroeléctrica"
}


def sanitize_val(val: Any) -> Any:
    """Evita NaN o infinitos en el JSON final."""
    if isinstance(val, (float, int)):
        if math.isnan(val) or math.isinf(val):
            return None
        return round(float(val), 2) if isinstance(val, float) else val
    return val


def build_payload() -> Dict[str, Any]:
    print("▶ Cargando datasets auditados...")

    # 1. Freshness contract
    freshness_path = OUTPUTS_DIR / "data_freshness.json"
    freshness_data = {}
    if freshness_path.exists():
        with open(freshness_path, "r", encoding="utf-8") as f:
            freshness_data = json.load(f)

    # 2. Weights profiles
    weights_path = CONFIG_DIR / "weights_profiles.json"
    weights_data = {}
    if weights_path.exists():
        with open(weights_path, "r", encoding="utf-8") as f:
            weights_data = json.load(f)

    # 3. CSVs
    df_dim = pd.read_csv(PBI_DIR / "dim_jurisdicciones.csv")
    df_scores = pd.read_csv(PBI_DIR / "fact_scores_perfiles.csv")
    df_subscores = pd.read_csv(PBI_DIR / "fact_subscores_radar.csv")
    df_centrales = pd.read_csv(PBI_DIR / "geo_centrales_sadi.csv")
    df_proyecciones = pd.read_csv(PBI_DIR / "fact_proyecciones_2026_2036.csv")

    print(f"✔ Cargadas {len(df_dim)} jurisdicciones, {len(df_scores)} scores por perfil, {len(df_centrales)} centrales.")

    # A. Mapeo de subscores por jurisdiccion_id
    subscores_by_jid: Dict[int, Dict[str, float]] = {}
    for _, row in df_subscores.iterrows():
        jid = int(row["jurisdiccion_id"])
        dim_id = str(row["dimension_id"])
        val = sanitize_val(row["subscore_valor"])
        if jid not in subscores_by_jid:
            subscores_by_jid[jid] = {}
        subscores_by_jid[jid][dim_id] = val

    # B. Mapeo de scores por jurisdiccion_id y perfil_id
    scores_by_jid: Dict[int, Dict[str, Dict[str, Any]]] = {}
    for _, row in df_scores.iterrows():
        jid = int(row["jurisdiccion_id"])
        pid = str(row["perfil_id"])
        if jid not in scores_by_jid:
            scores_by_jid[jid] = {}
        scores_by_jid[jid][pid] = {
            "score_base": sanitize_val(row["score_base"]),
            "rank_base": int(row["rank_base"]),
            "mc_score_mean": sanitize_val(row["mc_score_mean"]),
            "mc_score_std": sanitize_val(row["mc_score_std"]),
            "mc_score_p5": sanitize_val(row["mc_score_p5"]),
            "mc_score_p95": sanitize_val(row["mc_score_p95"]),
            "mc_rank_median": sanitize_val(row["mc_rank_median"]),
            "prob_top3_pct": sanitize_val(row["prob_top3_pct"]),
            "prob_top5_pct": sanitize_val(row["prob_top5_pct"]),
        }

    # C. Lista estructurada de 24 jurisdicciones
    jurisdicciones_list: List[Dict[str, Any]] = []
    for _, row in df_dim.iterrows():
        jid = int(row["jurisdiccion_id"])
        j_subscores = subscores_by_jid.get(jid, {})
        j_scores = scores_by_jid.get(jid, {})

        jurisdicciones_list.append({
            "id": jid,
            "nombre": str(row["jurisdiccion_nombre"]),
            "corta": str(row["jurisdiccion_corta"]),
            "region": str(row["region_argentina"]),
            "lat": sanitize_val(row["lat_capital"]),
            "lon": sanitize_val(row["lon_capital"]),
            "cluster": {
                "id": int(row["cluster_id"]),
                "nombre": str(row["cluster_nombre"]),
                "descripcion": str(row["cluster_descripcion"])
            },
            "subscores": j_subscores,
            "scores_perfiles": j_scores
        })

    # D. Centrales SADI normalizadas
    centrales_list: List[Dict[str, Any]] = []
    for _, row in df_centrales.iterrows():
        raw_tec = str(row.get("tecnologia_etiqueta", row.get("tecnologia", "Térmica")))
        filtro_tec = TECNOLOGIA_FILTRO_MAP.get(raw_tec, "Térmica")
        centrales_list.append({
            "id": int(row["central_id"]),
            "nombre": str(row["nombre"]),
            "codigo_central": str(row.get("central", "")),
            "jurisdiccion_id": int(row["jurisdiccion_id"]),
            "jurisdiccion_nombre": str(row["jurisdiccion_nombre"]),
            "tecnologia_original": raw_tec,
            "categoria_filtro": filtro_tec,
            "potencia_mw": sanitize_val(row["potencia_instalada_mw"]),
            "lat": sanitize_val(row["latitud"]),
            "lon": sanitize_val(row["longitud"])
        })

    # E. Proyecciones estructuradas por [perfil_id][jurisdiccion_id][escenario_id]
    proyecciones_dict: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]] = {}
    for _, row in df_proyecciones.iterrows():
        pid = str(row["perfil_id"])
        jid = str(int(row["jurisdiccion_id"]))
        esc = str(row["escenario_id"])

        if pid not in proyecciones_dict:
            proyecciones_dict[pid] = {}
        if jid not in proyecciones_dict[pid]:
            proyecciones_dict[pid][jid] = {}
        if esc not in proyecciones_dict[pid][jid]:
            proyecciones_dict[pid][jid][esc] = []

        proyecciones_dict[pid][jid][esc].append({
            "anio": int(row["anio"]),
            "horizonte": str(row["horizonte"]),
            "score": sanitize_val(row["score_proyectado"]),
            "rank": int(row["rank_proyectado"]),
            "delta_score_vs_2026": sanitize_val(row["delta_score_vs_2026"]),
            "delta_rank_vs_2026": int(row["delta_rank_vs_2026"])
        })

    # F. KPIs Analíticos y Lectura del Territorio por perfil
    perfiles_kpis: Dict[str, Any] = {}
    perfiles_ids = ["campus_ia_training", "nodo_inferencia_edge", "benchmark_cabase"]

    for pid in perfiles_ids:
        # Encontrar provincia líder
        sub_scores_pid = [
            (j["id"], j["nombre"], j["scores_perfiles"].get(pid, {}).get("score_base", 0), j["subscores"])
            for j in jurisdicciones_list
        ]
        sub_scores_pid.sort(key=lambda x: x[2], reverse=True)
        top1 = sub_scores_pid[0]
        top1_jid, top1_nombre, top1_score, top1_sub = top1

        # Max Energía
        max_energia = max(jurisdicciones_list, key=lambda j: j["subscores"].get("subscore_energia", 0))
        # Max Conectividad
        max_conec = max(jurisdicciones_list, key=lambda j: j["subscores"].get("subscore_conectividad", 0))

        # Lectura territorial dinámica
        if pid == "campus_ia_training":
            lectura_titulo = "La energía abre la oportunidad."
            lectura_cuerpo = f"{top1_nombre} alcanza {int(round(top1_score))} puntos en este escenario, impulsada por su alta disponibilidad energética renovable, bajas temperaturas para free cooling y adhesión fiscal favorable."
            lectura_equilibrio = "El equilibrio importa: las provincias patagónicas y de Cuyo ofrecen óptimas condiciones térmicas y de potencia, requiriendo complementariedad en redundancia y redes de transporte."
        elif pid == "nodo_inferencia_edge":
            lectura_titulo = "La latencia define la cercanía."
            lectura_cuerpo = f"{top1_nombre} lidera con {int(round(top1_score))} puntos gracias a la proximidad crítica al cable submarino de Las Toninas, máxima densidad de fibra troncal y concentración de talento IT especializado."
            lectura_equilibrio = "Los nodos edge demandan respuestas en milisegundos: Buenos Aires y Córdoba compensan costos térmicos con su infraestructura digital y ecosistema tecnológico."
        else:
            lectura_titulo = "Una visión neutral y balanceada."
            lectura_cuerpo = f"{top1_nombre} encabeza el índice de referencia con {int(round(top1_score))} puntos bajo ponderaciones uniformes de las 6 dimensiones auditadas."
            lectura_equilibrio = "El benchmark sectorial permite contrastar objetivamente el impacto que produce priorizar energía vs. conectividad en el territorio argentino."

        perfiles_kpis[pid] = {
            "provincias_evaluadas": 24,
            "top1_id": top1_jid,
            "top1_nombre": top1_nombre,
            "top1_score": top1_score,
            "max_energia_provincia": max_energia["nombre"],
            "max_energia_score": max_energia["subscores"].get("subscore_energia"),
            "max_conectividad_provincia": max_conec["nombre"],
            "max_conectividad_score": max_conec["subscores"].get("subscore_conectividad"),
            "dimensiones_count": 6,
            "lectura_editorial": {
                "titulo": lectura_titulo,
                "cuerpo": lectura_cuerpo,
                "equilibrio": lectura_equilibrio
            }
        }

    payload = {
        "_version": "2.0.0",
        "generated_at_utc": freshness_data.get("generated_at_utc", "2026-11-21T00:00:00Z"),
        "freshness": freshness_data,
        "dimensiones": DIMENSION_METADATA,
        "perfiles_config": weights_data,
        "kpis_por_perfil": perfiles_kpis,
        "jurisdicciones": jurisdicciones_list,
        "centrales_sadi": centrales_list,
        "proyecciones": proyecciones_dict
    }

    return payload


def main() -> int:
    try:
        payload = build_payload()
        TARGET_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(TARGET_JSON, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        file_size_kb = TARGET_JSON.stat().st_size / 1024
        print(f"\n✔ Payload generado exitosamente en: {TARGET_JSON}")
        print(f"  Tamaño: {file_size_kb:.1f} KB")
        print(f"  Jurisdicciones: {len(payload['jurisdicciones'])}")
        print(f"  Centrales SADI: {len(payload['centrales_sadi'])}")
        print(f"  Dimensiones auditadas: {len(payload['dimensiones'])}")
        return 0
    except Exception as e:
        print(f"\n❌ Error al generar ivid_payload.json: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
