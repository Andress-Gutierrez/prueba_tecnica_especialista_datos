"""
Punto de entrada de la capa Load.

Orquesta dimensiones y luego hechos, sin SQL ni conexión a PostgreSQL.
La persistencia se delega íntegramente a ``repository.*``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import pandas as pd

from etl.load.dimension_loader import DimensionLoader
from etl.load.fact_loader import FactLoader
from repository.dimension_repository import DimensionRepository
from repository.dimension_repository import PersistResult
from repository.fact_repository import FactRepository


@dataclass(frozen=True)
class LoadReport:
    """
    Resumen de orquestación de carga (sin ejecución real en 4.4A).

    Attributes
    ----------
    dimensions:
        Resultados por tabla dimensión.
    facts:
        Resultados por tabla hecho.
    """

    dimensions: dict[str, PersistResult] = field(default_factory=dict)
    facts: dict[str, PersistResult] = field(default_factory=dict)


class LoadOrchestrator:
    """
    Orquestador raíz dims → hechos.

    Parameters
    ----------
    dimension_loader:
        Orquestador de dimensiones.
    fact_loader:
        Orquestador de hechos.
    """

    def __init__(
        self,
        dimension_loader: DimensionLoader,
        fact_loader: FactLoader,
    ) -> None:
        self._dimension_loader = dimension_loader
        self._fact_loader = fact_loader

    def run(
        self,
        dimension_frames: Mapping[str, pd.DataFrame],
        fact_frames: Mapping[str, pd.DataFrame],
    ) -> LoadReport:
        """
        Ejecuta el flujo de orquestación: dimensiones primero, hechos después.

        Parameters
        ----------
        dimension_frames:
            DataFrames de dimensiones indexados por nombre de tabla.
        fact_frames:
            DataFrames de hechos indexados por nombre de tabla.

        Returns
        -------
        LoadReport
            Resultados agregados de la orquestación.
        """
        dim_results = self._dimension_loader.load_all(dimension_frames)
        fact_results = self._fact_loader.load_all(fact_frames)
        return LoadReport(dimensions=dim_results, facts=fact_results)


def run_load(
    dimension_repositories: Mapping[str, DimensionRepository],
    fact_repositories: Mapping[str, FactRepository],
    dimension_frames: Mapping[str, pd.DataFrame],
    fact_frames: Mapping[str, pd.DataFrame],
) -> LoadReport:
    """
    Punto de entrada funcional de la capa Load.

    Construye los orquestadores y ejecuta dims → hechos.

    Parameters
    ----------
    dimension_repositories:
        Mapa nombre lógico → repositorio de dimensión.
    fact_repositories:
        Mapa nombre lógico → repositorio de hecho.
    dimension_frames:
        DataFrames de dimensiones.
    fact_frames:
        DataFrames de hechos.

    Returns
    -------
    LoadReport
        Resumen de la orquestación.
    """
    orchestrator = LoadOrchestrator(
        dimension_loader=DimensionLoader(dimension_repositories),
        fact_loader=FactLoader(fact_repositories),
    )
    return orchestrator.run(dimension_frames, fact_frames)
