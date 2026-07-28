# README — Entrega de la Prueba Técnica

**Proyecto:** Prueba Técnica — Especialista de Datos (Proceso ETL y Visualización)  
**Estado:** entregables principales listos para revisión final.

---

## Contenido de la entrega

La solución contiene los tres entregables oficiales solicitados por el enunciado:

| Entregable | Descripción |
|------------|-------------|
| Scripts de creación y transformación de datos | DDL de PostgreSQL (`sql/ddl/`), seeds y módulos ETL en Python (`etl/`) |
| Archivo Power BI (`.pbix`) | Tablero ejecutivo con los Retos 1 (desempeño comercial) y 2 (gestión TMK Outbound) |
| Documento de explicación | `docs/Documento_Tecnico_Final.md` (diseño del modelo, transformaciones, novedades, justificación, medidas DAX, uso de IA) |

## Archivos disponibles

- `docs/Documento_Tecnico_Final.md`
- `docs/entregables/Documento_Tecnico_Final.pdf`
- `docs/entregables/Checklist_Entrega.md`
- `powerbi/PowerBI_ETL_Comercial.pbix`
- Scripts SQL en `sql/ddl/` y `sql/dml/`
- Código ETL en `etl/`, `repository/` y `scripts/`
- DAGs de Airflow en `airflow/dags/`
- `docker-compose.yml`
- Evidencia de validación en `logs/latest.log`

## Instrucciones generales de ejecución (resumen previsto)

1. Clonar el repositorio y ubicarse en la raíz del proyecto.
2. Copiar `replace.env` → `.env` y completar credenciales (PostgreSQL, Airflow, `FESTIVOS_API_KEY`).
3. Levantar los servicios: `docker compose up airflow-init` y `docker compose up -d`.
4. Ejecutar `calendar_seed_dag` (poblar `dim_tiempo` como Master Data).
5. Ejecutar el ETL comercial (`etl_comercial_pipeline` o `python -m scripts.run_etl_pipeline`).
6. Abrir el `.pbix` en Power BI Desktop y actualizar la conexión a PostgreSQL local.

La ejecución final validada cargó datos completos con `max_rows=None`:

- `fact_ventas`: 243359 filas.
- `fact_presupuesto`: 731 filas.
- `fact_gestion_tmk`: 459567 filas.
- Validación DW: OK.
- Chequeos: 38.
- Fallidos: 0.

## Requisitos

- Docker y Docker Compose
- Python 3.11+ (dependencias en `requirements.txt`)
- Power BI Desktop
- Puertos locales disponibles para PostgreSQL (5432) y Airflow (8080)

---

**Fecha límite oficial de entrega:** martes 28 de julio de 2026, 6:00 pm.
