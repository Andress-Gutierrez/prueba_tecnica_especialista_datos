# 03 — Arquitectura de Orquestación con Apache Airflow

----------------------------------------------------
ESTADO: ESPECIFICACIÓN OFICIAL — Subfase 5.0  
Documento de arquitectura de orquestación.  
**No contiene código Python, Docker, SQL ni DAGs.**  
Fuente de verdad para la implementación de la Fase 5.
----------------------------------------------------

Proyecto: prueba_tecnica_especialista_datos  
Fecha: 2026-07-27  
Autor: Cursor (Senior Software Developer)  
Revisión: Tech Lead / Project Owner

### Fuentes de diseño

- `docs/arquitectura/01_Arquitectura_ETL.md` (congelada — Fase 4)
- `docs/arquitectura/02_Catalogo_Reglas_Negocio.md` (congelado)
- Pre-Gate de infraestructura Fase 5 (`PROJECT_STATE.md`)
- Punto de entrada operativo: `scripts/run_etl_pipeline.py` (ETL congelado)

---

## 0. Principio rector (explícito)

Apache Airflow en este proyecto:

| Afirmación | Estado |
|------------|--------|
| Airflow **NO** contiene lógica de negocio | Obligatorio |
| Airflow **NO** transforma datos | Obligatorio |
| Airflow **NO** aplica reglas de negocio | Obligatorio |
| Airflow **NO** ejecuta SQL del Data Warehouse | Obligatorio |
| Airflow **NO** reemplaza el ETL | Obligatorio |
| Airflow **únicamente orquesta** la ejecución del pipeline existente | Obligatorio |
| El ETL sigue siendo ejecutable desde **consola** y desde **Airflow** sin modificaciones | Obligatorio |

El pipeline ETL (Extract → Transform → Business Rules → Load → Validation → Logging) permanece **congelado** y es la única unidad de procesamiento de datos.

---

## 1. Objetivo de Airflow dentro del proyecto

Proveer una capa de **orquestación, programación y monitoreo** para la ejecución del pipeline ETL ya implementado, de forma que:

1. Las corridas puedan programarse (calendario / disparo manual).
2. El estado de cada ejecución sea visible (éxito, fallo, duración).
3. Los reintentos y la notificación de fallos se gestionen a nivel de orquestación.
4. El Data Warehouse continúe siendo alimentado exclusivamente por el ETL Python existente.

Airflow es un **director de ejecución**, no un motor de transformación ni de persistencia analítica.

---

## 2. Alcance de la orquestación

### 2.1 Incluye (Fase 5)

- Definición arquitectónica e infraestructura de Airflow (subfases 5.1+).
- Un DAG (o conjunto mínimo de DAGs) cuya única responsabilidad de negocio-operativa sea **invocar** el entrypoint del ETL.
- Programación, monitoreo, reintentos y registro del estado de la corrida a nivel Airflow.
- Integración operativa con Docker / red / variables de entorno (sin alterar la lógica del ETL).
- Visibilidad operativa (UI Airflow + logs del ETL en `logs/`).

### 2.2 Excluye

- Cualquier lógica de Extract / Transform / Business Rules / Load / Validation dentro de Airflow.
- Escritura directa a tablas `dwh.*` desde tareas Airflow.
- Sustitución de `scripts/run_etl_pipeline.py` por un rediseño del pipeline.
- Power BI (Fase 6).
- Cambios al modelo dimensional o físico.

---

## 3. Responsabilidades exclusivas de Airflow

| Responsabilidad | Descripción |
|-----------------|-------------|
| Programación | Definir cuándo se dispara la corrida ETL. |
| Disparo | Iniciar el proceso/comando que ejecuta el pipeline congelado. |
| Observabilidad de corrida | Registrar estado de la tarea/DAG (queued, running, success, failed). |
| Reintentos de orquestación | Reintentar la **invocación** del pipeline según política definida (§11). |
| Dependencias de infraestructura | Esperar disponibilidad de PostgreSQL / servicios previos cuando aplique. |
| Aislamiento de roles | Separar “cuándo y si corre” de “cómo se procesan los datos”. |

---

## 4. Responsabilidades exclusivas del ETL

| Responsabilidad | Descripción |
|-----------------|-------------|
| Extract | Lectura de fuentes `.xlsb` inmutables. |
| Transform | Limpieza estructural y tipificación técnica. |
| Business Rules | Semántica de negocio catalogada (RN-*). |
| Load | Persistencia de dimensiones y hechos vía Repository. |
| Validation | Chequeos finales del Data Warehouse. |
| Logging operacional | Emisión de logs a consola + `logs/etl_YYYYMMDD_HHMMSS.log` + `logs/latest.log`. |
| Autonomía | Ejecución completa sin Airflow mediante consola. |

---

## 5. Flujo completo de ejecución

```
[Trigger]
  · Programación Airflow (schedule)
  · Disparo manual (UI / CLI Airflow)
  · Ejecución directa consola (sin Airflow)
        ↓
[Orquestación — solo si hay Airflow]
  · Scheduler selecciona el DAG
  · Task invoca el entrypoint ETL
        ↓
[Pipeline ETL congelado — siempre el mismo]
  Extract
    → Transform
    → Business Rules
    → Load (dims → hechos)
    → Validation
    → Logging operacional
        ↓
[Resultado]
  · Código de salida 0 → éxito de orquestación
  · Código de salida ≠ 0 → fallo de orquestación
        ↓
[Destino]
  PostgreSQL 16 — base `dwh_comercial` — esquema `dwh`
  Listo para consumo Power BI (Fase 6)
```

### Nota de equivalencia

La corrida iniciada por Airflow y la corrida iniciada por consola deben producir el **mismo contrato operativo**: mismo entrypoint, mismas variables `POSTGRES_*`, misma semántica de éxito/fallo, mismos artefactos de log del ETL.

---

## 6. Diagrama lógico del pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     CAPA ORQUESTACIÓN                       │
│                     (Apache Airflow)                        │
│  schedule / trigger → task → invoca entrypoint ETL          │
│  (sin transformaciones, sin reglas, sin SQL DW)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA ETL (CONGELADA)                     │
│              scripts/run_etl_pipeline.py                    │
│  Extract → Transform → Business Rules → Load → Validation   │
│              + Logging operacional (etl/utils/logger)       │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                ▼                             ▼
     ┌──────────────────┐          ┌──────────────────────┐
     │  data/raw/*.xlsb │          │  PostgreSQL (dwh.*)  │
     │   (inmutable)    │          │   Data Warehouse     │
     └──────────────────┘          └──────────────────────┘
                │
                ▼
     ┌──────────────────┐
     │ logs/etl_*.log   │
     │ logs/latest.log  │
     └──────────────────┘
```

---

## 7. Arquitectura de componentes

| Componente | Rol |
|------------|-----|
| Apache Airflow (Scheduler / API / UI) | Orquesta y monitorea. |
| DAG(s) en `airflow/dags/` | Declaran el flujo de orquestación; no procesan datos. |
| `airflow/config/` | Configuración de runtime Airflow. |
| `airflow/plugins/` | Extensiones opcionales; sin lógica de negocio del DW. |
| `airflow/logs/` | Logs propios del motor Airflow (distintos de `logs/` del ETL). |
| ETL Python (`etl/`, `repository/`, `scripts/`) | Procesamiento completo de datos. |
| PostgreSQL | Persistencia del Data Warehouse. |
| Docker Compose | Empaquetado/infraestructura de servicios (evolución en 5.1). |
| Variables de entorno | Configuración de conexión y runtime (sin hardcode de secretos). |

### 7.1 Calendario corporativo como Master Data

Se incorpora un DAG independiente de calendario (`calendar_seed_dag`) con
responsabilidad exclusiva de poblar/actualizar `dwh.dim_tiempo` usando la API
oficial de festivos de Colombia.

**La única fuente oficial del calendario corporativo es `dim_tiempo`, poblada
mediante `calendar_seed_dag`.**

Restricciones de arquitectura:

1. El ETL comercial no consume API de festivos.
2. El ETL comercial depende de `dim_tiempo` como única fuente de calendario
   (`es_habil` / `es_festivo` / `nombre_festivo`).
3. El DAG de calendario se ejecuta de forma manual (`schedule=None`) e
   independiente del DAG ETL comercial.
4. La API se configura solo mediante variables de entorno (`FESTIVOS_API_URL`,
   `FESTIVOS_API_KEY`, `CALENDAR_START_YEAR`, `CALENDAR_END_YEAR`) definidas
   en `replace.env` → `.env`.
5. No existe lógica duplicada de días hábiles/festivos en Business Rules.

---

## 8. Relación entre Docker, PostgreSQL, Airflow, ETL y Logging

```
Docker Compose (infraestructura)
├── Servicio PostgreSQL 16
│     └── Base dwh_comercial / esquema dwh
│           ▲
│           │  escritura/lectura solo vía ETL + Repository
│           │
├── Servicios Airflow (objetivo 5.1+)
│     └── DAG invoca entrypoint ETL
│           │
│           └── ETL (proceso)
│                 ├── lee data/raw
│                 ├── escribe dwh.*
│                 └── escribe logs/etl_*.log y logs/latest.log
│
└── Red compartida (objetivo 5.1)
      └── Airflow resuelve host de Postgres por nombre de servicio
          (no localhost desde contenedor)
```

### Separación de logs

| Origen | Ubicación | Propósito |
|--------|-----------|-----------|
| ETL | `logs/etl_YYYYMMDD_HHMMSS.log`, `logs/latest.log` | Traza operacional del pipeline de datos |
| Airflow | `airflow/logs/` | Traza del motor de orquestación (tasks/DAG) |

Ambas coexisten; Airflow **no sustituye** el logging del ETL.

---

## 9. Estrategia de ejecución del pipeline

1. **Entrypoint único:** `python -m scripts.run_etl_pipeline` (o equivalente operativo que invoque el mismo módulo sin alterar el ETL).
2. **Modo consola:** ejecución directa desde la raíz del proyecto, con `.env` / variables `POSTGRES_*`.
3. **Modo Airflow:** una task del DAG dispara el mismo entrypoint en un entorno con las mismas variables de conexión (ajustando el host según red Docker cuando corresponda).
4. **Sin fragmentación:** no se parte el pipeline en tasks Extract/Transform/Load dentro de Airflow en esta arquitectura; la unidad orquestada es el **pipeline completo**, preservando el orden y la atomicidad operativa ya validados en Fase 4.
5. **Idempotencia operativa:** la orquestación asume que el ETL ya implementa seeds/upserts/validaciones; Airflow no añade lógica compensatoria de datos.

---

## 10. Estrategia de manejo de errores

| Nivel | Responsable | Comportamiento |
|-------|-------------|----------------|
| Error de datos / reglas / carga / validación | ETL | Registra con `logger.exception()` / ERROR; retorna código de salida ≠ 0 |
| Error de invocación / entorno / timeout de task | Airflow | Marca la task/DAG como failed; aplica reintentos (§11) |
| Error de infraestructura (Postgres caído) | Orquestación + ops | No arrancar o fallar temprano; no “reparar” datos desde Airflow |

**Regla:** Airflow interpreta el resultado del proceso ETL; **no interpreta ni corrige** el contenido del Data Warehouse.

---

## 11. Estrategia de reintentos

1. Los reintentos de orquestación se configuran a nivel de **task/DAG** (número limitado, backoff).
2. Un reintento significa **volver a invocar** el pipeline completo, no reanudar una etapa interna desde Airflow.
3. No se definen reintentos selectivos por capa ETL (Extract/Transform/…) en Airflow.
4. La política concreta (reintentos, delay) se fijará en la Subfase 5.2 (DAG) sin alterar el código del ETL.
5. Reintentos infinitos están prohibidos por diseño.

---

## 12. Estrategia de logging

1. **ETL:** continúa emitiendo INFO / WARNING / ERROR a consola y a archivo por ejecución (`etl_YYYYMMDD_HHMMSS.log`) más `latest.log`.
2. **Airflow:** conserva sus propios logs de task para auditoría de orquestación.
3. En fallo, el operador debe consultar **ambos** orígenes: log Airflow (¿se invocó?) y log ETL (¿qué falló en el pipeline?).
4. Airflow no reimplementa ni silencia el logging del ETL.

---

## 13. Estrategia de configuración mediante variables de entorno

### 13.1 Ya existentes (ETL / PostgreSQL)

| Variable | Uso |
|----------|-----|
| `POSTGRES_DB` | Base de datos |
| `POSTGRES_USER` | Usuario |
| `POSTGRES_PASSWORD` | Credencial |
| `POSTGRES_HOST` | Host (localhost en consola; nombre de servicio en red Docker) |
| `POSTGRES_PORT` | Puerto |
| `POSTGRES_CONTAINER_NAME` | Nombre del contenedor Postgres (infra) |

### 13.2 Futuras (solo Airflow — Subfase 5.1+)

Variables exclusivas `AIRFLOW_*` (y relacionadas de autenticación/UI) se añadirán en infraestructura **sin** mezclarlas con la lógica del ETL.

### 13.3 Principios

- Sin secretos en DAGs ni en el código del ETL.
- Misma familia `POSTGRES_*` para el pipeline, independientemente del orquestador.
- Separación clara: configuración de **conexión DW** vs configuración de **motor Airflow**.

---

## 14. Buenas prácticas de orquestación

1. Un entrypoint estable y documentado.
2. Tasks delgadas: orquestar, no transformar.
3. Separar logs de orquestación y de negocio/datos.
4. Fallar de forma explícita (código de salida) ante validación DW no OK.
5. No acoplar Power BI ni SQL ad hoc a las tasks.
6. Mantener ejecutable el ETL sin Airflow (prueba de desacoplamiento).
7. Versionar solo artefactos de orquestación en `airflow/`; no duplicar el pipeline.
8. Documentar antes de implementar (este documento es la fuente de 5.1–5.4).

---

## 15. Restricciones arquitectónicas

1. Prohibido mover reglas de negocio a Airflow.
2. Prohibido ejecutar DDL/DML del DW desde tasks Airflow.
3. Prohibido modificar capas ETL / Repository / SQL como parte de la orquestación.
4. Prohibido que Airflow escriba directamente a `data/raw/`.
5. Prohibido fragmentar el pipeline en Airflow de forma que se altere el orden dims→hechos o se omita Validation/Logging.
6. `requirements.txt` del ETL permanece separado de la instalación de Airflow (gestión en 5.1).
7. Cualquier cambio de infraestructura Docker se realiza en Subfase 5.1, no en este documento de arquitectura.

---

## 16. Estructura esperada de la carpeta `airflow/`

```
airflow/
├── dags/          # Definiciones de DAG (orquestación únicamente)
├── config/        # Configuración de Airflow
├── logs/          # Logs del motor Airflow (no versionar contenido)
├── plugins/       # Plugins opcionales (sin lógica DW)
└── .gitkeep
```

Esta estructura ya existe en el repositorio como placeholder del Pre-Gate.  
En 5.2 se añadirán DAG(s); en 5.0 **no** se crean.

---

## 17. Roadmap oficial de la Fase 5

| Subfase | Nombre | Objetivo |
|---------|--------|----------|
| **5.0** | Arquitectura de orquestación | Este documento — especificación oficial |
| **5.1** | Infraestructura Airflow | Docker + servicios Airflow + red + variables; sin lógica de negocio |
| **5.2** | DAG ETL | DAG que invoca únicamente el entrypoint del pipeline congelado |
| **5.3** | Operación | Programación, corridas controladas, monitoreo operativo |
| **5.4** | Validación | Verificación de orquestación E2E (consola ≡ Airflow en resultado operativo) |

---

## 18. Versiones objetivo de infraestructura (referencia arquitectónica)

Las siguientes versiones son **objetivo de diseño** para la implementación (Subfase 5.1+).  
**No se instalan ni se aplican en 5.0.**

| Componente | Versión objetivo |
|------------|------------------|
| Python | **3.12.x** |
| PostgreSQL | **16.x** (alineado al servicio actual `postgres:16-alpine`) |
| Apache Airflow | **3.1.x**, o la **versión estable equivalente** disponible al momento de la implementación (p. ej. línea 3.x estable vigente) |

La selección exacta de patch/minor de Airflow se confirma en 5.1 según disponibilidad de imagen/documentación oficial, sin alterar este principio: orquestación delgada sobre el ETL congelado.

---

## 19. Criterios de aceptación de la arquitectura (Gate 5.0)

- [x] Documento creado en `docs/arquitectura/03_Arquitectura_Airflow.md`
- [x] Separación Airflow vs ETL explícita
- [x] Entrypoint único y ejecución dual (consola / Airflow) documentada
- [x] Roadmap 5.1–5.4 definido
- [x] Versiones objetivo registradas
- [x] Sin código de implementación en este documento

---

## 20. Fuera de alcance de la Subfase 5.0

- Instalar Apache Airflow
- Modificar `docker-compose.yml`
- Crear DAGs
- Modificar `requirements.txt`
- Modificar ETL / Repository / SQL / Business Rules
- Operar corridas productivas vía Airflow

**Siguiente subfase autorizada tras Gate 5.0:** **5.1 — Infraestructura Docker + Apache Airflow.**
