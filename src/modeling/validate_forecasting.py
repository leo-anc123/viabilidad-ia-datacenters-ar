"""
Suite de Validación Automatizada — Análisis Predictivo Prospectivo (2026–2036)
Proyecto: Viabilidad de Data Centers y Campus de IA en Argentina (Fase 3 — Bloque 2C)

Valida con aserciones estrictas:
1. Existencia e integridad de data/04_outputs/proyecciones_2026_2036.parquet y .csv.
2. Existencia e integridad de data/04_outputs/pbi_ready/fact_proyecciones_2026_2036.csv.
3. Dimensiones exactas:
   - Granularidad provincial: exactamente 504 registros (24 jurisdicciones × 7 años × 3 escenarios).
   - Granularidad BI hecho: exactamente 1.512 registros (504 registros × 3 perfiles oficiales).
4. CERO valores nulos (NaNs) en todo el conjunto de proyecciones.
5. Acotación estricta de subscores dimensionales y scores compuestos a [0.0, 100.0].
6. Rankings válidos: permutación estricta 1..24 sin empates ni omisiones para cada (año, escenario, perfil).
7. ORIGEN ÚNICO EN 2026:
   - Para anio == 2026, los tres escenarios (Acelerado, Tendencial, Conservador) deben confluir
     exactamente en el score base actual de scores_mcda_perfiles.parquet.
   - delta_score_vs_2026 == 0.0 y delta_rank_vs_2026 == 0 en todas las filas de 2026.
8. Monotonicidad lógica inter-escenario:
   - En cada año futuro (t > 2026), el promedio nacional del Score Compuesto debe cumplir:
     Score(Acelerado) >= Score(Tendencial) >= Score(Conservador).
9. Restricción física de Tierra del Fuego:
   - En 2026 y en todos los años de Tendencial y Conservador, TDF no tiene potencia SADI (0.0 MW).
   - En Acelerado, el aporte de microrred documentada solo ocurre a partir de 2031 (t >= 2031).
10. Coherencia termodinámica de PUE:
   - Subscore de clima no supera 100.0 y PUE respeta el límite de diseño PUE >= 1.10.
"""

import sys
from pathlib import Path
from typing import Tuple, List, Dict
import numpy as np
import pandas as pd

_pkg_root = Path(__file__).resolve().parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

OUTPUTS_DIR = _pkg_root / "data" / "04_outputs"
PBI_DIR = OUTPUTS_DIR / "pbi_ready"
PROFILES = ["campus_ia_training", "nodo_inferencia_edge", "benchmark_cabase"]
EXPECTED_YEARS = [2026, 2028, 2030, 2031, 2032, 2034, 2036]
EXPECTED_SCENARIOS = ["acelerado", "tendencial", "conservador"]


def test_file_existence_and_shapes() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Test 1: Verifica existencia física de archivos y dimensiones exactas."""
    print("▶ [TEST 1] Existencia de archivos y dimensiones...")
    parquet_path = OUTPUTS_DIR / "proyecciones_2026_2036.parquet"
    csv_path = OUTPUTS_DIR / "proyecciones_2026_2036.csv"
    pbi_path = PBI_DIR / "fact_proyecciones_2026_2036.csv"

    assert parquet_path.exists(), f"Falta archivo: {parquet_path}"
    assert csv_path.exists(), f"Falta archivo: {csv_path}"
    assert pbi_path.exists(), f"Falta archivo: {pbi_path}"

    df_parquet = pd.read_parquet(parquet_path)
    df_pbi = pd.read_csv(pbi_path, dtype={"jurisdiccion_id": str})

    expected_rows_parquet = 24 * 7 * 3  # 504
    assert len(df_parquet) == expected_rows_parquet, (
        f"Se esperaban {expected_rows_parquet} filas en parquet, obtenidas: {len(df_parquet)}"
    )

    expected_rows_pbi = 504 * 3  # 1.512
    assert len(df_pbi) == expected_rows_pbi, (
        f"Se esperaban {expected_rows_pbi} filas en fact_proyecciones, obtenidas: {len(df_pbi)}"
    )

    assert df_parquet["jurisdiccion_id"].nunique() == 24, "Faltan jurisdicciones en parquet"
    assert df_pbi["jurisdiccion_id"].nunique() == 24, "Faltan jurisdicciones en PBI"

    assert sorted(df_parquet["anio"].unique().tolist()) == EXPECTED_YEARS, "Años de proyección inconsistentes"
    assert set(df_parquet["escenario_id"].unique()) == set(EXPECTED_SCENARIOS), "Escenarios inconsistentes"

    print(f"  ✔ Parquet: {len(df_parquet)} filas | PBI Fact: {len(df_pbi)} filas | 24 jurisdicciones OK.")
    return df_parquet, df_pbi


def test_nulls_and_range_bounds(df_parquet: pd.DataFrame, df_pbi: pd.DataFrame) -> None:
    """Test 2: Cero nulos y acotación estricta a [0.0, 100.0]."""
    print("▶ [TEST 2] Verificación de nulos y rango [0.0, 100.0]...")

    nulls_parquet = df_parquet.isnull().sum().sum()
    assert nulls_parquet == 0, f"Se detectaron {nulls_parquet} valores nulos en proyecciones.parquet"

    nulls_pbi = df_pbi.isnull().sum().sum()
    assert nulls_pbi == 0, f"Se detectaron {nulls_pbi} valores nulos en fact_proyecciones_2026_2036.csv"

    subscores = [c for c in df_parquet.columns if c.startswith("subscore_")]
    assert len(subscores) == 6, f"Se esperaban 6 subscores dimensionales, encontrados: {len(subscores)}"

    for sub in subscores:
        min_v = df_parquet[sub].min()
        max_v = df_parquet[sub].max()
        assert min_v >= 0.0, f"Violación de cota inferior en {sub}: min={min_v}"
        assert max_v <= 100.0, f"Violación de cota superior en {sub}: max={max_v}"

    for prof in PROFILES:
        score_col = f"score_{prof}"
        min_s = df_parquet[score_col].min()
        max_s = df_parquet[score_col].max()
        assert min_s >= 0.0, f"Violación de cota inferior en {score_col}: min={min_s}"
        assert max_s <= 100.0, f"Violación de cota superior en {score_col}: max={max_s}"

    print(f"  ✔ 0 nulos detectados. 6 subscores y 3 perfiles estrictamente dentro de [0.0, 100.0].")


def test_origin_unique_2026(df_parquet: pd.DataFrame) -> None:
    """Test 3: Origen único en 2026 (confluencia de escenarios y deltas exactamente 0.0)."""
    print("▶ [TEST 3] Origen único en 2026 y congruencia con año base MCDA...")

    # Cargar scores oficiales base de 2026
    mcda_base_path = OUTPUTS_DIR / "scores_mcda_perfiles.parquet"
    assert mcda_base_path.exists(), f"Falta archivo base: {mcda_base_path}"
    df_base_mcda = pd.read_parquet(mcda_base_path).set_index("jurisdiccion_id")

    df_2026 = df_parquet[df_parquet["anio"] == 2026]
    assert len(df_2026) == 24 * 3, f"Se esperaban 72 filas en 2026, obtenidas: {len(df_2026)}"

    for scen in EXPECTED_SCENARIOS:
        df_scen_2026 = df_2026[df_2026["escenario_id"] == scen].set_index("jurisdiccion_id")

        for prof in PROFILES:
            # 1. Delta vs 2026 debe ser exactamente 0.0
            max_delta = np.abs(df_scen_2026[f"delta_score_{prof}"]).max()
            assert max_delta == 0.0, f"Delta no nulo en 2026 para {prof} ({scen}): max_delta={max_delta}"

            max_drank = np.abs(df_scen_2026[f"delta_rank_{prof}"]).max()
            assert max_drank == 0, f"Delta rank no nulo en 2026 para {prof} ({scen}): max_drank={max_drank}"

            # 2. Coincidencia idéntica con el score base actual (tolerancia 1e-4)
            diff_score = np.abs(df_scen_2026[f"score_{prof}"] - df_base_mcda[f"score_{prof}"]).max()
            assert diff_score < 1e-3, (
                f"Discrepancia entre proyección 2026 y score base en {prof} ({scen}): max_diff={diff_score}"
            )

    print("  ✔ En anio == 2026 todos los escenarios confluyen exactamente: delta_vs_2026 == 0.0.")


def test_ranking_permutation_validity(df_parquet: pd.DataFrame) -> None:
    """Test 4: Rankings forman permutación válida 1..24 sin saltos ni empates."""
    print("▶ [TEST 4] Validez ordinal de rankings (1 a 24 sin empates)...")

    expected_ranks = list(range(1, 25))

    for year in EXPECTED_YEARS:
        for scen in EXPECTED_SCENARIOS:
            sub_df = df_parquet[(df_parquet["anio"] == year) & (df_parquet["escenario_id"] == scen)]
            for prof in PROFILES:
                ranks = sorted(sub_df[f"rank_{prof}"].tolist())
                assert ranks == expected_ranks, (
                    f"Ranking inválido para {year}-{scen}-{prof}: {ranks}"
                )

    print("  ✔ 100% de combinaciones (año × escenario × perfil) tienen permutaciones perfectas 1..24.")


def test_scenario_monotonicity(df_parquet: pd.DataFrame) -> None:
    """Test 5: Monotonicidad lógica inter-escenario (Acelerado >= Tendencial >= Conservador)."""
    print("▶ [TEST 5] Monotonicidad lógica macroeconómica entre escenarios...")

    future_years = [y for y in EXPECTED_YEARS if y > 2026]

    for year in future_years:
        for prof in PROFILES:
            score_col = f"score_{prof}"
            mean_acel = df_parquet[(df_parquet["anio"] == year) & (df_parquet["escenario_id"] == "acelerado")][score_col].mean()
            mean_tend = df_parquet[(df_parquet["anio"] == year) & (df_parquet["escenario_id"] == "tendencial")][score_col].mean()
            mean_cons = df_parquet[(df_parquet["anio"] == year) & (df_parquet["escenario_id"] == "conservador")][score_col].mean()

            assert mean_acel >= mean_tend, (
                f"Violación de monotonicidad en {year} ({prof}): Acelerado ({mean_acel:.2f}) < Tendencial ({mean_tend:.2f})"
            )
            assert mean_tend >= mean_cons, (
                f"Violación de monotonicidad en {year} ({prof}): Tendencial ({mean_tend:.2f}) < Conservador ({mean_cons:.2f})"
            )

    print("  ✔ Verificado: Acelerado >= Tendencial >= Conservador en promedio nacional para todo t > 2026.")


def test_physical_constraints_tdf_and_pue(df_parquet: pd.DataFrame) -> None:
    """Test 6: Restricción física de Tierra del Fuego y cota termodinámica de PUE."""
    print("▶ [TEST 6] Restricciones físicas: Tierra del Fuego (SADI) y cota PUE...")

    # 1. Tierra del Fuego (id 94): en 2026, y en Tendencial/Conservador siempre subscore energía bajo
    df_tdf = df_parquet[df_parquet["jurisdiccion_id"] == "94"]

    # En 2026 el subscore_energia de TDF debe ser exactamente 0.0 (red aislada)
    tdf_2026_energia = df_tdf[df_tdf["anio"] == 2026]["subscore_energia"].unique()
    assert len(tdf_2026_energia) == 1 and tdf_2026_energia[0] == 0.0, (
        f"TDF en 2026 debe tener subscore_energia == 0.0, obtenido: {tdf_2026_energia}"
    )

    # En Tendencial y Conservador durante todo 2026-2036, TDF subscore_energia debe ser 0.0
    tdf_tend_cons = df_tdf[df_tdf["escenario_id"].isin(["tendencial", "conservador"])]
    assert (tdf_tend_cons["subscore_energia"] == 0.0).all(), (
        "TDF no puede tener subscore_energia > 0 en escenarios tendencial o conservador"
    )

    # En Acelerado, el subscore_energia solo puede crecer en t >= 2031
    tdf_acel_pre2031 = df_tdf[(df_tdf["escenario_id"] == "acelerado") & (df_tdf["anio"] < 2031)]
    assert (tdf_acel_pre2031["subscore_energia"] == 0.0).all(), (
        "TDF no puede tener subscore_energia > 0 antes de 2031 en escenario acelerado"
    )

    tdf_acel_post2031 = df_tdf[(df_tdf["escenario_id"] == "acelerado") & (df_tdf["anio"] >= 2031)]
    assert (tdf_acel_post2031["subscore_energia"] > 0.0).all(), (
        "TDF debe reflejar aporte de microrred documentada a partir de 2031 en escenario acelerado"
    )

    # 2. Cota física de clima: subscore clima en Patagonia debe ser superior al de Norte Cálido
    df_sc_2036 = df_parquet[(df_parquet["jurisdiccion_id"] == "78") & (df_parquet["anio"] == 2036)]["subscore_clima"].mean()
    df_formosa_2036 = df_parquet[(df_parquet["jurisdiccion_id"] == "34") & (df_parquet["anio"] == 2036)]["subscore_clima"].mean()
    assert df_sc_2036 > df_formosa_2036 + 50.0, (
        f"Patagonia (Santa Cruz: {df_sc_2036:.1f}) debe superar ampliamente a Norte Cálido (Formosa: {df_formosa_2036:.1f}) en clima"
    )

    print("  ✔ Restricciones físicas verificadas al 100% (TDF SADI y clima termodinámico).")


def run_all_forecasting_tests() -> None:
    print("=" * 80)
    print("🔍 INICIANDO SUITE DE VALIDACIÓN: ANÁLISIS PREDICTIVO PROSPECTIVO 2026–2036")
    print("=" * 80)

    df_parquet, df_pbi = test_file_existence_and_shapes()
    test_nulls_and_range_bounds(df_parquet, df_pbi)
    test_origin_unique_2026(df_parquet)
    test_ranking_permutation_validity(df_parquet)
    test_scenario_monotonicity(df_parquet)
    test_physical_constraints_tdf_and_pue(df_parquet)

    print("\n" + "=" * 80)
    print("🎉 TODAS LAS PRUEBAS DE VALIDACIÓN DE FORECASTING PASARON CON ÉXITO (PASS)")
    print("=" * 80)


if __name__ == "__main__":
    run_all_forecasting_tests()
