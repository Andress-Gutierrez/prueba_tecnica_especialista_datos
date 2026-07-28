"""
DAG de orquestación operativa del pipeline ETL comercial (Subfase 5.3).

Invoca exclusivamente ``etl.pipeline.run_pipeline`` mediante PythonOperator.
No contiene lógica de transformación, reglas de negocio ni SQL.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG

_DAG_DOC_MD = """
### Objetivo

Orquestar la ejecución del pipeline ETL comercial ya implementado y congelado,
sin incorporar lógica de negocio en Airflow.

### Flujo

Extract → Transform → Business Rules → Load → Validation → Logging

### Qué ejecuta

Una única tarea con `PythonOperator` que llama a `etl.pipeline.run_pipeline()`.

### Qué NO hace

- No transforma datos
- No aplica reglas de negocio
- No ejecuta SQL del Data Warehouse
- No abre conexiones manuales a PostgreSQL
- No reemplaza el ETL (solo lo orquesta)
"""


def _invoke_run_pipeline() -> None:
    """Inicia el ETL llamando al entrypoint público. Propaga excepciones."""
    from etl.pipeline import run_pipeline

    run_pipeline()


with DAG(
    dag_id="etl_comercial_pipeline",
    description=(
        "Orquesta el ETL comercial congelado "
        "(Extract → Transform → Business Rules → Load → Validation). "
        "No transforma datos ni aplica reglas de negocio."
    ),
    doc_md=_DAG_DOC_MD,
    start_date=datetime(2026, 7, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["etl", "dwh"],
    default_args={
        "owner": "data_engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(minutes=60),
    },
) as dag:
    run_etl_pipeline = PythonOperator(
        task_id="run_etl_pipeline",
        python_callable=_invoke_run_pipeline,
    )
