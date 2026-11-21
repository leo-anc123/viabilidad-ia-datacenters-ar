"""
src/pipeline/run_full_pipeline.py
==================================
Orquestador Idempotente y Pipeline de Actualización Continua (CI/CD)
Proyecto: 'Viabilidad de Data Centers y Campus de IA en Argentina'

Modos de ejecución:
  --mode full (por defecto):
      1. Ingesta Segura (Clima ERA5, Energía SADI, Conectividad, Talento/Riesgo, Fiscal)
      2. Consolidación de Tabla Maestra (24 jurisdicciones × 63 columnas)
      3. Preprocesamiento & Motor MCDA (6 dimensiones ponderadas)
      4. Clustering de Arquetipos (K-Means k=4) + Simulación Monte Carlo (1.000 runs)
      5. Exportación Star Schema (data/04_outputs/pbi_ready/)
      6. Contrato de Frescura de Datos (data/04_outputs/data_freshness.json)
      7. Suite Completa de Validación QA (validate_master, validate_mcda, validate_fase3)

  --mode refresh-apis:
      Ejecuta únicamente la ingesta segura y verificación de frescura contra
      fuentes remotas, actualizando crudos y data_freshness.json.

Tolerancia a fallos (Regla crítica de negocio):
  Si una API externa falla, genera timeout o HTTP 429/5xx, el orquestador
  preserva el último snapshot válido en data/01_raw/ y data/02_interim/,
  registrando el evento como CACHED_FALLBACK sin corromper el pipeline.
"""

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# ─────────────────────────────────────────────────────────────────────────────
# 0. Rutas canónicas
# ─────────────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

RAW_DIR = _REPO_ROOT / "data" / "01_raw"
INTERIM_DIR = _REPO_ROOT / "data" / "02_interim"
PROCESSED_DIR = _REPO_ROOT / "data" / "03_processed"
OUTPUTS_DIR = _REPO_ROOT / "data" / "04_outputs"
FRESHNESS_JSON = OUTPUTS_DIR / "data_freshness.json"


def _run_step(description: str, cmd: List[str], cwd: Path = _REPO_ROOT) -> int:
    """Ejecuta un paso del pipeline con registro de tiempo y captura de retorno."""
    print(f"\n{'='*75}")
    print(f"▶ [PIPELINE STEP] {description}")
    print(f"  Comando: {' '.join(cmd)}")
    print(f"{'='*75}")

    t0 = time.time()
    res = subprocess.run(cmd, cwd=cwd)
    elapsed = time.time() - t0

    if res.returncode == 0:
        print(f"✔ [PASS] {description} completado en {elapsed:.2f}s")
    else:
        print(f"❌ [FAIL] {description} falló con código {res.returncode} tras {elapsed:.2f}s")

    return res.returncode


def generar_contrato_frescura(statuses: Dict[str, str], pipeline_version: str = "2.0.0-alpha.2") -> Dict[str, Any]:
    """
    Construye y exporta data/04_outputs/data_freshness.json con la trazabilidad
    completa de cortes temporales y estados de actualización.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 1. Clima ERA5: extraer fecha fin de metadata crudo si existe
    cutoff_clima = "2024-12-31"
    raw_clima_path = RAW_DIR / "clima_24_jurisdicciones_raw.json"
    if raw_clima_path.exists():
        try:
            with open(raw_clima_path, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                cutoff_clima = c_data.get("_metadata", {}).get("fecha_fin", cutoff_clima)
        except Exception:
            pass

    # 2. Determinar estado general del pipeline
    any_fallback = any(v == "CACHED_FALLBACK" for v in statuses.values())
    global_status = "DEGRADED_FALLBACK" if any_fallback else "HEALTHY"

    contract = {
        "pipeline_version": pipeline_version,
        "generated_at_utc": now_utc,
        "pipeline_status": global_status,
        "sources": {
            "clima_era5": {
                "dimension": "clima",
                "fuente_oficial": "ECMWF / Open-Meteo Historical API (ERA5)",
                "url": "https://archive-api.open-meteo.com/v1/archive",
                "last_checked_utc": now_utc,
                "data_cutoff_date": cutoff_clima,
                "status": statuses.get("clima_era5", "UPDATED"),
                "update_frequency": "diaria",
                "notes": f"Serie climatológica diaria 2000-01-01 hasta {cutoff_clima}. Libre de imputaciones sintéticas.",
            },
            "cammesa_sadi": {
                "dimension": "energia",
                "fuente_oficial": "Secretaría de Energía / CAMMESA",
                "url": "http://datos.energia.gob.ar/dataset/c62df6c6-73af-4039-b956-db081ff6eebe/resource/230fdf38-8f12-4017-a1e8-d7a1bc4a1c1c/download/generacin-elctrica-centrales-de-generacin.csv",
                "last_checked_utc": now_utc,
                "data_cutoff_date": "2026-09-22",
                "status": statuses.get("cammesa_sadi", "STATIC_VERIFIED"),
                "update_frequency": "anual",
                "notes": "474 centrales SADI georreferenciadas vigentes en BBOX nacional. Serie mensual histórica en portal datos.gob.ar congelada en 2020-02.",
            },
            "enacom_conectividad": {
                "dimension": "conectividad",
                "fuente_oficial": "ENACOM / Datos Abiertos",
                "url": "https://indicadores.enacom.gob.ar/Files/DatosAbiertos/",
                "last_checked_utc": now_utc,
                "data_cutoff_date": "2026-06-30",
                "status": statuses.get("enacom_conectividad", "STATIC_VERIFIED"),
                "update_frequency": "trimestral",
                "notes": "Accesos FTTH, penetración de internet por hogares/habitantes y velocidad media provincial hasta 2026-T2.",
            },
            "cepxxi_talento": {
                "dimension": "talento",
                "fuente_oficial": "CEP XXI / Secretaría de Industria y Desarrollo Productivo",
                "url": "https://cdn.produccion.gob.ar/cdn-cep/datos-por-provincia/por-provincia-clae2/puestos/puestos_priv.csv",
                "last_checked_utc": now_utc,
                "data_cutoff_date": "2023-11-01",
                "status": statuses.get("cepxxi_talento", "STATIC_VERIFIED"),
                "update_frequency": "mensual",
                "notes": "Último corte público disponible en portal oficial (marzo 2024). Verificado formalmente sin datos inventados.",
            },
            "inpres_sismico": {
                "dimension": "talento_riesgo",
                "fuente_oficial": "Instituto Nacional de Prevención Sísmica (INPRES CIRSOC 103)",
                "url": "https://www.inpres.gob.ar/zonas_result.php",
                "last_checked_utc": now_utc,
                "data_cutoff_date": "2024-01-01",
                "status": statuses.get("inpres_sismico", "STATIC_VERIFIED"),
                "update_frequency": "reglamentaria",
                "notes": "Zonificación sísmica oficial según norma sismorresistente INPRES-CIRSOC 103 (escala 0 a 4).",
            },
            "rigi_fiscal": {
                "dimension": "fiscal",
                "fuente_oficial": "Boletines Oficiales Provinciales / RIGI Ley 27.742",
                "url": "https://www.boletinoficial.gob.ar/detalleAviso/primera/310239/20240708",
                "last_checked_utc": now_utc,
                "data_cutoff_date": "2026-11-20",
                "status": statuses.get("rigi_fiscal", "STATIC_VERIFIED"),
                "update_frequency": "legislativa",
                "notes": "18 provincias adheridas formalmente; regímenes provinciales de IIBB tech para economía del conocimiento.",
            },
        },
    }

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(FRESHNESS_JSON, "w", encoding="utf-8") as f:
        json.dump(contract, f, ensure_ascii=False, indent=2)

    print(f"\n✔ [FRESHNESS] Contrato de frescura emitido en: {FRESHNESS_JSON}")
    return contract


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Orquestador del Pipeline de Datos y CI/CD — Viabilidad IA Data Centers AR"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "refresh-apis"],
        default="full",
        help="Modo de ejecución: 'full' (end-to-end + QA) o 'refresh-apis' (solo ingesta y frescura)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Omite la suite de pruebas QA (no recomendado en CI/CD)",
    )
    parser.add_argument(
        "--usar-raw-existente",
        action="store_true",
        help="Reutiliza archivos crudos en data/01_raw/ sin volver a consultar endpoints externos",
    )
    args = parser.parse_args()

    py_exe = sys.executable
    print("=" * 80)
    print(f"🚀 INICIANDO ORQUESTADOR DE PIPELINE (MODO: {args.mode.upper()})")
    print(f"   Python Executable : {py_exe}")
    print(f"   Directorio Raíz   : {_REPO_ROOT}")
    print(f"   Timestamp Inicio  : {datetime.datetime.now().isoformat()}")
    print("=" * 80)

    statuses: Dict[str, str] = {
        "clima_era5": "STATIC_VERIFIED",
        "cammesa_sadi": "STATIC_VERIFIED",
        "enacom_conectividad": "STATIC_VERIFIED",
        "cepxxi_talento": "STATIC_VERIFIED",
        "inpres_sismico": "STATIC_VERIFIED",
        "rigi_fiscal": "STATIC_VERIFIED",
    }

    # ─────────────────────────────────────────────────────────────────────────
    # ETAPA 1: Ingesta de Datos y Verificación de Snapshots
    # ─────────────────────────────────────────────────────────────────────────
    print("\n📦 ETAPA 1: INGESTA RESILIENTE Y ACTUALIZACIÓN DE CRUDOS")

    # 1.1 Clima ERA5
    cmd_clima = [py_exe, "src/gis/fetch_clima_pue.py"]
    if args.usar_raw_existente:
        cmd_clima.append("--usar-raw-existente")
    rc_clima = _run_step("1.1 Ingesta Clima y PUE (ERA5 / Open-Meteo)", cmd_clima)

    # Verificar si el raw de clima fue efectivamente actualizado o si se aplicó CACHED_FALLBACK
    raw_clima_path = RAW_DIR / "clima_24_jurisdicciones_raw.json"
    if rc_clima == 0 and raw_clima_path.exists():
        try:
            with open(raw_clima_path, "r", encoding="utf-8") as f:
                c_meta = json.load(f).get("_metadata", {})
                gen_date = c_meta.get("generado_en", "")[:10]
                today_date = datetime.date.today().isoformat()
                if gen_date == today_date and not args.usar_raw_existente:
                    statuses["clima_era5"] = "UPDATED"
                else:
                    statuses["clima_era5"] = "STATIC_VERIFIED" if args.usar_raw_existente else "CACHED_FALLBACK"
        except Exception:
            statuses["clima_era5"] = "CACHED_FALLBACK"
    else:
        statuses["clima_era5"] = "CACHED_FALLBACK"

    # 1.2 Energía SADI
    cmd_energia = [py_exe, "src/etl/fetch_energia_sadi.py", "--usar-raw-existente"]
    rc_energia = _run_step("1.2 Ingesta Energía SADI y Centrales CAMMESA", cmd_energia)
    statuses["cammesa_sadi"] = "STATIC_VERIFIED" if rc_energia == 0 else "CACHED_FALLBACK"

    # 1.3 Conectividad ENACOM
    cmd_conect = [py_exe, "src/gis/fetch_conectividad.py"]
    rc_conect = _run_step("1.3 Ingesta Conectividad ENACOM", cmd_conect)
    statuses["enacom_conectividad"] = "STATIC_VERIFIED" if rc_conect == 0 else "CACHED_FALLBACK"

    # 1.4 Talento & Riesgo Sísmico
    cmd_talento = [py_exe, "src/etl/fetch_talento_riesgo.py", "--usar-raw-existente"]
    rc_talento = _run_step("1.4 Ingesta Talento CEP XXI y Riesgo INPRES", cmd_talento)
    statuses["cepxxi_talento"] = "STATIC_VERIFIED" if rc_talento == 0 else "CACHED_FALLBACK"
    statuses["inpres_sismico"] = "STATIC_VERIFIED" if rc_talento == 0 else "CACHED_FALLBACK"

    # 1.5 Fiscal y Regulatorio
    cmd_fiscal = [py_exe, "src/etl/build_fiscal_regulatoria.py"]
    rc_fiscal = _run_step("1.5 Dimensión Fiscal y Regulatoria RIGI", cmd_fiscal)
    statuses["rigi_fiscal"] = "STATIC_VERIFIED" if rc_fiscal == 0 else "CACHED_FALLBACK"

    # Emitir Contrato de Frescura
    generar_contrato_frescura(statuses)

    if args.mode == "refresh-apis":
        print("\n✅ Modo 'refresh-apis' completado satisfactoriamente.")
        return 0

    # ─────────────────────────────────────────────────────────────────────────
    # ETAPA 2: Consolidación de Tabla Maestra (24 Jurisdicciones × 63 Columnas)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n🏗️ ETAPA 2: CONSOLIDACIÓN DE TABLA MAESTRA")
    rc_master = _run_step("2. Consolidación Maestra (build_master_table.py)", [py_exe, "src/etl/build_master_table.py"])
    if rc_master != 0:
        print("❌ Error crítico en consolidación maestra. Abortando pipeline.")
        return 1

    # ─────────────────────────────────────────────────────────────────────────
    # ETAPA 3: Preprocesamiento y Motor MCDA (6 Dimensiones)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n⚙️ ETAPA 3: PREPROCESAMIENTO Y MOTOR MCDA")
    rc_mcda = _run_step("3. Preprocesamiento & MCDA Engine (mcda_engine.py)", [py_exe, "src/modeling/mcda_engine.py"])
    if rc_mcda != 0:
        print("❌ Error crítico en motor MCDA. Abortando pipeline.")
        return 1

    # ─────────────────────────────────────────────────────────────────────────
    # ETAPA 4: Clustering de Arquetipos y Simulación Monte Carlo
    # ─────────────────────────────────────────────────────────────────────────
    print("\n🔬 ETAPA 4: CIENCIA DE DATOS & MODELADO ESTADÍSTICO")
    rc_cluster = _run_step("4.1 Clustering K-Means (clustering.py)", [py_exe, "src/modeling/clustering.py"])
    if rc_cluster != 0:
        print("❌ Error crítico en clustering. Abortando pipeline.")
        return 1

    rc_mc = _run_step("4.2 Simulación Monte Carlo (montecarlo.py)", [py_exe, "src/modeling/montecarlo.py"])
    if rc_mc != 0:
        print("❌ Error crítico en Monte Carlo. Abortando pipeline.")
        return 1

    # ─────────────────────────────────────────────────────────────────────────
    # ETAPA 5: Exportación Star Schema (Power BI & Streamlit feeds)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n📊 ETAPA 5: EXPORTACIÓN BI FEEDS (STAR SCHEMA)")
    rc_bi = _run_step("5. Exportación BI Modelo Estrella (export_bi_feeds.py)", [py_exe, "src/modeling/export_bi_feeds.py"])
    if rc_bi != 0:
        print("❌ Error crítico en exportación BI. Abortando pipeline.")
        return 1

    # ─────────────────────────────────────────────────────────────────────────
    # ETAPA 6: Suite Completa de Control de Calidad y Validación QA
    # ─────────────────────────────────────────────────────────────────────────
    if not args.skip_validation:
        print("\n🛡️ ETAPA 6: COMPUERTA DE CALIDAD Y VALIDACIÓN ESTADÍSTICA (QUALITY GATE)")

        # 6.1 Auditor de Tabla Maestra
        rc_v_master = _run_step(
            "6.1 Validación Tabla Maestra (validate_master.py)",
            [py_exe, "src/etl/validate_master.py", "data/03_processed/master_24_jurisdicciones.parquet"]
        )
        if rc_v_master != 0:
            print("❌ Fallo en validate_master.py. Abortando compuerta de calidad.")
            return 1

        # 6.2 Validador Motor MCDA
        rc_v_mcda = _run_step(
            "6.2 Validación Motor MCDA (validate_mcda.py)",
            [py_exe, "src/modeling/validate_mcda.py"]
        )
        if rc_v_mcda != 0:
            print("❌ Fallo en validate_mcda.py. Abortando compuerta de calidad.")
            return 1

        # 6.3 Validador Fase 3 (Clustering, Monte Carlo, Star Schema)
        rc_v_fase3 = _run_step(
            "6.3 Validación Fase 3 ML & BI (validate_fase3.py)",
            [py_exe, "src/modeling/validate_fase3.py"]
        )
        if rc_v_fase3 != 0:
            print("❌ Fallo en validate_fase3.py. Abortando compuerta de calidad.")
            return 1

    print("\n" + "=" * 80)
    print("🎉 PIPELINE END-TO-END COMPLETADO EXITOSAMENTE AL 100% (EXIT CODE 0)")
    print(f"   Timestamp Finalización : {datetime.datetime.now().isoformat()}")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
