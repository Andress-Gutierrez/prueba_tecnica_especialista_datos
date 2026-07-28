"""Orquestador genérico de transformaciones sobre DataFrames."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pandas as pd

TransformFn = Callable[[pd.DataFrame], pd.DataFrame]


def apply_pipeline(
    df: pd.DataFrame,
    steps: Sequence[TransformFn],
) -> pd.DataFrame:
    """
    Ejecuta una secuencia de transformaciones sobre un DataFrame.

    Cada paso recibe el DataFrame resultante del anterior y debe devolver
    un DataFrame. El orquestador no conoce datasets ni reglas de negocio.

    Parameters
    ----------
    df:
        DataFrame de entrada.
    steps:
        Secuencia ordenada de funciones ``(DataFrame) -> DataFrame``.

    Returns
    -------
    pandas.DataFrame
        DataFrame tras aplicar todos los pasos en orden.

    Raises
    ------
    TypeError
        Si algún paso no es invocable.
    """
    result = df
    for index, step in enumerate(steps):
        if not callable(step):
            raise TypeError(
                f"El paso en la posición {index} no es invocable: {type(step)!r}"
            )
        result = step(result)
    return result
