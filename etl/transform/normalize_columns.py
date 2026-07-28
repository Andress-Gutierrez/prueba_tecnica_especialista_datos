"""Normalización técnica de nombres de columnas (sin semántica de negocio)."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd


def _normalize_column_name(name: object) -> str:
    """
    Normaliza un nombre de columna a snake_case ASCII técnico.

    - Convierte a str
    - Quita acentos
    - Minúsculas
    - Espacios y separadores → guion bajo
    - Colapsa guiones bajos repetidos
    """
    text = str(name).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
    text = re.sub(r"_+", "_", text).strip("_")
    return text if text else "columna"


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve una copia del DataFrame con nombres de columnas normalizados.

    Solo aplica normalización técnica (espacios, mayúsculas, separadores,
    acentos). No renombra columnas según catálogos de negocio.

    Parameters
    ----------
    df:
        DataFrame de entrada.

    Returns
    -------
    pandas.DataFrame
        Copia con columnas renombradas de forma técnica.
    """
    new_names: list[str] = []
    seen: dict[str, int] = {}
    for col in df.columns:
        base = _normalize_column_name(col)
        if base not in seen:
            seen[base] = 0
            new_names.append(base)
        else:
            seen[base] += 1
            new_names.append(f"{base}_{seen[base]}")

    out = df.copy()
    out.columns = new_names
    return out
