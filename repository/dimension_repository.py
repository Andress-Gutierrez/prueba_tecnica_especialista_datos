"""
Contrato e infraestructura de persistencia para dimensiones.

Subfase 4.4B.2: motor genérico configurable por dimensión.
Única dimensión cableada: ``dwh.dim_tiempo`` (API pública 4.4B.1 intacta).
Sin hechos ni reglas de negocio.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import pandas as pd
from psycopg import Connection, sql
from psycopg.rows import tuple_row

from repository.postgres import PostgresSettings, postgres_connection

DIM_TIEMPO_TABLE: str = "dim_tiempo"


@dataclass(frozen=True)
class PersistResult:
    """
    Resultado genérico de una solicitud de persistencia.

    Attributes
    ----------
    table_name:
        Tabla destino lógica.
    row_count:
        Filas procesadas (insertadas + actualizadas + omitidas seed).
    status:
        Estado de la solicitud.
    detail:
        Detalle opcional para trazabilidad.
    """

    table_name: str
    row_count: int
    status: str
    detail: str = ""


@dataclass(frozen=True)
class DimensionTableConfig:
    """
    Configuración declarativa de una dimensión para el motor genérico.

    Parameters
    ----------
    logical_name:
        Nombre lógico expuesto al Load (p. ej. ``dim_tiempo``).
    schema:
        Esquema PostgreSQL (p. ej. ``dwh``).
    table:
        Nombre físico de tabla.
    sk_column:
        Columna surrogate key.
    natural_key_columns:
        Columnas de clave natural para lookup.
    attribute_columns:
        Columnas de negocio (todas excepto la SK) en orden de INSERT.
    update_columns:
        Subconjunto actualizable en conflicto (no incluye SK).
    required_columns:
        Columnas obligatorias en el DataFrame de entrada.
    date_columns:
        Columnas a normalizar como ``date`` / ``None``.
    bool_columns:
        Columnas booleanas obligatorias (no nulas).
    optional_bool_columns:
        Columnas booleanas opcionales.
    optional_int_columns:
        Columnas enteras opcionales.
    optional_str_columns:
        Columnas texto opcionales.
    int_columns:
        Columnas enteras obligatorias.
    """

    logical_name: str
    schema: str
    table: str
    sk_column: str
    natural_key_columns: tuple[str, ...]
    attribute_columns: tuple[str, ...]
    update_columns: tuple[str, ...]
    required_columns: tuple[str, ...]
    date_columns: tuple[str, ...] = ()
    bool_columns: tuple[str, ...] = ()
    optional_bool_columns: tuple[str, ...] = ()
    optional_int_columns: tuple[str, ...] = ()
    optional_str_columns: tuple[str, ...] = ()
    int_columns: tuple[str, ...] = ()

    @property
    def qualified_table(self) -> str:
        """Nombre calificado ``schema.table`` (solo para mensajes)."""
        return f"{self.schema}.{self.table}"


# Configuración específica de dim_tiempo (única dimensión habilitada).
DIM_TIEMPO_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name=DIM_TIEMPO_TABLE,
    schema="dwh",
    table="dim_tiempo",
    sk_column="sk_tiempo",
    natural_key_columns=("periodo_yyyymm", "fecha"),
    attribute_columns=(
        "fecha",
        "anio",
        "mes",
        "dia",
        "periodo_yyyymm",
        "nombre_mes",
        "dia_semana",
        "es_dia_habil",
        "es_festivo_co",
        "es_fin_semana",
    ),
    update_columns=(
        "anio",
        "mes",
        "dia",
        "nombre_mes",
        "dia_semana",
        "es_dia_habil",
        "es_festivo_co",
        "es_fin_semana",
    ),
    required_columns=(
        "anio",
        "mes",
        "periodo_yyyymm",
        "es_dia_habil",
        "es_festivo_co",
    ),
    date_columns=("fecha",),
    bool_columns=("es_dia_habil", "es_festivo_co"),
    optional_bool_columns=("es_fin_semana",),
    optional_int_columns=("dia", "dia_semana"),
    optional_str_columns=("nombre_mes",),
    int_columns=("anio", "mes", "periodo_yyyymm"),
)


class DimensionRepository(ABC):
    """Puerto de persistencia de dimensiones."""

    @abstractmethod
    def persist_dimension(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """
        Persiste filas de una dimensión.

        Parameters
        ----------
        table_name:
            Nombre lógico de la dimensión (``dim_*``).
        frame:
            DataFrame a persistir.

        Returns
        -------
        PersistResult
            Resultado de la operación de repositorio.
        """


class GenericDimensionRepository(DimensionRepository):
    """
    Motor reutilizable de persistencia dimensional.

    Recibe una ``DimensionTableConfig`` y ejecuta lookup / insert / update
    parametrizados sin duplicar SQL por dimensión.
    """

    def __init__(
        self,
        settings: PostgresSettings,
        config: DimensionTableConfig,
    ) -> None:
        self._settings = settings
        self._config = config

    def persist_dimension(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """
        Persiste la dimensión definida en ``config``.

        Parameters
        ----------
        table_name:
            Debe coincidir con ``config.logical_name``.
        frame:
            DataFrame alineado a la configuración.

        Returns
        -------
        PersistResult
            Conteos de inserción/actualización/omisión de seed.

        Raises
        ------
        ValueError
            Si el nombre lógico no coincide o faltan columnas requeridas.
        """
        if table_name != self._config.logical_name:
            raise ValueError(
                "GenericDimensionRepository configurado para "
                f"{self._config.logical_name!r}; recibido {table_name!r}."
            )
        self._validate_frame(frame)

        inserted = 0
        updated = 0
        skipped_seed = 0

        with postgres_connection(self._settings) as connection:
            for row in frame.to_dict(orient="records"):
                action = self._persist_row(connection, row)
                if action == "inserted":
                    inserted += 1
                elif action == "updated":
                    updated += 1
                else:
                    skipped_seed += 1

        total = inserted + updated + skipped_seed
        return PersistResult(
            table_name=self._config.logical_name,
            row_count=total,
            status="persisted",
            detail=(
                f"inserted={inserted}; updated={updated}; "
                f"skipped_sk0={skipped_seed}"
            ),
        )

    def _validate_frame(self, frame: pd.DataFrame) -> None:
        """Valida columnas mínimas requeridas por la configuración."""
        missing = [c for c in self._config.required_columns if c not in frame.columns]
        if missing:
            raise ValueError(
                f"{self._config.logical_name}: faltan columnas obligatorias: "
                + ", ".join(missing)
            )

    def _persist_row(self, connection: Connection, row: Mapping[str, Any]) -> str:
        """Inserta o actualiza una fila; omite preservación de sk=0."""
        cfg = self._config
        payload = self._normalize_row(row)
        sk_value = payload[cfg.sk_column]
        if sk_value == 0:
            return "skipped_seed"

        nk_values = tuple(payload[col] for col in cfg.natural_key_columns)
        existing_sk = self._lookup_sk(connection, nk_values)
        if existing_sk == 0:
            return "skipped_seed"

        if existing_sk is not None:
            self._update_row(connection, existing_sk, payload)
            return "updated"

        sk = sk_value if sk_value is not None else self._next_sk(connection)
        self._insert_row(connection, int(sk), payload)
        return "inserted"

    def _normalize_row(self, row: Mapping[str, Any]) -> dict[str, Any]:
        """Normaliza tipos Python/SQL según la configuración."""
        cfg = self._config
        payload: dict[str, Any] = {}

        sk_raw = row.get(cfg.sk_column)
        if sk_raw is None or (isinstance(sk_raw, float) and pd.isna(sk_raw)) or pd.isna(sk_raw):
            payload[cfg.sk_column] = None
        else:
            payload[cfg.sk_column] = int(sk_raw)

        for col in cfg.attribute_columns:
            raw = row.get(col)
            if col in cfg.date_columns:
                payload[col] = _as_date_or_none(raw)
            elif col in cfg.bool_columns:
                payload[col] = bool(raw)
            elif col in cfg.optional_bool_columns:
                payload[col] = _as_optional_bool(raw)
            elif col in cfg.int_columns:
                payload[col] = int(raw)
            elif col in cfg.optional_int_columns:
                payload[col] = _as_optional_int(raw)
            elif col in cfg.optional_str_columns:
                payload[col] = _as_optional_str(raw)
            else:
                payload[col] = None if _is_na(raw) else raw
        return payload

    def _lookup_sk(
        self,
        connection: Connection,
        nk_values: Sequence[Any],
    ) -> int | None:
        """Resuelve SK existente por clave natural."""
        cfg = self._config
        conditions = sql.SQL(" AND ").join(
            sql.SQL("{} IS NOT DISTINCT FROM %s").format(sql.Identifier(col))
            for col in cfg.natural_key_columns
        )
        query = sql.SQL("SELECT {sk} FROM {schema}.{table} WHERE {conds}").format(
            sk=sql.Identifier(cfg.sk_column),
            schema=sql.Identifier(cfg.schema),
            table=sql.Identifier(cfg.table),
            conds=conditions,
        )
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(query, tuple(nk_values))
            found = cursor.fetchone()
        if found is None:
            return None
        return int(found[0])

    def _next_sk(self, connection: Connection) -> int:
        """Obtiene el siguiente surrogate key disponible."""
        cfg = self._config
        query = sql.SQL(
            "SELECT COALESCE(MAX({sk}), 0) + 1 FROM {schema}.{table}"
        ).format(
            sk=sql.Identifier(cfg.sk_column),
            schema=sql.Identifier(cfg.schema),
            table=sql.Identifier(cfg.table),
        )
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(query)
            found = cursor.fetchone()
        return int(found[0]) if found is not None else 1

    def _insert_row(
        self,
        connection: Connection,
        sk_value: int,
        payload: Mapping[str, Any],
    ) -> None:
        """Inserta una fila nueva según la configuración."""
        cfg = self._config
        columns = (cfg.sk_column, *cfg.attribute_columns)
        col_ids = sql.SQL(", ").join(sql.Identifier(c) for c in columns)
        placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in columns)
        query = sql.SQL(
            "INSERT INTO {schema}.{table} ({cols}) VALUES ({vals})"
        ).format(
            schema=sql.Identifier(cfg.schema),
            table=sql.Identifier(cfg.table),
            cols=col_ids,
            vals=placeholders,
        )
        values = (sk_value, *(payload[c] for c in cfg.attribute_columns))
        with connection.cursor() as cursor:
            cursor.execute(query, values)

    def _update_row(
        self,
        connection: Connection,
        sk_value: int,
        payload: Mapping[str, Any],
    ) -> None:
        """Actualiza atributos de negocio sin tocar sk=0."""
        cfg = self._config
        assignments = sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(col))
            for col in cfg.update_columns
        )
        query = sql.SQL(
            "UPDATE {schema}.{table} SET {assigns} "
            "WHERE {sk} = %s AND {sk} <> 0"
        ).format(
            schema=sql.Identifier(cfg.schema),
            table=sql.Identifier(cfg.table),
            assigns=assignments,
            sk=sql.Identifier(cfg.sk_column),
        )
        values = tuple(payload[c] for c in cfg.update_columns) + (sk_value,)
        with connection.cursor() as cursor:
            cursor.execute(query, values)


class DimTiempoRepository(DimensionRepository):
    """
    Fachada pública de ``dim_tiempo`` (API 4.4B.1).

    Delega en ``GenericDimensionRepository`` + ``DIM_TIEMPO_CONFIG``.
    """

    def __init__(self, settings: PostgresSettings) -> None:
        self._inner = GenericDimensionRepository(settings, DIM_TIEMPO_CONFIG)

    def persist_dimension(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """
        Persiste únicamente ``dim_tiempo``.

        Parameters
        ----------
        table_name:
            Debe ser ``dim_tiempo``.
        frame:
            Columnas alineadas al DDL de ``dwh.dim_tiempo``.

        Returns
        -------
        PersistResult
            Conteos de inserción/actualización.
        """
        return self._inner.persist_dimension(table_name, frame)


class UnimplementedDimensionRepository(DimensionRepository):
    """Stub histórico 4.4A; preferir ``DimTiempoRepository`` para dim_tiempo."""

    def persist_dimension(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """No escribe en PostgreSQL."""
        return PersistResult(
            table_name=table_name,
            row_count=int(len(frame.index)),
            status="not_implemented",
            detail="Usar DimTiempoRepository para dim_tiempo.",
        )


def _is_na(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _as_date_or_none(value: Any) -> date | None:
    if _is_na(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.date()


def _as_optional_int(value: Any) -> int | None:
    if _is_na(value):
        return None
    return int(value)


def _as_optional_str(value: Any) -> str | None:
    if _is_na(value):
        return None
    text = str(value).strip()
    return text if text else None


def _as_optional_bool(value: Any) -> bool | None:
    if _is_na(value):
        return None
    return bool(value)
