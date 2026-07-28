"""Eliminación genérica de registros duplicados."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def remove_duplicates(
    df: pd.DataFrame,
    *,
    subset: Sequence[str] | None = None,
    keep: str | bool = "first",
) -> pd.DataFrame:
    """
    Elimina filas duplicadas de forma reutilizable.

    No asume claves de negocio. Si ``subset`` es ``None``, considera
    todas las columnas (comportamiento estándar de pandas).

    Parameters
    ----------
    df:
        DataFrame de entrada.
    subset:
        Columnas opcionales que definen la igualdad de filas.
    keep:
        Criterio ``keep`` de ``DataFrame.drop_duplicates``
        (``'first'``, ``'last'`` o ``False``).

    Returns
    -------
    pandas.DataFrame
        Copia sin duplicados según los parámetros.
    """
    out = df.copy()
    cols = list(subset) if subset is not None else None
    if cols is not None:
        cols = [col for col in cols if col in out.columns]
        if not cols:
            return out
    return out.drop_duplicates(subset=cols, keep=keep).reset_index(drop=True)
