"""
Orquestador de hechos (capa Load).

Subfase 4.5A: orquesta los tres hechos vía mapa de repositorios.
No contiene SQL ni lógica de negocio.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd

from repository.fact_repository import FactRepository, PersistResult

# Orden oficial alineado a ``01_Arquitectura_ETL.md`` §4.2.
FACT_LOAD_ORDER: tuple[str, ...] = (
    "fact_ventas",
    "fact_presupuesto",
    "fact_gestion_tmk",
)


class FactLoader:
    """
    Orquesta la carga de hechos vía repositorios por tabla.

    Parameters
    ----------
    repositories:
        Mapa ``nombre_lógico → FactRepository``.
    load_order:
        Orden de tablas. Por defecto el orden oficial del proyecto.
    """

    def __init__(
        self,
        repositories: Mapping[str, FactRepository],
        load_order: Sequence[str] | None = None,
    ) -> None:
        self._repositories: dict[str, FactRepository] = dict(repositories)
        self._load_order: tuple[str, ...] = tuple(
            load_order if load_order is not None else FACT_LOAD_ORDER
        )

    def load_one(self, table_name: str, frame: pd.DataFrame) -> PersistResult:
        """
        Solicita la persistencia de un hecho registrado.

        Raises
        ------
        ValueError
            Si el hecho no está registrado.
        """
        repository = self._repositories.get(table_name)
        if repository is None:
            raise ValueError(
                f"FactLoader: no hay repositorio registrado para {table_name!r}."
            )
        return repository.persist_fact(table_name, frame)

    def load_all(
        self,
        frames_by_table: Mapping[str, pd.DataFrame],
    ) -> dict[str, PersistResult]:
        """
        Orquesta la carga de hechos en el orden configurado.

        Solo procesa tablas presentes en ``frames_by_table`` y con repositorio.
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
