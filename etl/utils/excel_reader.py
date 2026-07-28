"""Lector reutilizable de archivos Excel binarios (.xlsb)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_xlsb(
    file_path: Path | str,
    *,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    """
    Abre un archivo ``.xlsb`` y lo devuelve como :class:`pandas.DataFrame`.

    No aplica reglas de negocio, limpieza ni renombre de columnas.
    Solo valida existencia y realiza la lectura técnica.

    Parameters
    ----------
    file_path:
        Ruta al archivo ``.xlsb``.
    sheet_name:
        Nombre o índice de la hoja a leer (default: primera hoja).

    Returns
    -------
    pandas.DataFrame
        Contenido crudo de la hoja solicitada.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValueError
        Si la extensión no es ``.xlsb``.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Archivo fuente no encontrado: {path}")

    if not path.is_file():
        raise FileNotFoundError(f"La ruta no es un archivo: {path}")

    if path.suffix.lower() != ".xlsb":
        raise ValueError(
            f"Se esperaba un archivo .xlsb; recibido: {path.suffix!r} ({path})"
        )

    return pd.read_excel(path, sheet_name=sheet_name, engine="pyxlsb")
