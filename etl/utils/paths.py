"""Resolución de rutas del proyecto sin hardcodear rutas absolutas."""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """
    Devuelve la raíz del repositorio.

    Se calcula a partir de la ubicación de este módulo:
    ``etl/utils/paths.py`` → subir dos niveles hasta la raíz.
    """
    return Path(__file__).resolve().parents[2]


def get_raw_dir(project_root: Path | None = None) -> Path:
    """
    Devuelve la carpeta ``data/raw`` relativa a la raíz del proyecto.

    Parameters
    ----------
    project_root:
        Raíz del proyecto. Si es ``None``, se resuelve con
        :func:`get_project_root`.
    """
    root = project_root if project_root is not None else get_project_root()
    return root / "data" / "raw"
