"""
Seeder de calendario corporativo en dwh.dim_tiempo.

Proceso independiente del ETL comercial.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from time import perf_counter

from psycopg.rows import tuple_row

from etl.calendar.festivos_client import (
    FestivosApiAuthError,
    FestivosApiError,
    fetch_festivos_by_year,
)
from etl.utils.logger import get_logger
from repository.postgres import PostgresSettings, postgres_connection

logger = get_logger("calendar_seed")


@dataclass(frozen=True)
class CalendarSeedResult:
    years: tuple[int, ...]
    festivos_obtenidos: int
    fechas_procesadas: int
    inserted: int
    updated: int
    elapsed_seconds: float


def run_calendar_seed_from_env() -> CalendarSeedResult:
    """
    Entry point para Airflow/CLI.

    Requiere variables:
    - FESTIVOS_API_URL
    - FESTIVOS_API_KEY
    - CALENDAR_START_YEAR (opcional, default anio actual-1)
    - CALENDAR_END_YEAR (opcional, default anio actual+1)
    """
    settings = PostgresSettings.from_env()
    api_url = os.environ["FESTIVOS_API_URL"].strip()
    api_key = os.environ["FESTIVOS_API_KEY"].strip()
    current_year = date.today().year
    start_year = int(os.environ.get("CALENDAR_START_YEAR", str(current_year - 1)))
    end_year = int(os.environ.get("CALENDAR_END_YEAR", str(current_year + 1)))
    return seed_calendar(
        settings=settings,
        api_url=api_url,
        api_key=api_key,
        start_year=start_year,
        end_year=end_year,
    )


def seed_calendar(
    *,
    settings: PostgresSettings,
    api_url: str,
    api_key: str,
    start_year: int,
    end_year: int,
) -> CalendarSeedResult:
    """Carga/actualiza calendario oficial en dim_tiempo de forma idempotente."""
    if start_year > end_year:
        raise ValueError("start_year no puede ser mayor que end_year.")

    started = perf_counter()
    years = tuple(range(start_year, end_year + 1))
    logger.info("Inicio calendar seed | years=%s", years)

    try:
        festivos_by_date: dict[date, str] = {}
        festivos_obtenidos = 0
        for year in years:
            fetched = fetch_festivos_by_year(
                base_url=api_url,
                api_key=api_key,
                year=year,
            )
            festivos_obtenidos += len(fetched)
            for item in fetched:
                festivos_by_date[item.fecha] = item.nombre_festivo

        fechas = _iter_dates(start_year, end_year)
        inserted, updated = _upsert_calendar_dates(
            settings=settings,
            fechas=fechas,
            festivos_by_date=festivos_by_date,
        )

        elapsed = perf_counter() - started
        logger.info("Anios consultados: %s", years)
        logger.info("Cantidad de festivos obtenidos: %s", festivos_obtenidos)
        logger.info("Cantidad de fechas procesadas: %s", len(fechas))
        logger.info("Resultados persistencia: inserted=%s | updated=%s", inserted, updated)
        logger.info("Tiempo de ejecucion calendar seed: %.2f s", elapsed)

        return CalendarSeedResult(
            years=years,
            festivos_obtenidos=festivos_obtenidos,
            fechas_procesadas=len(fechas),
            inserted=inserted,
            updated=updated,
            elapsed_seconds=elapsed,
        )
    except FestivosApiAuthError:
        logger.exception("Error de autenticacion al consumir API de festivos")
        raise
    except FestivosApiError:
        logger.exception("Error HTTP/red al consumir API de festivos")
        raise
    except Exception:
        logger.exception("Error no controlado en calendar seed")
        raise


def _iter_dates(start_year: int, end_year: int) -> list[date]:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    out: list[date] = []
    cursor = start
    while cursor <= end:
        out.append(cursor)
        cursor = cursor + timedelta(days=1)
    return out


def _upsert_calendar_dates(
    *,
    settings: PostgresSettings,
    fechas: list[date],
    festivos_by_date: dict[date, str],
) -> tuple[int, int]:
    inserted = 0
    updated = 0

    with postgres_connection(settings) as connection:
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(
                """
                SELECT COALESCE(MAX(sk_tiempo), 0) + 1
                FROM dwh.dim_tiempo
                """
            )
            next_sk = int(cursor.fetchone()[0])

            for fecha in fechas:
                es_festivo = fecha in festivos_by_date
                nombre_festivo = festivos_by_date.get(fecha)
                # Requerimiento funcional: solo domingo es fin de semana.
                es_fin_semana = fecha.weekday() == 6
                es_habil = (not es_fin_semana) and (not es_festivo)
                periodo = fecha.year * 100 + fecha.month
                dia_semana = fecha.weekday() + 1  # 1=lunes ... 7=domingo

                cursor.execute(
                    """
                    SELECT sk_tiempo
                    FROM dwh.dim_tiempo
                    WHERE fecha IS NOT DISTINCT FROM %s
                    """,
                    (fecha,),
                )
                found = cursor.fetchone()
                if found is None:
                    cursor.execute(
                        """
                        INSERT INTO dwh.dim_tiempo (
                            sk_tiempo,
                            fecha,
                            anio,
                            mes,
                            dia,
                            periodo_yyyymm,
                            nombre_mes,
                            dia_semana,
                            es_dia_habil,
                            es_festivo_co,
                            es_fin_semana,
                            es_festivo,
                            nombre_festivo,
                            es_habil
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            next_sk,
                            fecha,
                            fecha.year,
                            fecha.month,
                            fecha.day,
                            periodo,
                            fecha.strftime("%B"),
                            dia_semana,
                            es_habil,
                            es_festivo,
                            es_fin_semana,
                            es_festivo,
                            nombre_festivo,
                            es_habil,
                        ),
                    )
                    next_sk += 1
                    inserted += 1
                    continue

                cursor.execute(
                    """
                    UPDATE dwh.dim_tiempo
                    SET
                        anio = %s,
                        mes = %s,
                        dia = %s,
                        periodo_yyyymm = %s,
                        nombre_mes = %s,
                        dia_semana = %s,
                        es_dia_habil = %s,
                        es_festivo_co = %s,
                        es_fin_semana = %s,
                        es_festivo = %s,
                        nombre_festivo = %s,
                        es_habil = %s
                    WHERE fecha IS NOT DISTINCT FROM %s
                    """,
                    (
                        fecha.year,
                        fecha.month,
                        fecha.day,
                        periodo,
                        fecha.strftime("%B"),
                        dia_semana,
                        es_habil,
                        es_festivo,
                        es_fin_semana,
                        es_festivo,
                        nombre_festivo,
                        es_habil,
                        fecha,
                    ),
                )
                updated += 1

    return inserted, updated
