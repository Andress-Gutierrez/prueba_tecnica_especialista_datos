"""Infraestructura genérica para tratamiento de valores nulos."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd


def clean_nulls(
    df: pd.DataFrame,
    *,
    fill_values: Mapping[str, Any] | None = None,
    drop_rows_if_null_in: Sequence[str] | None = None,
) -> pd.DataFrame:
    """
    Aplica tratamiento genérico de nulos según parámetros del llamador.

    No contiene reglas de negocio. Si no se pasa ningún parámetro de
    acción, devuelve una copia sin cambios estructurales.

    Parameters
    ----------
    df:
        DataFrame de entrada.
    fill_values:
        Mapa opcional ``columna → valor`` para ``fillna``.
    drop_rows_if_null_in:
        Columnas opcionales: se eliminan filas con nulo en cualquiera
        de ellas (``how='any'`` sobre ese subconjunto).

    Returns
    -------
    pandas.DataFrame
        Copia tras el tratamiento solicitado.
    """
    out = df.copy()

    if fill_values:
        applicable = {col: val for col, val in fill_values.items() if col in out.columns}
        if applicable:
            out = out.fillna(value=applicable)

    if drop_rows_if_null_in:
        cols = [col for col in drop_rows_if_null_in if col in out.columns]
        if cols:
            out = out.dropna(subset=cols, how="any")

    return out
