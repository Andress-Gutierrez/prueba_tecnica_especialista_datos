"""Infraestructura genérica para conversión de tipos de columnas."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd


def cast_column_types(
    df: pd.DataFrame,
    type_map: Mapping[str, Any],
) -> pd.DataFrame:
    """
    Aplica conversiones de tipo según un mapeo externo columna → dtype.

    No define conversiones específicas de ningún dataset. El llamador
    suministra el mapeo. Las columnas ausentes en ``df`` se ignoran.

    Parameters
    ----------
    df:
        DataFrame de entrada.
    type_map:
        Mapa ``nombre_columna → dtype`` compatible con ``DataFrame.astype``.

    Returns
    -------
    pandas.DataFrame
        Copia con las columnas indicadas casteadas.

    Raises
    ------
    TypeError
        Si ``type_map`` no es un mapping.
    """
    if not isinstance(type_map, Mapping):
        raise TypeError(
            f"type_map debe ser un Mapping; recibido: {type(type_map)!r}"
        )

    out = df.copy()
    applicable = {col: dtype for col, dtype in type_map.items() if col in out.columns}
    if not applicable:
        return out
    return out.astype(applicable)
