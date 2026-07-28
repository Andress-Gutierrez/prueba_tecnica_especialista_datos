"""
Extractor de fuentes oficiales del Data Warehouse.

Conoce el inventario de archivos en ``data/raw`` e invoca el lector
``.xlsb``. No transforma, limpia ni renombra columnas.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from etl.utils.excel_reader import read_xlsb
from etl.utils.paths import get_raw_dir

# Inventario oficial de fuentes (nombres de archivo, no rutas absolutas).
SOURCE_FILES: dict[str, str] = {
    "ventas": "Ventas.xlsb",
    "presupuesto": "Presupuesto.xlsb",
    "registros": "Registros.xlsb",
}


def list_expected_sources() -> dict[str, str]:
    """
    Devuelve el inventario de fuentes oficiales.

    Returns
    -------
    dict[str, str]
        Mapa ``clave_lógica → nombre_de_archivo``.
    """
    return dict(SOURCE_FILES)


def resolve_source_path(raw_dir: Path, source_key: str) -> Path:
    """
    Resuelve la ruta de una fuente a partir de su clave lógica.

    Parameters
    ----------
    raw_dir:
        Directorio ``data/raw``.
    source_key:
        Clave lógica (``ventas``, ``presupuesto``, ``registros``).

    Returns
    -------
    pathlib.Path
        Ruta completa al archivo ``.xlsb``.

    Raises
    ------
    KeyError
        Si la clave no pertenece al inventario oficial.
    """
    try:
        filename = SOURCE_FILES[source_key]
    except KeyError as exc:
        known = ", ".join(sorted(SOURCE_FILES))
        raise KeyError(
            f"Fuente desconocida: {source_key!r}. Fuentes válidas: {known}"
        ) from exc

    return Path(raw_dir) / filename


def extract_source(
    source_key: str,
    *,
    raw_dir: Path | None = None,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    """
    Extrae una única fuente oficial como DataFrame crudo.

    Parameters
    ----------
    source_key:
        Clave lógica de la fuente.
    raw_dir:
        Carpeta ``data/raw``. Si es ``None``, se resuelve desde la raíz
        del proyecto.
    sheet_name:
        Hoja a leer (default: primera).

    Returns
    -------
    pandas.DataFrame
        Datos crudos sin transformación.
    """
    base = raw_dir if raw_dir is not None else get_raw_dir()
    path = resolve_source_path(base, source_key)
    return read_xlsb(path, sheet_name=sheet_name)


def extract_all_sources(
    *,
    raw_dir: Path | None = None,
    sheet_name: str | int = 0,
) -> dict[str, pd.DataFrame]:
    """
    Extrae todas las fuentes oficiales y las devuelve organizadas.

    Parameters
    ----------
    raw_dir:
        Carpeta ``data/raw``. Si es ``None``, se resuelve desde la raíz
        del proyecto.
    sheet_name:
        Hoja a leer en cada archivo (default: primera).

    Returns
    -------
    dict[str, pandas.DataFrame]
        Mapa ``clave_lógica → DataFrame`` crudo.

    Raises
    ------
    FileNotFoundError
        Si falta alguno de los archivos del inventario.
    """
    base = raw_dir if raw_dir is not None else get_raw_dir()
    frames: dict[str, pd.DataFrame] = {}

    for key in SOURCE_FILES:
        frames[key] = extract_source(
            key,
            raw_dir=base,
            sheet_name=sheet_name,
        )

    return frames
