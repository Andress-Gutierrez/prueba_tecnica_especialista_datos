"""
Transformaciones técnicas del dataset Ventas.

Solo adaptación estructural del DataFrame: normalización de columnas,
textos, fechas, tipos y deduplicación exacta. Sin reglas de negocio.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from etl.transform.cast_types import cast_column_types
from etl.transform.normalize_columns import normalize_column_names
from etl.transform.pipeline import apply_pipeline
from etl.transform.remove_duplicates import remove_duplicates

# Nombres esperados tras normalize_column_names (derivados del perfilado).
_DATE_YYYYMMDD_COLS: tuple[str, ...] = (
    "fecha_venta",
    "fecha_finalizacion_reserva",
)

_TYPE_MAP: dict[str, str] = {
    "cuotas": "Float64",
    "valor_antes_de_iva": "Float64",
    "ano": "Int64",
    "mes": "Int64",
    "dia": "Int64",
    "identificacion": "string",
    "cedula_vendedor": "string",
    "codigo_factura": "string",
    "region_comercial": "string",
    "gv_division": "string",
    "d_division": "string",
    "canal": "string",
    "canal2": "string",
    "categoria": "string",
    "marca": "string",
    "nota_credito": "string",
}


def _strip_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Recorta espacios en columnas de texto (sin semántica de negocio)."""
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return out


def _parse_yyyymmdd_columns(
    df: pd.DataFrame,
    columns: Sequence[str],
) -> pd.DataFrame:
    """Convierte enteros/cadenas YYYYMMDD a datetime (errors → NaT)."""
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            continue
        as_str = (
            pd.to_numeric(out[col], errors="coerce")
            .astype("Int64")
            .astype("string")
        )
        out[col] = pd.to_datetime(as_str, format="%Y%m%d", errors="coerce")
    return out


def _parse_ventas_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parseo técnico de fechas del dataset Ventas."""
    return _parse_yyyymmdd_columns(df, _DATE_YYYYMMDD_COLS)


def _cast_ventas_types(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el mapeo de tipos técnicos de Ventas."""
    return cast_column_types(df, _TYPE_MAP)


def _dedupe_exact_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas 100% duplicadas (hallazgo técnico de calidad)."""
    return remove_duplicates(df, subset=None, keep="first")


def transform_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el pipeline técnico de Ventas.

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
            _parse_ventas_dates,
            _cast_ventas_types,
            _dedupe_exact_rows,
        ],
    )
