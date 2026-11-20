"""
fetch_conectividad.py
=====================
Módulo GIS y ETL para la dimensión Conectividad del proyecto
"Viabilidad de Data Centers y Campus de IA en Argentina".

Calcula la distancia geodésica exacta (Haversine WGS84) desde cada capital
provincial hasta el punto de amarre de cables submarinos en Las Toninas
(-36.487, -56.696), e ingesta los indicadores de conectividad fija de ENACOM:
- Accesos por tecnología (Fibra Óptica / FTTH, Cablemódem, ADSL, etc.)
- Penetración de internet fijo (accesos cada 100 hogares y habitantes)
- Velocidad media de descarga (Mbps)
- Nodos IXP CABASE (mantenido en NaN documentado según regla de calidad)

Salidas:
- `data/01_raw/enacom_internet_tecnologias_raw.csv`
- `data/01_raw/enacom_internet_penetracion_raw.csv`
- `data/01_raw/enacom_internet_velocidad_raw.csv`
- `data/02_interim/dim_conectividad.csv`
"""

import math
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

# Rutas del repositorio
REPO_ROOT = Path(__file__).resolve().parents[2]
PATH_ANCLA = REPO_ROOT / "data" / "02_interim" / "jurisdicciones_base.csv"
DIR_RAW = REPO_ROOT / "data" / "01_raw"
DIR_INTERIM = REPO_ROOT / "data" / "02_interim"
PATH_SALIDA = DIR_INTERIM / "dim_conectividad.csv"

# Coordenadas oficiales de amarre de cables submarinos en Las Toninas, Bs As
LAT_LAS_TONINAS = -36.487
LON_LAS_TONINAS = -56.696

# URLs oficiales de ENACOM (Datos Abiertos)
URLS_ENACOM = {
    "tecnologias": (
        "https://indicadores.enacom.gob.ar/Files/DatosAbiertos/"
        "internet_accesos_tecnologias_provincias.csv"
    ),
    "penetracion": (
        "https://indicadores.enacom.gob.ar/Files/DatosAbiertos/"
        "internet_accesos_penetracion_provincias.csv"
    ),
    "velocidad": (
        "https://indicadores.enacom.gob.ar/Files/DatosAbiertos/"
        "internet_velocidad_media_descarga_provincias.csv"
    ),
}

# Mapeo exhaustivo de nombres ENACOM a jurisdiccion_id oficial (INDEC)
MAPA_PROVINCIAS_ENACOM: Dict[str, str] = {
    "CABA": "02",
    "Buenos Aires": "06",
    "Catamarca": "10",
    "Córdoba": "14",
    "Corrientes": "18",
    "Chaco": "22",
    "Chubut": "26",
    "Entre Ríos": "30",
    "Formosa": "34",
    "Jujuy": "38",
    "La Pampa": "42",
    "La Rioja": "46",
    "Mendoza": "50",
    "Misiones": "54",
    "Neuquén": "58",
    "Río Negro": "62",
    "Salta": "66",
    "San Juan": "70",
    "San Luis": "74",
    "Santa Cruz": "78",
    "Santa Fe": "82",
    "Santiago Del Estero": "86",
    "Santiago del Estero": "86",
    "Tierra Del Fuego": "94",
    "Tierra del Fuego": "94",
    "Tucumán": "90",
}


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia geodésica en kilómetros entre dos coordenadas
    en el elipsoide WGS84 (EPSG:4326) mediante la fórmula de Haversine.

    Radio de la Tierra considerado: R = 6.371,0 km.
    """
    R = 6371.0  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def descargar_crudo_enacom(nombre: str, url: str) -> Path:
    """
    Descarga el dataset crudo de ENACOM a data/01_raw/ asegurando inmutabilidad.
    """
    DIR_RAW.mkdir(parents=True, exist_ok=True)
    destino = DIR_RAW / f"enacom_internet_{nombre}_raw.csv"

    print(f"[CONECTIVIDAD] Descargando {nombre} desde {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()

    with open(destino, "wb") as f:
        f.write(content)

    print(f"  -> Guardado crudo: {destino} ({len(content):,} bytes)")
    return destino


def procesar_conectividad() -> pd.DataFrame:
    """
    Ejecuta el pipeline completo de la dimensión Conectividad:
    1. Carga ancla territorial (jurisdicciones_base.csv)
    2. Calcula distancia Haversine a Las Toninas
    3. Descarga y procesa datasets ENACOM al período más reciente
    4. Unifica y normaliza según contrato AGENTS.md
    """
    if not PATH_ANCLA.exists():
        raise FileNotFoundError(f"No se encontró la tabla ancla: {PATH_ANCLA}")

    df_base = pd.read_csv(PATH_ANCLA, dtype={"jurisdiccion_id": str})
    print(f"[CONECTIVIDAD] Ancla territorial cargada: {len(df_base)} jurisdicciones.")

    # 1. Distancia geodésica a Las Toninas
    print("[CONECTIVIDAD] Calculando distancias geodésicas a Las Toninas...")
    distancias = []
    for _, row in df_base.iterrows():
        dist = haversine_distance_km(
            float(row["lat_capital"]),
            float(row["lon_capital"]),
            LAT_LAS_TONINAS,
            LON_LAS_TONINAS,
        )
        distancias.append(dist)
    df_base["distancia_las_toninas_km"] = distancias

    # 2. Descargar y parsear datasets ENACOM
    archivos = {}
    for nombre, url in URLS_ENACOM.items():
        archivos[nombre] = descargar_crudo_enacom(nombre, url)

    # 3. Procesar tecnologías (Fibra Óptica / FTTH)
    df_tec = pd.read_csv(archivos["tecnologias"])
    max_anio_tec = df_tec["anio"].max()
    max_trim_tec = df_tec[df_tec["anio"] == max_anio_tec]["trimestre"].max()
    print(f"[CONECTIVIDAD] Tecnologías: período más reciente {max_anio_tec}-T{max_trim_tec}")
    df_tec_latest = df_tec[
        (df_tec["anio"] == max_anio_tec) & (df_tec["trimestre"] == max_trim_tec)
    ].copy()
    df_tec_latest["jurisdiccion_id"] = df_tec_latest["provincia"].map(MAPA_PROVINCIAS_ENACOM)

    # 4. Procesar penetración
    df_pen = pd.read_csv(archivos["penetracion"])
    max_anio_pen = df_pen["anio"].max()
    max_trim_pen = df_pen[df_pen["anio"] == max_anio_pen]["trimestre"].max()
    print(f"[CONECTIVIDAD] Penetración: período más reciente {max_anio_pen}-T{max_trim_pen}")
    df_pen_latest = df_pen[
        (df_pen["anio"] == max_anio_pen) & (df_pen["trimestre"] == max_trim_pen)
    ].copy()
    df_pen_latest["jurisdiccion_id"] = df_pen_latest["provincia"].map(MAPA_PROVINCIAS_ENACOM)

    # 5. Procesar velocidad
    df_vel = pd.read_csv(archivos["velocidad"])
    max_anio_vel = df_vel["anio"].max()
    max_trim_vel = df_vel[df_vel["anio"] == max_anio_vel]["trimestre"].max()
    print(f"[CONECTIVIDAD] Velocidad: período más reciente {max_anio_vel}-T{max_trim_vel}")
    df_vel_latest = df_vel[
        (df_vel["anio"] == max_anio_vel) & (df_vel["trimestre"] == max_trim_vel)
    ].copy()
    df_vel_latest["jurisdiccion_id"] = df_vel_latest["provincia"].map(MAPA_PROVINCIAS_ENACOM)

    # 6. Consolidación de métricas ENACOM por jurisdiccion_id
    # FTTH accesos y porcentaje
    df_tec_summary = df_tec_latest[["jurisdiccion_id", "fibra_optica", "total"]].rename(
        columns={"fibra_optica": "fibra_optica_accesos", "total": "total_accesos_fijos"}
    )
    df_tec_summary["fibra_optica_pct"] = (
        (df_tec_summary["fibra_optica_accesos"] / df_tec_summary["total_accesos_fijos"]) * 100.0
    ).round(2)

    # Penetración hogares
    df_pen_summary = df_pen_latest[
        ["jurisdiccion_id", "accesos_cada_100_hogares", "accesos_cada_100_habitantes"]
    ].rename(
        columns={
            "accesos_cada_100_hogares": "penetracion_hogares_pct",
            "accesos_cada_100_habitantes": "penetracion_habitantes_pct",
        }
    )

    # Velocidad
    df_vel_summary = df_vel_latest[["jurisdiccion_id", "Mbps"]].rename(
        columns={"Mbps": "velocidad_media_bajada_mbps"}
    )

    # 7. Merge con tabla base
    df_merged = df_base.merge(df_tec_summary, on="jurisdiccion_id", how="left")
    df_merged = df_merged.merge(df_pen_summary, on="jurisdiccion_id", how="left")
    df_merged = df_merged.merge(df_vel_summary, on="jurisdiccion_id", how="left")

    # Columnas auditables requeridas y gobernanza de NaNs
    df_merged["ixp_cabase_nodos"] = np.nan  # Cero datos inventados: carga manual pendiente
    df_merged["fibra_troncal_cobertura_score"] = np.nan  # Pendiente Fase 3 scoring
    df_merged["fuente_conectividad"] = "ENACOM / IGN"
    df_merged["fecha_corte_conectividad"] = f"{max_anio_tec}-T{max_trim_tec}"

    # Selección final de columnas según contrato
    cols_finales = [
        "jurisdiccion_id",
        "jurisdiccion_nombre",
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
    ]
    df_salida = df_merged[cols_finales].copy()

    # Formato de salida UTF-8 con BOM para interoperabilidad
    DIR_INTERIM.mkdir(parents=True, exist_ok=True)
    df_salida.to_csv(PATH_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\n[CONECTIVIDAD] ✅ Archivo generado exitosamente: {PATH_SALIDA}")
    print(f"[CONECTIVIDAD] Dimensiones: {df_salida.shape[0]} filas × {df_salida.shape[1]} columnas.")

    return df_salida


if __name__ == "__main__":
    try:
        procesar_conectividad()
    except Exception as exc:
        print(f"[ERROR] Falló la ejecución de fetch_conectividad.py: {exc}", file=sys.stderr)
        sys.exit(1)
