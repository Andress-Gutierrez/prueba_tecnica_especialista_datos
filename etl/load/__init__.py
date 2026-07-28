"""
Capa de carga ETL (orquestación).

Separa la orquestación de la persistencia: no contiene SQL ni acceso directo
a PostgreSQL. La persistencia se delega en ``repository.*``.
"""

from etl.load.loader import LoadOrchestrator, run_load

__all__ = [
    "LoadOrchestrator",
    "run_load",
]
