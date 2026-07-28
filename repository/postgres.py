"""
Gestión exclusiva de la conexión a PostgreSQL.

Sin lógica de negocio y sin SQL de carga de dimensiones/hechos.
Provee settings, puerto abstracto y conexión efectiva con context manager.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator

import psycopg
from psycopg import Connection


@dataclass(frozen=True)
class PostgresSettings:
    """
    Parámetros de conexión a PostgreSQL.

    Attributes
    ----------
    host:
        Host del servidor.
    port:
        Puerto TCP.
    database:
        Nombre de la base de datos.
    user:
        Usuario.
    password:
        Contraseña (no se registra en logs desde esta capa).
    """

    host: str
    port: int
    database: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> PostgresSettings:
        """
        Construye settings desde variables ``POSTGRES_*``.

        Returns
        -------
        PostgresSettings
            Configuración tipada.

        Raises
        ------
        KeyError
            Si falta alguna variable requerida.
        ValueError
            Si ``POSTGRES_PORT`` no es entero.
        """
        return cls(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ["POSTGRES_PORT"]),
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )


class PostgresConnectionPort(ABC):
    """Puerto de conexión a PostgreSQL."""

    @abstractmethod
    def connect(self, settings: PostgresSettings) -> Connection:
        """
        Abre una conexión según ``settings``.

        Parameters
        ----------
        settings:
            Configuración tipada de PostgreSQL.

        Returns
        -------
        Connection
            Conexión psycopg.
        """

    @abstractmethod
    def close(self, connection: Connection) -> None:
        """
        Cierra una conexión previamente abierta.

        Parameters
        ----------
        connection:
            Objeto de conexión del driver.
        """


class PsycopgConnection(PostgresConnectionPort):
    """Implementación de conexión efectiva con psycopg 3."""

    def connect(self, settings: PostgresSettings) -> Connection:
        """Abre una conexión PostgreSQL parametrizada por ``settings``."""
        return psycopg.connect(
            host=settings.host,
            port=settings.port,
            dbname=settings.database,
            user=settings.user,
            password=settings.password,
        )

    def close(self, connection: Connection) -> None:
        """Cierra la conexión si permanece abierta."""
        if connection is not None and not connection.closed:
            connection.close()


@contextmanager
def postgres_connection(
    settings: PostgresSettings,
    port: PostgresConnectionPort | None = None,
) -> Iterator[Connection]:
    """
    Context manager de conexión PostgreSQL.

    Abre, entrega y cierra la conexión. Hace commit al salir sin error;
    rollback si ocurre excepción.

    Parameters
    ----------
    settings:
        Configuración tipada.
    port:
        Implementación del puerto de conexión. Por defecto ``PsycopgConnection``.

    Yields
    ------
    Connection
        Conexión lista para operaciones parametrizadas.
    """
    connector = port if port is not None else PsycopgConnection()
    connection = connector.connect(settings)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connector.close(connection)


# Compatibilidad con stubs de 4.4A (arquitectura intacta).
class UnimplementedPostgresConnection(PostgresConnectionPort):
    """Stub histórico 4.4A; preferir ``PsycopgConnection`` / ``postgres_connection``."""

    def connect(self, settings: PostgresSettings) -> Any:
        """Rechaza el uso del stub en favor de la conexión efectiva."""
        raise NotImplementedError(
            "Usar PsycopgConnection o postgres_connection; "
            f"settings.database={settings.database!r}"
        )

    def close(self, connection: Any) -> None:
        """No aplica sin conexión efectiva del stub."""
        raise NotImplementedError(
            "Usar PsycopgConnection o postgres_connection."
        )
