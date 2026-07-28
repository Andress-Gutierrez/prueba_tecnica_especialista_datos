# Validación Operacional Integral — Fase 5

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-07-28 |
| **Proyecto** | prueba_tecnica_especialista_datos |
| **Subfase** | 5.4 — Validación Operacional Integral |
| **Versión Airflow** | 3.1.3 |
| **Versión PostgreSQL** | 16 (imagen `postgres:16-alpine`) |
| **DAG validado** | `etl_comercial_pipeline` |
| **Run ID Success** | `manual__2026-07-28T06:34:38.855246+00:00` |

---

## 1. Objetivo

Verificar de extremo a extremo que la plataforma operativa (Docker + PostgreSQL + Airflow + ETL + Logging + Data Warehouse) funciona de forma coherente, sin modificar la implementación congelada del ETL ni del modelo físico.

---

## 2. Checklist y resultados

### 2.1 Infraestructura Docker

| Chequeo | Resultado | Evidencia |
|---------|-----------|-----------|
| PostgreSQL operativo | ✅ OK | Contenedor `prueba_tecnica_postgres` **healthy** |
| Airflow Init | ✅ OK | `prueba_tecnica_airflow_init` **Exited (0)** |
| Airflow Webserver | ✅ OK | `prueba_tecnica_airflow_webserver` **healthy**; `/api/v2/version` → `3.1.3` |
| Airflow Scheduler | ✅ OK | `prueba_tecnica_airflow_scheduler` **healthy** |
| Airflow Dag Processor | ✅ OK | `prueba_tecnica_airflow_dag_processor` **Up** |

### 2.2 Airflow — metadatos del DAG

| Chequeo | Resultado | Evidencia |
|---------|-----------|-----------|
| DAG visible | ✅ OK | `etl_comercial_pipeline` listado |
| Sin errores de parseo | ✅ OK | `has_import_errors = False`; `import_errors = {}` |
| PythonOperator | ✅ OK | Única tarea `run_etl_pipeline` → `PythonOperator` |
| Owner | ✅ OK | `data_engineering` |
| Tags | ✅ OK | `etl`, `dwh` |
| Schedule | ✅ OK | `None` / *Never, external triggers only* |
| `doc_md` | ✅ OK | Presente (`doc_md_len=506`, contiene sección Objetivo) |

### 2.3 Ejecución manual del DAG

| Chequeo | Resultado | Evidencia |
|---------|-----------|-----------|
| Trigger manual | ✅ OK | Run `manual__2026-07-28T06:34:38.855246+00:00` |
| Estado final | ✅ **Success** | `state = success` (fin `2026-07-28T06:38:34Z`) |
| Duración ETL | ✅ OK | ~217 s según `logs/latest.log` |

**Nota operativa:** la primera corrida falló por `Connection refused` hacia la Execution API (`localhost`). Se corrigió únicamente la variable de entorno `AIRFLOW__CORE__EXECUTION_API_SERVER_URL=http://airflow-webserver:8080/execution/` (sin cambiar Docker Compose, ETL ni DAG). La corrida posterior quedó en **Success**.

### 2.4 Data Warehouse

Validación vía `etl.validation.validate_data_warehouse` (solo SELECT):

| Chequeo | Resultado |
|---------|-----------|
| 13 dimensiones presentes | ✅ OK |
| 3 hechos presentes | ✅ OK |
| Integridad referencial / sin huérfanos | ✅ OK (`orphans=0`) |
| Miembro `sk=0` | ✅ OK (dims aplicables) |
| Dominio `dim_validez_venta` | ✅ OK (4 filas) |
| Resumen | ✅ **Validación DW: OK — 38 chequeos, 0 fallidos** |

Conteos observados al cierre de la corrida Success (referencia):

| Tabla | Filas |
|-------|------:|
| dim_tiempo | 62 |
| dim_region | 7 |
| dim_canal | 8 |
| dim_categoria | 5 |
| dim_jerarquia_comercial | 26 |
| dim_aliado | 43 |
| dim_unidad_gestion | 6 |
| dim_marca | 5 |
| dim_vendedor | 82 |
| dim_validez_venta | 4 |
| dim_campana | 32 |
| dim_segmento | 5 |
| dim_tipo_contacto | 14 |
| fact_ventas | 230 |
| fact_presupuesto | 609 |
| fact_gestion_tmk | 730 |

### 2.5 Logging

| Chequeo | Resultado | Evidencia |
|---------|-----------|-----------|
| Logs Airflow de la tarea | ✅ OK | `airflow/logs/.../attempt=1.log` (~5 KB) para el run Success |
| `logs/latest.log` | ✅ OK | Generado; refleja Inicio/Fin ETL y Validación DW OK |
| `logs/etl_YYYYMMDD_HHMMSS.log` | ✅ OK | `logs/etl_20260728_063456.log` |

---

## 3. Conclusión

La **Fase 5 — Apache Airflow** se considera **validada operacionalmente**.

- Infraestructura Docker estable
- DAG operativo con PythonOperator y políticas 5.3
- Ejecución manual en estado **Success**
- Data Warehouse íntegro (38/38 chequeos)
- Logging Airflow + ETL operativo

**Plataforma lista para la Fase 6 — Power BI** (consumo exclusivo desde PostgreSQL `dwh_comercial` / esquema `dwh`).

---

## 4. Restricciones respetadas

Durante la Subfase 5.4 no se modificaron:

- ETL (Extract / Transform / Business Rules / Load / Validation / Logging)
- SQL / modelo físico
- Repository
- Docker Compose
- Código del DAG
