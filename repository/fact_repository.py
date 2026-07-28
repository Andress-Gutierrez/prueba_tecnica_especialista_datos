"""
Contrato e implementación de persistencia para hechos.

Subfase 4.5A/5.5.2: carga Full Load de ``fact_ventas``, ``fact_presupuesto`` y
``fact_gestion_tmk`` con estrategia TRUNCATE + INSERT por tabla.
Sin reglas de negocio. Usa ``postgres_connection``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from psycopg import Connection, sql
from psycopg.rows import tuple_row

from repository.dimension_repository import PersistResult
from repository.postgres import PostgresSettings, postgres_connection

_INSERT_BATCH_SIZE = 5000

__all__ = [
    "PersistResult",
    "FactRepository",
    "PostgresFactRepository",
    "UnimplementedFactRepository",
]


class FactRepository(ABC):
    """Puerto de persistencia de hechos."""

    @abstractmethod
    def persist_fact(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """Persiste filas de un hecho."""


class PostgresFactRepository(FactRepository):
    """
    Implementación de persistencia de un hecho vía TRUNCATE + INSERT parametrizado.

    Completa el puerto ``FactRepository`` aprobado en 4.4A (sin nueva capa).
    """

    def __init__(
        self,
        settings: PostgresSettings,
        *,
        logical_name: str,
        table: str,
        sk_column: str,
        columns: tuple[str, ...],
        required_columns: tuple[str, ...],
        schema: str = "dwh",
    ) -> None:
        self._settings = settings
        self._logical_name = logical_name
        self._table = table
        self._sk_column = sk_column
        self._columns = columns
        self._required_columns = required_columns
        self._schema = schema

    def persist_fact(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """
        Ejecuta carga Full Load del hecho configurado (TRUNCATE + INSERT).

        Asigna ``sk`` si falta y ``fecha_carga_dw`` si no viene en el frame.
        """
        if table_name != self._logical_name:
            raise ValueError(
                f"PostgresFactRepository configurado para {self._logical_name!r}; "
                f"recibido {table_name!r}."
            )
        missing = [c for c in self._required_columns if c not in frame.columns]
        if missing:
            raise ValueError(
                f"{self._logical_name}: faltan columnas obligatorias: "
                + ", ".join(missing)
            )

        inserted = 0
        with postgres_connection(self._settings) as connection:
            self._truncate_table(connection)
            next_sk = self._next_sk(connection)
            carga = datetime.now(timezone.utc).replace(tzinfo=None)
            batch: list[tuple[Any, ...]] = []
            for row in frame.to_dict(orient="records"):
                payload = self._normalize_row(row, carga)
                sk_value = payload.get(self._sk_column)
                if sk_value is None:
                    sk_value = next_sk
                    next_sk += 1
                payload[self._sk_column] = int(sk_value)
                batch.append(tuple(payload[c] for c in self._columns))
                if len(batch) >= _INSERT_BATCH_SIZE:
                    self._copy_rows(connection, batch)
                    inserted += len(batch)
                    batch.clear()
            if batch:
                self._copy_rows(connection, batch)
                inserted += len(batch)

        return PersistResult(
            table_name=self._logical_name,
            row_count=inserted,
            status="persisted",
            detail=f"full_load_truncate_insert={inserted}",
        )

    def _truncate_table(self, connection: Connection) -> None:
        """
        Vacía únicamente la tabla de hecho objetivo antes de insertar.

        No toca dimensiones, secuencias, índices ni FKs.
        """
        query = sql.SQL("TRUNCATE TABLE {schema}.{table}").format(
            schema=sql.Identifier(self._schema),
            table=sql.Identifier(self._table),
        )
        with connection.cursor() as cursor:
            cursor.execute(query)

    def _normalize_row(
        self,
        row: dict[str, Any],
        fecha_carga_dw: datetime,
    ) -> dict[str, Any]:
        """Normaliza valores de una fila de hecho."""
        payload: dict[str, Any] = {}
        for col in self._columns:
            if col == "fecha_carga_dw":
                raw = row.get(col)
                payload[col] = (
                    fecha_carga_dw if _is_na(raw) else pd.to_datetime(raw).to_pydatetime()
                )
                continue
            if col == self._sk_column:
                raw = row.get(col)
                payload[col] = None if _is_na(raw) else int(raw)
                continue
            raw = row.get(col)
            if _is_na(raw):
                payload[col] = None
            elif col.startswith("sk_") or col in {"cantidad"}:
                payload[col] = int(raw)
            elif col in {
                "valor_antes_iva",
                "cuotas",
                "terminales",
                "tecnologia",
                "tyt",
                "intentos",
            }:
                payload[col] = float(raw)
            else:
                text = str(raw).strip()
                payload[col] = text if text else None
        return payload

    def _next_sk(self, connection: Connection) -> int:
        """Siguiente surrogate key del hecho."""
        query = sql.SQL(
            "SELECT COALESCE(MAX({sk}), 0) + 1 FROM {schema}.{table}"
        ).format(
            sk=sql.Identifier(self._sk_column),
            schema=sql.Identifier(self._schema),
            table=sql.Identifier(self._table),
        )
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(query)
            found = cursor.fetchone()
        return int(found[0]) if found is not None else 1

    def _copy_rows(
        self,
        connection: Connection,
        rows: list[tuple[Any, ...]],
    ) -> None:
        """Carga filas por COPY para hechos de alto volumen."""
        col_ids = sql.SQL(", ").join(sql.Identifier(c) for c in self._columns)
        query = sql.SQL(
            "COPY {schema}.{table} ({cols}) FROM STDIN"
        ).format(
            schema=sql.Identifier(self._schema),
            table=sql.Identifier(self._table),
            cols=col_ids,
        )
        with connection.cursor() as cursor:
            with cursor.copy(query) as copy:
                for row in rows:
                    copy.write_row(row)


class UnimplementedFactRepository(FactRepository):
    """Stub histórico 4.4A; preferir fachadas 4.5A."""

    def persist_fact(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """No escribe en PostgreSQL."""
        return PersistResult(
            table_name=table_name,
            row_count=int(len(frame.index)),
            status="not_implemented",
            detail="Usar fachadas Fact*Repository (4.5A).",
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
