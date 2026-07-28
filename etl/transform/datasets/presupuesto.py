"""
Transformaciones técnicas del dataset Presupuesto.

Solo adaptación estructural: columnas, textos, periodo y tipos.
No consolida cruces con medidas distintas (eso es regla de negocio/ETL load).
"""

from __future__ import annotations

import pandas as pd

from etl.transform.cast_types import cast_column_types
from etl.transform.normalize_columns import normalize_column_names
from etl.transform.pipeline import apply_pipeline

_TYPE_MAP: dict[str, str] = {
    "mes": "Int64",
    "terminales": "Float64",
    "tecnologia": "Float64",
    "t_t": "Float64",
    "region": "string",
    "canal": "string",
    "canal2": "string",
    "sub_canal": "string",
    "categoria": "string",
    "unidad_de_gestion": "string",
    "especialista": "string",
    "jefe": "string",
    "gerente": "string",
    "descrip2": "string",
}


def _strip_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Recorta espacios en columnas de texto."""
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return out


def _parse_periodo_yyyymm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza ``mes`` (YYYYMM) a fecha del primer día del mes.

    Conserva también el entero original en ``mes`` vía recaste posterior;
    aquí se crea ``mes_fecha`` solo si se desea — para no inventar columnas
    de negocio, se convierte ``mes`` a datetime de inicio de periodo.
    """
    out = df.copy()
    if "mes" not in out.columns:
        return out
    as_str = (
        pd.to_numeric(out["mes"], errors="coerce")
        .astype("Int64")
        .astype("string")
    )
    out["mes"] = pd.to_datetime(as_str + "01", format="%Y%m%d", errors="coerce")
    return out


def _cast_presupuesto_types(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica tipos técnicos; omite ``mes`` si ya es datetime."""
    type_map = {k: v for k, v in _TYPE_MAP.items() if k != "mes"}
    return cast_column_types(df, type_map)


def transform_presupuesto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el pipeline técnico de Presupuesto.

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
            _parse_periodo_yyyymm,
            _cast_presupuesto_types,
        ],
    )
