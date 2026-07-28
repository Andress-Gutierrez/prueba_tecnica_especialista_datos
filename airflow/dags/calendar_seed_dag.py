"""
DAG independiente para poblar el calendario corporativo (master data).

No ejecuta ETL comercial ni reglas de negocio del pipeline.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

_DAG_DOC_MD = """
### Objetivo

Mantener el calendario corporativo oficial en `dwh.dim_tiempo` a partir de la
API oficial de festivos de Colombia.

### Alcance

- Consume la API de festivos con variables de entorno.
- Inserta/actualiza el calendario en `dim_tiempo` de forma idempotente.
- No ejecuta el ETL comercial.

### Ejecucion

Manual (`schedule=None`).
"""


def _run_calendar_seed() -> None:
    """Ejecuta el seeder del calendario corporativo."""
    from etl.calendar import run_calendar_seed_from_env

    run_calendar_seed_from_env()


with DAG(
    dag_id="calendar_seed_dag",
    description="Puebla/actualiza calendario corporativo oficial en dwh.dim_tiempo.",
    doc_md=_DAG_DOC_MD,
    start_date=datetime(2026, 7, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["calendar", "master_data", "dwh"],
    default_args={
        "owner": "data_engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(minutes=60),
    },
) as dag:
    seed_calendar = PythonOperator(
        task_id="seed_calendar_dim_tiempo",
        python_callable=_run_calendar_seed,
    )
