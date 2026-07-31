# Prueba Técnica — Especialista de Datos

Proceso ETL y Visualización para análisis comercial (Ventas, Presupuesto, Gestión TMK Outbound).

Pipeline objetivo:

```
Excel (.xlsb) → Python ETL → Apache Airflow → PostgreSQL → Power BI
```

**Estado actual:** Fase 5 **cerrada** (Subfase **5.5.3** consolidación calendario corporativo).  
Siguiente fase autorizada: **Fase 6 — Power BI**.

---

## Arquitectura implementada

| Componente | Estado |
|------------|--------|
| Docker Compose + PostgreSQL 16 | ✅ Operativo |
| Base de datos `dwh_comercial` (DW) | ✅ Oficial |
| Esquema `dwh` + dims/hechos | ✅ DDL/DML |
| ETL Python (Extract→…→Validation+Logging) | ✅ Congelado |
| Apache Airflow 3.1.3 (`LocalExecutor`) | ✅ Infraestructura 5.1 |
| DAG `etl_comercial_pipeline` (PythonOperator + políticas 5.3) | ✅ Validado (5.4 Success) |
| DAG `calendar_seed_dag` (Master Data calendario) | ✅ Oficial (`dim_tiempo`) |
| Validación operacional integral | ✅ `docs/entregables/Validacion_Operacional.md` |
| Power BI | ⏳ Fase 6 |

---

## Estructura del proyecto

```
prueba_tecnica_especialista_datos/
├── docker-compose.yml
├── replace.env               # Plantilla de variables (copiar a .env)
├── requirements.txt          # Dependencias ETL (sin Airflow)
├── data/
│   └── raw/                  # Fuentes .xlsb (inmutables)
├── docs/
│   ├── analisis/
│   ├── arquitectura/         # ETL + Airflow + catálogo de reglas
│   ├── entregables/
│   └── modelo/
├── sql/
│   ├── ddl/
│   └── dml/
├── etl/
│   ├── extract/
│   ├── transform/
│   ├── business_rules/
│   ├── load/
│   ├── calendar/             # Master Data calendario (API festivos → dim_tiempo)
│   ├── utils/
│   ├── pipeline.py
│   └── validation.py         # Validación DW post-carga
├── repository/               # Persistencia (Repository Pattern)
├── scripts/                  # CLI: ETL, calendar seed, DDL/DML, validate_dw
├── airflow/
│   ├── dags/                 # etl_comercial_pipeline, calendar_seed_dag
│   ├── logs/
│   ├── plugins/
│   └── config/
├── logs/                     # Logs operativos del ETL
├── notebooks/
├── powerbi/                  # Fase 6
└── tests/
```

---

## Requisitos

- Docker Desktop (o Docker Engine + Compose v2)
- PowerShell (Windows)
- Archivo `.env` (copiar desde `replace.env`)
- Python **3.10+** (recomendado **3.12**) — solo si se ejecuta el ETL por consola (ver sección siguiente)

Flujo de configuración:

```text
replace.env
  ↓
.env
```

---

## Entorno Python local (solo para ejecución por consola)

Existen **dos contextos de ejecución** y solo uno requiere instalar dependencias manualmente:

| Contexto | ¿Requiere venv / pip install? |
|----------|-------------------------------|
| DAGs vía Airflow (Docker) | **No.** La imagen `apache/airflow:3.1.3` trae Python 3.12 y las dependencias del ETL se instalan automáticamente al arrancar los contenedores (`_PIP_ADDITIONAL_REQUIREMENTS` en `docker-compose.yml`) |
| ETL / seeder por consola (`python -m scripts...`) | **Sí.** Crear venv e instalar `requirements.txt` |

Para la ejecución por consola, después de clonar el repositorio y antes de ejecutar cualquier script:

```powershell
# Verificar versión (requiere 3.10+, recomendado 3.12)
python --version

# Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias del ETL
pip install -r requirements.txt
```

Notas:

- El proyecto usa sintaxis moderna de tipos (`int | None`), por lo que **Python 3.10 es el mínimo**. Se recomienda 3.12 para alinear el host con la imagen de Airflow.
- `requirements.txt` **no incluye Apache Airflow**: Airflow solo corre dentro de Docker.
- `_PIP_ADDITIONAL_REQUIREMENTS` es una práctica de desarrollo local; en producción se construiría una imagen propia con `pip install -r requirements.txt` en build.

---

## Orden de ejecución operativo

```text
1. Copiar replace.env → .env y completar secretos (incl. FESTIVOS_API_KEY)
2. (Solo ejecución por consola) Crear venv Python 3.10+ e instalar requirements.txt
3. docker compose up airflow-init && docker compose up -d
4. Aplicar DDL/DML si aplica (scripts/run_ddl.ps1, run_dml.ps1)
5. Ejecutar calendar_seed_dag (o: python -m scripts.run_calendar_seed)
6. Ejecutar etl_comercial_pipeline (o: python -m scripts.run_etl_pipeline)
7. Revisar validación DW / logs/
```

---

## Docker — PostgreSQL (Data Warehouse)

| Recurso | Valor |
|---------|-------|
| Imagen | `postgres:16-alpine` |
| Contenedor | `prueba_tecnica_postgres` |
| Volumen | `prueba_tecnica_postgres_data` |
| Base DW | `dwh_comercial` |
| Red | `prueba_tecnica_net` |
| Puerto host | `POSTGRES_PORT` (default `5432`) |

---

## Docker — Apache Airflow (Subfase 5.1)

| Recurso | Valor |
|---------|-------|
| Imagen fija | `apache/airflow:3.1.3` |
| Executor | `LocalExecutor` |
| Servicios | `airflow-init`, `airflow-webserver`, `airflow-scheduler`, `airflow-dag-processor` |
| Metadata DB | PostgreSQL DB `airflow` (misma instancia; distinta de `dwh_comercial`) |
| UI / API | Servicio `airflow-webserver` (comando Airflow 3.1: `api-server`) |
| URL Web UI | http://localhost:8080 |
| Usuario admin (ejemplo) | `airflow` |
| Password admin (ejemplo) | `airflow` |

**Importante:** las credenciales `airflow` / `airflow` son de **ejemplo** para desarrollo local. Cámbielas en `.env` (`_AIRFLOW_WWW_USER_USERNAME` / `_AIRFLOW_WWW_USER_PASSWORD`) antes de cualquier uso real.

No se incluyen Redis, workers Celery ni Flower.

---

## Cómo levantar la infraestructura

Desde la **raíz del proyecto**:

```powershell
Copy-Item replace.env .env
# Editar POSTGRES_PASSWORD, claves Airflow y FESTIVOS_API_KEY en .env
# Si el password de Postgres tiene caracteres especiales (!, @, #, ...),
# codifíquelos en AIRFLOW__DATABASE__SQL_ALCHEMY_CONN (ej. ! -> %21)

# Inicializar metadata + usuario admin (una vez / idempotente)
docker compose up airflow-init

# Levantar Postgres + Web UI + Scheduler + Dag Processor
docker compose up -d

docker compose ps
```

Abrir en el navegador: **http://localhost:8080**  
Login de ejemplo: usuario `airflow` / password `airflow`.

Detener (conserva volúmenes):

```powershell
docker compose down
```

---

## DAG ETL (Subfases 5.2 / 5.3)

| Campo | Valor |
|-------|-------|
| Ubicación | `airflow/dags/etl_comercial_pipeline.py` |
| `dag_id` | `etl_comercial_pipeline` |
| Operador | `PythonOperator` (única tarea) |
| Invocación | `etl.pipeline.run_pipeline` (función pública del ETL) |
| Schedule | `None` (solo ejecución manual) |
| Owner | `data_engineering` |
| Tags | `etl`, `dwh` |

El DAG **reutiliza el ETL existente** y **no implementa lógica propia** (no transforma datos, no aplica reglas, no ejecuta SQL del DW).

### Políticas operativas (Subfase 5.3)

| Política | Valor |
|----------|-------|
| Reintentos | `retries = 2` |
| Delay entre reintentos | `retry_delay = 5 minutos` |
| Timeout de ejecución | `execution_timeout = 60 minutos` |
| Concurrencia de runs | `max_active_runs = 1` |
| Concurrencia de tareas | `max_active_tasks = 1` |

### Restricciones del DAG

- Una sola tarea; no divide el pipeline
- Sin schedule/cron automático (ejecución manual)
- Sin Connections, Variables, Pools, SLA ni notificaciones
- No modifica parámetros ni lógica del ETL

### Cómo visualizarlo

1. Abrir http://localhost:8080
2. Iniciar sesión con las credenciales de ejemplo
3. Buscar el DAG `etl_comercial_pipeline`
4. Revisar la documentación del DAG en la UI (objetivo, flujo, qué ejecuta / qué no hace)

### Cómo ejecutarlo manualmente

1. En la UI, localizar `etl_comercial_pipeline`
2. Quitar la pausa (unpause) si está pausado
3. Disparar un run manual (Trigger DAG)
4. Revisar el estado de la tarea `run_etl_pipeline` en Airflow y, si aplica, los logs del ETL en `logs/`
5. Revisar evidencia documental: `docs/entregables/Validacion_Operacional.md`

---

## DAG calendario corporativo (Subfase 5.6)

| Campo | Valor |
|-------|-------|
| Ubicación | `airflow/dags/calendar_seed_dag.py` |
| `dag_id` | `calendar_seed_dag` |
| Operador | `PythonOperator` (única tarea) |
| Invocación | `etl.calendar.run_calendar_seed_from_env` |
| Schedule | `None` (solo ejecución manual) |
| Rol | Poblar/actualizar `dwh.dim_tiempo` como Master Data |

Variables de entorno requeridas (`.env`, plantilla en `replace.env`):
- `FESTIVOS_API_URL`
- `FESTIVOS_API_KEY`
- `CALENDAR_START_YEAR`
- `CALENDAR_END_YEAR`

Principios operativos:
- **La única fuente oficial del calendario corporativo es `dim_tiempo`, poblada mediante `calendar_seed_dag`.**
- el calendario se obtiene **solo** desde la API oficial `festivos.com.co` (vía el seeder);
- el ETL comercial **no consume API** de festivos;
- el ETL comercial valida al inicio que exista calendario oficial cargado;
- Presupuesto lee días hábiles exclusivamente desde `dim_tiempo.es_habil`;
- el calendario se gestiona de forma idempotente (re-ejecutar no duplica fechas).

Ejecución manual (opcional desde consola):

```powershell
python -m scripts.run_calendar_seed
```

---

## Validación operacional (Subfase 5.4)

Evidencia de cierre de Fase 5: [`docs/entregables/Validacion_Operacional.md`](docs/entregables/Validacion_Operacional.md).

Incluye checklist de infraestructura, metadatos del DAG, ejecución manual en **Success**, integridad del Data Warehouse y logging.

## Hardening operacional hechos (Subfase 5.5.2)

Estrategia oficial del proyecto para tablas de hechos:

```text
FULL LOAD
  ↓
TRUNCATE TABLE fact_xxx
  ↓
INSERT
```

Aplica únicamente a `fact_ventas`, `fact_presupuesto` y `fact_gestion_tmk`.

Justificación técnica breve:
- garantiza idempotencia en corridas repetidas sobre el mismo corte;
- evita duplicados por acumulación append-only;
- es coherente con una prueba técnica Full Load;
- preserva la arquitectura aprobada (sin rediseño ETL, sin incremental, sin UPSERT en hechos).

El ETL permanece ejecutable de forma autónoma:

```powershell
python -m scripts.run_etl_pipeline
```

---

## Cómo ejecutar los DDL / DML / validación DW

```powershell
.\scripts\run_ddl.ps1
.\scripts\run_dml.ps1
.\scripts\validate_dw.ps1
```

---

## Roadmap

| Fase | Nombre | Estado |
|------|--------|--------|
| 0–3 | Preparación → PostgreSQL | ✅ |
| 4 | ETL Python | ✅ Cerrada |
| 5.0 | Arquitectura Airflow | ✅ |
| 5.1 | Infraestructura Docker + Airflow | ✅ |
| **5.2** | **Primer DAG ETL** | **✅ Implementada** |
| **5.3** | **Operación del DAG** | **✅ Implementada** |
| **5.4** | **Validación operacional** | **✅ Completada** |
| **5.5.1** | **Auditoría de hardening operacional** | **✅ Completada** |
| **5.5.2** | **Idempotencia de hechos (TRUNCATE + INSERT)** | **✅ Completada** |
| **5.5.3** | **Consolidación calendario corporativo** | **✅ Completada** |
| **5.6** | **Infraestructura calendario corporativo** | **✅ Implementada** |
| 6 | Power BI | Siguiente |
| 7 | Documentación final | Pendiente |

---

## Notas

- Documentos en `docs/modelo/` y capas ETL: **congelados**.
- Bitácora de estado: `PROJECT_STATE.md` (externa al repo).
- Arquitectura Airflow: `docs/arquitectura/03_Arquitectura_Airflow.md`.
