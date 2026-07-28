"""
Orquestador de dimensiones (capa Load).

Subfase 4.4B.3: orquesta las 13 dimensiones vía mapa de repositorios.
No contiene SQL ni lógica de negocio; delega en Repository.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd

from repository.dimension_repository import (
    DIM_TIEMPO_TABLE,
    DimensionRepository,
    PersistResult,
)

# Orden oficial alineado a ``01_Arquitectura_ETL.md`` §4.1 / DDL 01–13.
DIMENSION_LOAD_ORDER: tuple[str, ...] = (
    "dim_tiempo",
    "dim_region",
    "dim_canal",
    "dim_categoria",
    "dim_jerarquia_comercial",
    "dim_aliado",
    "dim_unidad_gestion",
    "dim_marca",
    "dim_vendedor",
    "dim_validez_venta",
    "dim_campana",
    "dim_segmento",
    "dim_tipo_contacto",
)


class DimensionLoader:
    """
    Orquesta la carga de dimensiones vía repositorios por tabla.

    Parameters
    ----------
    repositories:
        Mapa ``nombre_lógico → DimensionRepository`` (p. ej. resultado de
        ``build_dimension_repositories``).
    load_order:
        Orden de tablas. Por defecto el orden oficial completo.
    """

    def __init__(
        self,
        repositories: Mapping[str, DimensionRepository],
        load_order: Sequence[str] | None = None,
    ) -> None:
        self._repositories: dict[str, DimensionRepository] = dict(repositories)
        self._load_order: tuple[str, ...] = tuple(
            load_order if load_order is not None else DIMENSION_LOAD_ORDER
        )

    def load_one(self, table_name: str, frame: pd.DataFrame) -> PersistResult:
        """
        Solicita la persistencia de una dimensión registrada.

        Parameters
        ----------
        table_name:
            Nombre lógico (``dim_*``).
        frame:
            DataFrame preparado para carga.

        Returns
        -------
        PersistResult
            Resultado reportado por el repositorio.

        Raises
        ------
        ValueError
            Si la dimensión no está registrada en el mapa de repositorios.
        """
        repository = self._repositories.get(table_name)
        if repository is None:
            raise ValueError(
                "DimensionLoader: no hay repositorio registrado para "
                f"{table_name!r}."
            )
        return repository.persist_dimension(table_name, frame)

    def load_dim_tiempo(self, frame: pd.DataFrame) -> PersistResult:
        """Atajo tipado para persistir ``dim_tiempo``."""
        return self.load_one(DIM_TIEMPO_TABLE, frame)

    def load_all(
        self,
        frames_by_table: Mapping[str, pd.DataFrame],
    ) -> dict[str, PersistResult]:
        """
        Orquesta la carga según ``load_order``.

        Solo procesa tablas presentes tanto en ``load_order`` como en
        ``frames_by_table`` y con repositorio registrado.
        """
        results: dict[str, PersistResult] = {}
        for table_name in self._load_order:
            if table_name not in frames_by_table:
                continue
            if table_name not in self._repositories:
                continue
            results[table_name] = self.load_one(
                table_name,
                frames_by_table[table_name],
            )
        return results
