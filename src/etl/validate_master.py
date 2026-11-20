"""
validate_master.py
==================
Auditor automático de calidad para tablas de jurisdicciones del proyecto
"Viabilidad IA Data Centers AR".

Verifica integridad estructural contra la tabla ancla territorial
`data/02_interim/jurisdicciones_base.csv` y reporta nulos, tipos y duplicados.

Uso como módulo:
    from src.etl.validate_master import validate_jurisdicciones, run_audit
    result = run_audit("data/02_interim/jurisdicciones_base.csv")

Uso por CLI:
    python src/etl/validate_master.py <path_archivo> [--ancla <path_ancla>]

    Ejemplos:
        python src/etl/validate_master.py data/02_interim/jurisdicciones_base.csv
        python src/etl/validate_master.py data/03_processed/master_24_jurisdicciones.parquet
        python src/etl/validate_master.py mi_tabla.csv --ancla data/02_interim/jurisdicciones_base.csv

Retorna (como dict en uso por módulo):
    {
        "status":      "PASS" | "FAIL",
        "errors":      [str],   # checks críticos fallidos (vacío si PASS)
        "warnings":    [str],   # checks de advertencia
        "null_report": {col: pct_nulos},  # % nulos por columna
    }
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# 0. Rutas por defecto
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_ANCLA = _REPO_ROOT / "data" / "02_interim" / "jurisdicciones_base.csv"

# IDs INDEC oficiales de las 24 jurisdicciones (ground truth estático)
_IDS_INDEC_OFICIALES = {
    "02", "06", "10", "14", "18", "22", "26", "30", "34",
    "38", "42", "46", "50", "54", "58", "62", "66", "70",
    "74", "78", "82", "86", "90", "94",
}

# Tipos esperados para columnas de la ancla territorial
_TIPOS_ESPERADOS = {
    "jurisdiccion_id":     "object",    # str en pandas
    "jurisdiccion_nombre": "object",
    "jurisdiccion_corta":  "object",
    "region_argentina":    "object",
    "lat_capital":         "float64",
    "lon_capital":         "float64",
}

# Rango válido WGS84 para Argentina
_LAT_MIN, _LAT_MAX = -55.5, -21.0
_LON_MIN, _LON_MAX = -74.0, -53.0


# ---------------------------------------------------------------------------
# 1. Función principal de validación
# ---------------------------------------------------------------------------

def validate_jurisdicciones(
    df: pd.DataFrame,
    path_ancla: Optional[Path] = None,
    verbose: bool = True,
) -> dict:
    """
    Valida un DataFrame de jurisdicciones contra la tabla ancla.

    Parameters
    ----------
    df : pd.DataFrame
        Tabla a validar (ya cargada en memoria).
    path_ancla : Path, optional
        Ruta a `jurisdicciones_base.csv`. Si es None, usa la ruta por defecto.
    verbose : bool
        Si True, imprime el reporte completo a consola.

    Returns
    -------
    dict con claves: status, errors, warnings, null_report
    """
    ancla_path = Path(path_ancla) if path_ancla else _DEFAULT_ANCLA
    errors: list[str] = []
    warnings: list[str] = []

    def _log(msg: str) -> None:
        if verbose:
            print(msg)

    _log("\n" + "─" * 60)
    _log("  AUDITOR DE CALIDAD — Viabilidad IA Data Centers AR")
    _log("─" * 60)

    # ── CHECK 1 — Exactamente 24 filas ─────────────────────────────────────
    n_filas = len(df)
    if n_filas != 24:
        msg = f"[CRÍTICO] CHECK 1 — Filas: esperadas=24, encontradas={n_filas}."
        errors.append(msg)
        _log(f"  ❌ {msg}")
    else:
        _log(f"  ✅ CHECK 1 — 24 filas confirmadas.")

    # ── CHECK 2 — Columnas mínimas requeridas ──────────────────────────────
    cols_requeridas = {"jurisdiccion_id", "jurisdiccion_nombre"}
    cols_faltantes = cols_requeridas - set(df.columns)
    if cols_faltantes:
        msg = f"[CRÍTICO] CHECK 2 — Columnas requeridas ausentes: {sorted(cols_faltantes)}."
        errors.append(msg)
        _log(f"  ❌ {msg}")
        # Sin estas columnas no podemos continuar los checks siguientes
        _log("\n  ⛔ Checks 3–7 omitidos por error crítico en CHECK 2.")
        return _build_result(errors, warnings, df, verbose)
    else:
        _log(f"  ✅ CHECK 2 — Columnas requeridas presentes: {sorted(cols_requeridas)}.")

    # ── CHECK 3 — Sin duplicados en jurisdiccion_id ────────────────────────
    duplicados = df[df["jurisdiccion_id"].duplicated(keep=False)]["jurisdiccion_id"].unique().tolist()
    if duplicados:
        msg = f"[CRÍTICO] CHECK 3 — jurisdiccion_id duplicados: {duplicados}."
        errors.append(msg)
        _log(f"  ❌ {msg}")
    else:
        _log(f"  ✅ CHECK 3 — Sin duplicados en jurisdiccion_id.")

    # ── CHECK 4 — Match contra ancla territorial ───────────────────────────
    ids_df = set(df["jurisdiccion_id"].astype(str).str.zfill(2).tolist())

    # Intentar cargar ancla; si no existe, usar el set estático oficial
    if ancla_path.exists():
        try:
            df_ancla = pd.read_csv(ancla_path, dtype={"jurisdiccion_id": str})
            ids_ancla = set(df_ancla["jurisdiccion_id"].str.zfill(2).tolist())
            ancla_origen = f"ancla CSV ({ancla_path.name})"
        except Exception as exc:
            ids_ancla = _IDS_INDEC_OFICIALES
            ancla_origen = "set estático INDEC (fallo al leer ancla CSV)"
            warnings.append(f"[WARNING] No se pudo leer la ancla CSV: {exc}. Usando set INDEC estático.")
    else:
        ids_ancla = _IDS_INDEC_OFICIALES
        ancla_origen = "set estático INDEC (ancla CSV no encontrada)"
        warnings.append(f"[WARNING] Ancla CSV no encontrada en {ancla_path}. Usando set INDEC estático.")

    ids_faltantes = ids_ancla - ids_df
    ids_extras = ids_df - ids_ancla

    if ids_faltantes or ids_extras:
        if ids_faltantes:
            msg = f"[CRÍTICO] CHECK 4 — IDs faltantes vs {ancla_origen}: {sorted(ids_faltantes)}."
            errors.append(msg)
            _log(f"  ❌ {msg}")
        if ids_extras:
            msg = f"[CRÍTICO] CHECK 4 — IDs extra vs {ancla_origen}: {sorted(ids_extras)}."
            errors.append(msg)
            _log(f"  ❌ {msg}")
    else:
        _log(f"  ✅ CHECK 4 — IDs match perfecto vs {ancla_origen}.")

    # ── CHECK 5 — Tipos de datos para columnas conocidas ──────────────────
    _log(f"  {'─'*48}")
    _log(f"  CHECK 5 — Tipos de dato (columnas de ancla territorial):")
    for col, tipo_esperado in _TIPOS_ESPERADOS.items():
        if col not in df.columns:
            continue
        tipo_real = str(df[col].dtype)
        # pandas reporta dtype "object" como "str" en algunas versiones; ambos son equivalentes
        _EQUIVALENTES = {("object", "str"), ("str", "object")}
        ok = tipo_real == tipo_esperado or (tipo_real, tipo_esperado) in _EQUIVALENTES
        icono = "✅" if ok else "⚠️ "
        _log(f"    {icono} {col:<35} esperado={tipo_esperado:<10} real={tipo_real}")
        if not ok:
            warnings.append(
                f"[WARNING] CHECK 5 — Tipo incorrecto en '{col}': "
                f"esperado={tipo_esperado}, real={tipo_real}."
            )

    # ── CHECK 6 — Reporte de nulos por columna ─────────────────────────────
    _log(f"  {'─'*48}")
    _log(f"  CHECK 6 — Porcentaje de valores nulos por columna:")
    null_report: dict[str, float] = {}
    for col in df.columns:
        pct = round(df[col].isnull().mean() * 100, 1)
        null_report[col] = pct
        icono = "🔴" if pct == 100 else ("🟡" if pct > 0 else "✅")
        _log(f"    {icono} {col:<35} {pct:>5.1f}% nulos")

    # ── CHECK 7 — Coordenadas en rango WGS84 (si las columnas existen) ─────
    _log(f"  {'─'*48}")
    lat_col = "lat_capital"
    lon_col = "lon_capital"
    if lat_col in df.columns and lon_col in df.columns:
        fuera_lat = df[
            ~df[lat_col].between(_LAT_MIN, _LAT_MAX) & df[lat_col].notna()
        ]["jurisdiccion_nombre"].tolist() if "jurisdiccion_nombre" in df.columns else []
        fuera_lon = df[
            ~df[lon_col].between(_LON_MIN, _LON_MAX) & df[lon_col].notna()
        ]["jurisdiccion_nombre"].tolist() if "jurisdiccion_nombre" in df.columns else []

        if fuera_lat:
            msg = f"[WARNING] CHECK 7 — Latitudes fuera de rango AR [{_LAT_MIN}, {_LAT_MAX}]: {fuera_lat}."
            warnings.append(msg)
            _log(f"  ⚠️  {msg}")
        if fuera_lon:
            msg = f"[WARNING] CHECK 7 — Longitudes fuera de rango AR [{_LON_MIN}, {_LON_MAX}]: {fuera_lon}."
            warnings.append(msg)
            _log(f"  ⚠️  {msg}")
        if not fuera_lat and not fuera_lon:
            _log(f"  ✅ CHECK 7 — Coordenadas dentro de rango WGS84 Argentina.")
    else:
        _log(f"  ℹ️  CHECK 7 — Omitido (columnas {lat_col}/{lon_col} no presentes).")

    return _build_result(errors, warnings, df, verbose, null_report)


# ---------------------------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------------------------

def _build_result(
    errors: list,
    warnings: list,
    df: pd.DataFrame,
    verbose: bool,
    null_report: dict | None = None,
) -> dict:
    """Construye y retorna el dict de resultado final."""
    if null_report is None:
        null_report = {col: round(df[col].isnull().mean() * 100, 1) for col in df.columns}

    status = "FAIL" if errors else "PASS"
    if verbose:
        print("─" * 60)
        if status == "PASS":
            print(f"  ✅ RESULTADO FINAL: PASS — {len(warnings)} advertencia(s).")
        else:
            print(f"  ❌ RESULTADO FINAL: FAIL — {len(errors)} error(es) crítico(s), {len(warnings)} advertencia(s).")
            for e in errors:
                print(f"     → {e}")
        if warnings:
            print(f"  Advertencias:")
            for w in warnings:
                print(f"     ⚠  {w}")
        print("─" * 60 + "\n")

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "null_report": null_report,
    }


# ---------------------------------------------------------------------------
# 3. Función de alto nivel (entry point por módulo)
# ---------------------------------------------------------------------------

def run_audit(
    path_archivo: str | Path,
    path_ancla: Optional[str | Path] = None,
    verbose: bool = True,
) -> dict:
    """
    Carga un CSV o Parquet y ejecuta la auditoría completa.

    Parameters
    ----------
    path_archivo : str | Path
        Ruta al archivo a auditar (.csv o .parquet).
    path_ancla : str | Path, optional
        Ruta a jurisdicciones_base.csv. Usa la ruta por defecto si no se indica.
    verbose : bool
        Si True, imprime el reporte a consola.

    Returns
    -------
    dict con status, errors, warnings, null_report
    """
    path_archivo = Path(path_archivo)
    ancla = Path(path_ancla) if path_ancla else _DEFAULT_ANCLA

    if verbose:
        print(f"\n[AUDITOR] Archivo a evaluar : {path_archivo}")
        print(f"[AUDITOR] Tabla ancla        : {ancla}")

    # Cargar archivo
    if not path_archivo.exists():
        print(f"[ERROR] Archivo no encontrado: {path_archivo}")
        sys.exit(1)

    ext = path_archivo.suffix.lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(path_archivo, dtype={"jurisdiccion_id": str})
        elif ext == ".parquet":
            df = pd.read_parquet(path_archivo)
            # Garantizar que jurisdiccion_id sea str con zero-padding
            if "jurisdiccion_id" in df.columns:
                df["jurisdiccion_id"] = df["jurisdiccion_id"].astype(str).str.zfill(2)
        else:
            print(f"[ERROR] Formato no soportado: '{ext}'. Use .csv o .parquet.")
            sys.exit(1)
    except Exception as exc:
        print(f"[ERROR] No se pudo cargar el archivo: {exc}")
        sys.exit(1)

    if verbose:
        print(f"[AUDITOR] Archivo cargado    : {len(df)} filas × {len(df.columns)} columnas")

    return validate_jurisdicciones(df, path_ancla=ancla, verbose=verbose)


# ---------------------------------------------------------------------------
# 4. CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auditor de calidad para tablas de jurisdicciones AR.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "archivo",
        type=str,
        help="Ruta al archivo a auditar (.csv o .parquet).",
    )
    parser.add_argument(
        "--ancla",
        type=str,
        default=None,
        help=(
            "Ruta a jurisdicciones_base.csv (tabla ancla). "
            f"Por defecto: {_DEFAULT_ANCLA}"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suprime la salida detallada. Solo imprime PASS/FAIL.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    result = run_audit(
        path_archivo=args.archivo,
        path_ancla=args.ancla,
        verbose=not args.quiet,
    )
    # Exit code para integración CI/CD
    sys.exit(0 if result["status"] == "PASS" else 1)
