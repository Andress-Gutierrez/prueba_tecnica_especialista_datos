"""
Capa de repositorio (persistencia).

Aísla el acceso a PostgreSQL de la orquestación ETL. Sin reglas de negocio.
"""

from repository.postgres import (
    PostgresConnectionPort,
    PostgresSettings,
    PsycopgConnection,
    postgres_connection,
)

__all__ = [
    "PostgresConnectionPort",
    "PostgresSettings",
    "PsycopgConnection",
    "postgres_connection",
]

