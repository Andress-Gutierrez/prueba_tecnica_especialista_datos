"""
Transformaciones técnicas del dataset Gestión TMK (Registros).

Solo adaptación estructural: columnas, textos, fechas, tipos y
deduplicación exacta. Sin tipificación de negocio ni filtros TMK.
"""

from __future__ import annotations

import pandas as pd

from etl.transform.cast_types import cast_column_types
from etl.transform.normalize_columns import normalize_column_names
from etl.transform.pipeline import apply_pipeline
from etl.transform.remove_duplicates import remove_duplicates

_TYPE_MAP: dict[str, str] = {
    "cantidad": "Int64",
    "periodo": "Int64",
    "dia": "Int64",
    "intentos": "Float64",
    "division_comercial": "string",
    "nombre_campana": "string",
    "tipo_contacto": "string",
    "detalle1": "string",
    "area_comercial": "string",
    "segmento": "string",
    "aliado": "string",
    "gerente": "string",
    "jefe": "string",
    "especialista": "string",
}

_ISO_DATE_COLS: tuple[str, ...] = (
    "fecha_gestion",
    "fecha_cargue",
)


def _strip_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Recorta espacios en columnas de texto."""
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return out


def _parse_iso_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parsea columnas de fecha en texto ISO a datetime."""
    out = df.copy()
    for col in _ISO_DATE_COLS:
        if col not in out.columns:
            continue
        out[col] = pd.to_datetime(out[col], errors="coerce")
    return out


def _parse_periodo_yyyymm(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza ``periodo`` (YYYYMM) a fecha de inicio de mes."""
    out = df.copy()
    if "periodo" not in out.columns:
        return out
    as_str = (
        pd.to_numeric(out["periodo"], errors="coerce")
        .astype("Int64")
        .astype("string")
    )
    out["periodo"] = pd.to_datetime(
        as_str + "01",
        format="%Y%m%d",
        errors="coerce",
    )
    return out


def _cast_gestion_types(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica tipos técnicos; omite columnas ya convertidas a datetime."""
    skip = set(_ISO_DATE_COLS) | {"periodo"}
    type_map = {k: v for k, v in _TYPE_MAP.items() if k not in skip}
    return cast_column_types(df, type_map)


def _dedupe_exact_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas 100% duplicadas (hallazgo técnico de calidad)."""
    return remove_duplicates(df, subset=None, keep="first")


def transform_gestion_tmk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el pipeline técnico de Gestión TMK (Registros).

    Parameters
    ----------
    df:
        DataFrame crudo de extracción.

    Returns
    -------
    pandas.DataFrame
        DataFrame adaptado técnicamente (sin reglas de negocio).
    """
    return apply_pipeline(
        df,
        [
            normalize_column_names,
            _strip_text_columns,
            _parse_iso_dates,
            _parse_periodo_yyyymm,
            _cast_gestion_types,
            _dedupe_exact_rows,
        ],
    )
