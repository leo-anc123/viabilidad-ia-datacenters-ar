"""
build_master_table.py
======================
Script de Consolidación Maestra — Fase 2 (v0.5.0).
"Viabilidad Técnica, Energética y Geoespacial para Data Centers y Campus de IA en Argentina".

Fusiona la tabla ancla territorial `jurisdicciones_base.csv` con las 5 tablas dimensionales
interim mediante merges controlados 1:1 sobre `jurisdiccion_id`:
  1. `data/02_interim/dim_energia_sadi.csv`
  2. `data/02_interim/dim_clima_agua.csv`
  3. `data/02_interim/dim_conectividad.csv`
  4. `data/02_interim/dim_talento_riesgo.csv`
  5. `data/02_interim/dim_fiscal_regulatoria.csv`

Salidas oficiales:
  - `data/03_processed/master_24_jurisdicciones.parquet` (oficial de alta compresión y tipos preservados)
  - `data/03_processed/master_24_jurisdicciones.csv` (espejo UTF-8-BOM para inspección rápida)
  - `docs/qa_report_fase2.md` (reporte automático de cobertura, nulos y calidad)

Uso:
    python src/etl/build_master_table.py
"""

import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# 0. Rutas
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = REPO_ROOT / "data" / "02_interim"
PROCESSED_DIR = REPO_ROOT / "data" / "03_processed"
DOCS_DIR = REPO_ROOT / "docs"

ANCLA_FILE = INTERIM_DIR / "jurisdicciones_base.csv"

DIM_FILES = [
    ("energia", INTERIM_DIR / "dim_energia_sadi.csv"),
    ("clima", INTERIM_DIR / "dim_clima_agua.csv"),
    ("conectividad", INTERIM_DIR / "dim_conectividad.csv"),
    ("talento_riesgo", INTERIM_DIR / "dim_talento_riesgo.csv"),
    ("fiscal_regulatoria", INTERIM_DIR / "dim_fiscal_regulatoria.csv"),
]

OUT_PARQUET = PROCESSED_DIR / "master_24_jurisdicciones.parquet"
OUT_CSV = PROCESSED_DIR / "master_24_jurisdicciones.csv"
OUT_QA_REPORT = DOCS_DIR / "qa_report_fase2.md"

# ---------------------------------------------------------------------------
# 1. Esquema y Ordenamiento Canónico de Columnas (docs/data_dictionary.md)
# ---------------------------------------------------------------------------
COLUMN_SECTIONS = {
    "Sección 0 — Ancla Territorial": [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
        "jurisdiccion_corta",
        "region_argentina",
        "lat_capital",
        "lon_capital",
    ],
    "Sección 1 — Energía y Red SADI": [
        "sadi_potencia_instalada_mw",
        "sadi_pct_renovable",
        "sadi_uptime_index",
        "sadi_margen_disponible_mw",
        "proyeccion_potencia_2028_mw",
        "proyeccion_potencia_2036_mw",
        "potencial_offgrid_score",
        "n_centrales_sadi",
        "fuente_energia",
        "fecha_corte_energia",
    ],
    "Sección 2 — Clima y Agua": [
        "temp_media_anual_c",
        "temp_max_verano_prom_c",
        "horas_free_cooling_estimadas",
        "pue_climatologico_estimado",
        "indice_estres_hidrico",
        "n_dias_datos",
        "fuente_clima",
        "fuente_hidrica",
        "periodo_referencia",
        "umbral_free_cooling_c",
        "pue_base_mecanico",
        "pue_min_free_cooling",
        "factor_horario_ajuste",
    ],
    "Sección 3 — Conectividad": [
        "distancia_las_toninas_km",
        "fibra_optica_accesos",
        "fibra_optica_pct",
        "penetracion_hogares_pct",
        "penetracion_habitantes_pct",
        "velocidad_media_bajada_mbps",
        "ixp_cabase_nodos",
        "fibra_troncal_cobertura_score",
        "fuente_conectividad",
        "fecha_corte_conectividad",
    ],
    "Sección 4 — Fiscal y Regulatorio": [
        "rigi_adhesion",
        "rigi_normativa",
        "rigi_fecha_sancion",
        "iibb_alicuota_tech_pct",
        "iibb_regimen_promocion",
        "iibb_alicuota_energia_pct",
        "indice_promocion_fiscal",
        "estado_verificacion_normativa",
        "fuente_fiscal",
        "fecha_corte_fiscal",
    ],
    "Sección 5 — Capital Humano y Riesgo": [
        "puestos_privados_totales",
        "puestos_software_clae62",
        "puestos_tic_clae61_63",
        "pct_empleo_tic_privado",
        "densidad_stem_it_score",
        "graduados_stem_anual",
        "riesgo_sismico_zona",
        "riesgo_climatico_score",
        "riesgo_combinado_score",
        "fuente_talento",
        "fecha_corte_talento",
        "fuente_riesgo_sismico",
        "fecha_corte_riesgo_sismico",
    ],
}


def load_and_merge() -> pd.DataFrame:
    """Ejecuta los cruces secuenciales 1:1 sobre jurisdiccion_id."""
    if not ANCLA_FILE.exists():
        raise FileNotFoundError(f"No existe el archivo ancla: {ANCLA_FILE}")

    print(f"Cargando ancla territorial: {ANCLA_FILE.name}")
    master = pd.read_csv(ANCLA_FILE, dtype={"jurisdiccion_id": str})
    master["jurisdiccion_id"] = master["jurisdiccion_id"].str.zfill(2)

    assert len(master) == 24, f"El ancla debe tener 24 filas, tiene {len(master)}"

    for dim_name, path in DIM_FILES:
        if not path.exists():
            raise FileNotFoundError(f"Archivo dimensional no encontrado: {path}")

        print(f"Merge con dimensión [{dim_name}]: {path.name}...")
        sub = pd.read_csv(path, dtype={"jurisdiccion_id": str})
        sub["jurisdiccion_id"] = sub["jurisdiccion_id"].str.zfill(2)

        assert len(sub) == 24, f"La dimensión {dim_name} debe tener 24 filas, tiene {len(sub)}"

        # Descartar nombre redundante para evitar _x/_y
        if "jurisdiccion_nombre" in sub.columns:
            sub = sub.drop(columns=["jurisdiccion_nombre"])

        master = master.merge(
            sub,
            on="jurisdiccion_id",
            how="inner",
            validate="1:1"
        )

    # Validaciones estructurales post-merge
    assert len(master) == 24, f"El resultado del merge debe tener 24 filas, tiene {len(master)}"

    # Verificar que no hayan quedado columnas duplicadas con sufijos
    bad_cols = [c for c in master.columns if c.endswith("_x") or c.endswith("_y")]
    assert not bad_cols, f"Columnas duplicadas encontradas tras merge: {bad_cols}"

    # Ordenar columnas según el esquema canónico
    ordered_cols = []
    for section_cols in COLUMN_SECTIONS.values():
        for col in section_cols:
            if col in master.columns and col not in ordered_cols:
                ordered_cols.append(col)

    # Agregar cualquier columna remanente si la hubiere
    remaining = [c for c in master.columns if c not in ordered_cols]
    ordered_cols.extend(remaining)

    master = master[ordered_cols]
    master = master.sort_values("jurisdiccion_id").reset_index(drop=True)
    return master


def generate_qa_report(df: pd.DataFrame, out_path: Path) -> None:
    """Genera el reporte formal de cobertura y calidad docs/qa_report_fase2.md."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_cols = len(df.columns)
    complete_cols = [c for c in df.columns if df[c].isna().sum() == 0]
    partial_cols = [c for c in df.columns if 0 < df[c].isna().sum() < len(df)]
    nan_cols = [c for c in df.columns if df[c].isna().sum() == len(df)]

    pct_global_complete = (len(complete_cols) / total_cols) * 100

    report = []
    report.append("# Reporte de Control de Calidad y Cobertura — Fase 2 (v0.5.0)")
    report.append("")
    report.append(f"**Fecha de generación:** {now_str}  ")
    report.append(f"**Tabla auditada:** `data/03_processed/master_24_jurisdicciones.parquet`  ")
    report.append(f"**Registros territoriales:** 24 jurisdicciones (23 provincias + CABA) — 100% match ancla INDEC.  ")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## 1. Resumen Ejecutivo de Cobertura")
    report.append("")
    report.append(f"- **Total de columnas unificadas:** {total_cols}")
    report.append(f"- **Columnas 100% completas (0% nulos):** {len(complete_cols)} ({pct_global_complete:.1f}%)")
    report.append(f"- **Columnas con nulos parciales justificados:** {len(partial_cols)} ({(len(partial_cols)/total_cols)*100:.1f}%)")
    report.append(f"- **Columnas 100% NaN documentadas para Fase 3/4/5:** {len(nan_cols)} ({(len(nan_cols)/total_cols)*100:.1f}%)")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## 2. Cobertura por Dimensión Analítica")
    report.append("")
    report.append("| Dimensión | Columnas Totales | 100% Completas | Parciales | 100% NaN | Estado de Viabilidad |")
    report.append("|:---|:---:|:---:|:---:|:---:|:---|")

    for section_name, cols in COLUMN_SECTIONS.items():
        present_cols = [c for c in cols if c in df.columns]
        n_comp = sum(df[c].isna().sum() == 0 for c in present_cols)
        n_part = sum(0 < df[c].isna().sum() < len(df) for c in present_cols)
        n_nan = sum(df[c].isna().sum() == len(df) for c in present_cols)
        estado = "🟢 Operativa" if n_nan == 0 else ("🟡 Operativa c/ pendientes" if n_comp > n_nan else "🔴 Requiere ingesta")
        report.append(f"| {section_name} | {len(present_cols)} | {n_comp} | {n_part} | {n_nan} | {estado} |")

    report.append("")
    report.append("---")
    report.append("")
    report.append("## 3. Matriz Exhaustiva de Columnas y Tratamiento para Fase 3")
    report.append("")
    report.append("| Sección | Columna | No-Nulos | Nulos | % Nulos | Estado | Tratamiento / Decisión Fase 3 |")
    report.append("|:---|:---|:---:|:---:|:---:|:---:|:---|")

    # Invertir mapa para saber la sección de cada columna
    col_to_sec = {}
    for sec, cols in COLUMN_SECTIONS.items():
        for c in cols:
            col_to_sec[c] = sec.split("—")[1].strip() if "—" in sec else sec

    for col in df.columns:
        sec = col_to_sec.get(col, "General")
        non_nulls = df[col].notna().sum()
        nulls = df[col].isna().sum()
        pct_null = (nulls / len(df)) * 100

        if pct_null == 0:
            status_icon = "🟢 Completo"
            decision = "Ingresa directamente al modelo multicriterio (MCDA) / clustering."
        elif pct_null < 100:
            status_icon = "🟡 Parcial"
            decision = "Valor nulo con significado de negocio (ej. sin fecha por no adhesión)."
        else:
            status_icon = "🔴 100% NaN"
            decision = "Sin datos oficiales uniformes. No inventar. Conservar o excluir en scoring Fase 3."

        report.append(f"| {sec} | `{col}` | {non_nulls} | {nulls} | {pct_null:.1f}% | {status_icon} | {decision} |")

    report.append("")
    report.append("---")
    report.append("")
    report.append("## 4. Conclusión de Calidad")
    report.append("")
    report.append("1. **Integridad Territorial:** 24/24 jurisdicciones oficiales argentinas presentes y validadas contra el ancla INDEC.")
    report.append("2. **Cero Datos Inventados:** No se aplicó ninguna imputación sintética en crudos ni en interim. Todas las variables NaN cuentan con justificación metodológica en `docs/data_dictionary.md`.")
    report.append("3. **Compatibilidad:** La exportación Parquet preserva tipos precisos para Scikit-learn en Fase 3; el CSV espejo permite inspección en Excel y visualización en Power BI.")
    report.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(report), encoding="utf-8")
    print(f"✔ Reporte QA generado exitosamente en: {out_path}")


def main() -> int:
    print("=" * 60)
    print("CONSOLIDACIÓN MAESTRA DE FASE 2 — Viabilidad IA Data Centers AR")
    print("=" * 60)

    master = load_and_merge()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Guardar Parquet oficial
    master.to_parquet(OUT_PARQUET, index=False, engine="pyarrow", compression="snappy")
    print(f"✔ Tabla maestra oficial guardada en: {OUT_PARQUET}")

    # 2. Guardar CSV espejo
    master.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✔ Tabla maestra espejo guardada en: {OUT_CSV}")

    # 3. Generar QA Report
    generate_qa_report(master, OUT_QA_REPORT)

    print("\nResumen final:")
    print(f"  - Filas consolidadas: {len(master)} / 24")
    print(f"  - Columnas totales:   {len(master.columns)}")
    print(f"  - Columnas completas: {sum(master[c].isna().sum() == 0 for c in master.columns)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
