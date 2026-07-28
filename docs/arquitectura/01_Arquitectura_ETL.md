# 01 — Arquitectura ETL

----------------------------------------------------
ESTADO: ESPECIFICACIÓN OFICIAL — Subfase 4.0  
Documento de arquitectura técnica del pipeline ETL.  
**No contiene código Python ni SQL.**  
Fuente de verdad para la implementación de la Fase 4.
----------------------------------------------------

Proyecto: prueba_tecnica_especialista_datos  
Fecha: 2026-07-27  
Autor: Cursor (Senior Software Developer)  
Revisión: Tech Lead / Project Owner

### Fuentes de diseño

- `docs/modelo/03_Modelo_Dimensional.md` (congelado)
- `docs/modelo/04_Modelo_Fisico.md` (congelado)
- `docs/analisis/02_Reglas_Negocio.md`, `03_Requisitos_Funcionales.md`
- Bitácora: cierre operativo Fase 3 (`PROJECT_STATE.md`)

---

## 1. Objetivo del ETL

### 1.1 Propósito

Extraer, transformar y cargar las fuentes Excel oficiales hacia el Data Warehouse Star Schema en PostgreSQL (`dwh_comercial` / esquema `dwh`), aplicando las reglas de negocio aprobadas, de forma que Power BI consuma únicamente datos ya materializados en PostgreSQL.

### 1.2 Alcance

**Incluye (Fase 4):**

- Lectura de `data/raw/*.xlsb` (Ventas, Presupuesto, Registros).
- Normalización tipográfica/fechas/catálogos.
- Generación y resolución de surrogate keys.
- Aplicación de reglas oficiales (ventas válidas, meta diaria/déficit como preparación de atributos, tipificación TMK).
- Carga de las 13 dimensiones y 3 hechos definidos en el Modelo Físico.
- Validaciones pre/post carga y logging operativo.

**Excluye (fases posteriores):**

- Orquestación Airflow (Fase 5) — el ETL debe poder ejecutarse de forma autónoma (script/CLI).
- Dashboards Power BI (Fase 6).
- Lógica de negocio dentro de PostgreSQL o Airflow.

### 1.3 Fuentes

| Archivo | Dominio | Destino lógico |
|---------|---------|----------------|
| `data/raw/Ventas.xlsb` | Venta comercial | `fact_ventas` + dims asociadas |
| `data/raw/Presupuesto.xlsb` | Metas mensuales | `fact_presupuesto` + dims asociadas |
| `data/raw/Registros.xlsb` | Gestión TMK Outbound | `fact_gestion_tmk` + dims asociadas |

Las fuentes en `data/raw/` son **inmutables**: el ETL no las modifica ni elimina.

### 1.4 Destino

| Recurso | Valor |
|---------|-------|
| Motor | PostgreSQL 16 (Docker) |
| Base de datos | `dwh_comercial` |
| Esquema analítico | `dwh` |
| Esquema staging (opcional/futuro) | `stg` (si se materializa; ver §3) |
| Capas de archivo | `data/staging/`, `data/processed/` (artefactos intermedios; no versionados) |

---

## 2. Flujo completo del pipeline

### 2.0 Flujo oficial vigente (calendario + ETL comercial)

```
Calendar Seed DAG
        ↓
dim_tiempo          [Master Data; única fuente oficial del calendario]
        ↓
ETL Comercial
        ↓
Business Rules
        ↓
Load                [dims de negocio + hechos; NO construye ni carga dim_tiempo]
        ↓
Validation
```

`dim_tiempo` se pobla **exclusivamente** mediante `calendar_seed_dag` (API `festivos.com.co`).  
El ETL comercial **lee** `dim_tiempo` (precheck + días hábiles / resolución `sk_tiempo`); **no** la construye ni la upserta.

### 2.1 Flujo detallado del ETL comercial

```
Excel (.xlsb)  [data/raw/ — inmutable]
        ↓
Landing        [lectura en memoria / copia controlada a data/staging]
        ↓
Staging        [dataframes tipados; opcional persistencia stg.* o parquet/csv en data/staging]
        ↓
Transformación [limpieza, renombres, normalización, dedupe]
        ↓
Business Rules [ventas válidas, tipificación TMK, días hábiles desde dim_tiempo, etc.]
        ↓
Carga Dimensiones de negocio [lookup NK → SK; upsert; sk=0 ya seed]
        ↓
Carga Hechos [Full Load TRUNCATE + INSERT; resolución FK → SK]
        ↓
Validación [conteos, FK, nulos críticos, reconciliación básica]
        ↓
Data Warehouse [dwh.* listo para Power BI]
```

### Notas de flujo

1. **Calendario primero:** ejecutar `calendar_seed_dag` antes del ETL comercial.
2. **Landing:** único punto de contacto con `.xlsb` (`pyxlsb` / pandas).
3. **Staging:** no altera el modelo dimensional; es capa técnica de trabajo.
4. **Transformación vs reglas:** transformar = calidad estructural; reglas = semántica de negocio.
5. **Orden dims de negocio → hechos:** obligatorio por integridad referencial (FK físicas).
6. **`dim_tiempo`:** Master Data externo al Load comercial; el ETL solo consulta/resuelve SK.
7. **Validación:** no modifica datos; reporta OK/ERROR (complementa `scripts/validate_dw.ps1` a nivel de metadatos).

---

## 3. Arquitectura de carpetas ETL

### 3.1 Carpetas existentes (oficiales)

| Carpeta | Función |
|---------|---------|
| `etl/` | Raíz del paquete ETL. Punto de entrada CLI/orquestador interno (sin Airflow). |
| `etl/extract/` | Lectura de fuentes `.xlsb`; inventario de hojas/columnas; volcado a staging en memoria o archivo. |
| `etl/transform/` | Limpieza tipológica, renombre a snake_case, normalización de textos/fechas, deduplicación exacta, homologación de catálogos. |
| `etl/business_rules/` | Reglas oficiales: validez de venta (O1), flags de tipificación TMK, preparación de atributos para meta diaria/déficit (sin materializar un cuarto hecho). |
| `etl/load/` | Upsert/insert de dimensiones y hechos hacia `dwh.*`; resolución de SK; escritura de `fecha_carga_dw`. |
| `etl/utils/` | Helpers compartidos: I/O, tipos, hashing de NK, reintentos de conexión, formateo de logs. |

Capas de datos del repo (ya existentes, usadas por el ETL):

| Carpeta | Función |
|---------|---------|
| `data/raw/` | Fuentes oficiales inmutables. |
| `data/staging/` | Artefactos intermedios generados (ignorados en Git). |
| `data/processed/` | Salidas opcionales post-transform (ignorados en Git). |

### 3.2 Carpetas no existentes — propuesta justificada (NO creadas en 4.0)

El listado de alcance menciona `config/`, `logging/` y `validation/`. **Hoy no existen** bajo `etl/`. No se crean en esta subfase.

| Carpeta propuesta | Justificación | Alternativa inmediata |
|-------------------|---------------|------------------------|
| `etl/config/` | Centralizar conexión BD, rutas y constantes sin hardcode. | Módulo `etl/utils/config.py` (o similar) hasta Gate de creación de carpeta. |
| `etl/logging/` | Separar handlers/formatters si el logging crece. | Logger configurado desde `utils` + salida a `logs/` (si se aprueba). |
| `etl/validation/` | Validaciones pre/post carga independientes del load. | Funciones en `utils` o submódulo `load/validate_*.py` hasta Gate. |

**Decisión 4.0:** documentar la necesidad; **crear carpetas solo con aprobación explícita** del Tech Lead en una subfase posterior. Mientras tanto, las responsabilidades se alojan en `utils/` / `load/` sin romper la estructura ya versionada.

---

## 4. Orden de carga

### 4.1 Master Data de tiempo (fuera del Load comercial)

| Tabla | Quién la carga | Notas |
|-------|----------------|-------|
| `dim_tiempo` | **Solo** `calendar_seed_dag` | Única fuente oficial del calendario (`es_habil`, `es_festivo`, `nombre_festivo`). El ETL comercial **no** construye ni carga esta dimensión. |

### 4.2 Dimensiones de negocio (ETL comercial, antes que cualquier hecho)

Orden recomendado (independientes entre sí; cualquier orden entre estas dims es válido siempre que precedan a hechos). Alineado al DDL (`02`–`13`):

1. `dim_region`
2. `dim_canal`
3. `dim_categoria`
4. `dim_jerarquia_comercial`
5. `dim_aliado`
6. `dim_unidad_gestion`
7. `dim_marca`
8. `dim_vendedor`
9. `dim_validez_venta` *(seed DML ya aporta dominio; ETL puede enriquecer si aplica)*
10. `dim_campana`
11. `dim_segmento`
12. `dim_tipo_contacto`

### 4.3 Hechos (después de dims de negocio; `dim_tiempo` ya poblada)

13. `fact_ventas`
14. `fact_presupuesto`
15. `fact_gestion_tmk`

### 4.4 Por qué este orden

1. Las FK físicas en hechos apuntan a dimensiones: sin dim cargada (o sin `sk=0`) falla la integridad; `dim_tiempo` debe existir vía Calendar Seed antes del ETL.
2. `sk=0` (“No informado”) ya existe por DML; el ETL lo reutiliza para nulos/huérfanos.
3. Los hechos no se referencian entre sí: el orden entre hechos es libre, pero se fija Ventas → Presupuesto → Gestión por afinidad a Retos 1 y 2.
4. Alineación con numeración DDL facilita trazabilidad y despliegue.

---

## 5. Estrategia de carga

| Tema | Decisión arquitectónica |
|------|-------------------------|
| **Full Load (estrategia oficial)** | En cada corrida ETL: `TRUNCATE` + `INSERT` para tablas de hechos (`fact_ventas`, `fact_presupuesto`, `fact_gestion_tmk`). Reproducible e idempotente para la prueba técnica. |
| **Incremental** | **No aplica en este proyecto.** Requeriría rediseño de alcance (watermarks, detección de cambios y auditoría), fuera de la arquitectura congelada. |
| **Upsert de dimensiones** | Sobre NK (`*_nk` o UNIQUE compuesto): si existe → reutilizar SK; si no → asignar nuevo SK. No sobrescribir `sk=0`. |
| **Hechos** | Carga por grano con política Full Load: truncar tabla de hecho objetivo y recargar por `INSERT`. SK del hecho (`sk_venta`, etc.) asignada por el ETL, nunca `Código Factura` como identidad. |
| **Manejo de SK** | Surrogate keys obligatorias. Lookup por NK en memoria o consulta a `dwh.dim_*`. Reservado: `sk = 0` = No informado (seed). |
| **Miembro No Informado** | Ante nulo / no homologable → mapear a `sk=0` de la dimensión correspondiente. No inventar miembros de negocio fuera del catálogo sin regla. |
| **Registros huérfanos** | Dimensiones: crear miembro o mapear a `sk=0` según política por dimensión (región/jerarquía → `sk=0` prioritario). Hechos: no insertar sin SK resuelto; fallar o enviar a cuarentena en staging. |
| **Validaciones previas al insert** | Ver §9. Bloqueo hard ante violación de NOT NULL / FK / grano inconsistente. |
| **Deduplicación** | Filas exactas duplicadas en origen (Ventas/Registros) → regla en transform (quedarse con 1). Los 5 cruces de Presupuesto con montos distintos → regla explícita (sumar o conservar ambas) documentada en implementación 4.3/4.5; **no alteran el grano aprobado**. |
| **Festivos CO** | **Única fuente oficial:** `dwh.dim_tiempo` poblada por `calendar_seed_dag` (API `festivos.com.co`). El ETL comercial **no** recalcula festivos/hábiles; Presupuesto consume `es_habil` desde `dim_tiempo`. |

---

## 6. Configuración

El módulo de configuración (ubicación física: preferible `etl/config/` tras Gate, o `etl/utils` temporalmente) manejará:

| Categoría | Contenido |
|-----------|-----------|
| **Conexión BD** | Host, puerto, DB (`dwh_comercial`), usuario, password — leídos de `.env` / variables de entorno (nunca hardcodeados ni commitados). |
| **Rutas** | `data/raw`, `data/staging`, `data/processed`; nombres de archivos fuente. |
| **Parámetros** | Batch size, modo full, timeout conexión, encoding, engine Excel. |
| **Constantes** | `SK_NO_INFORMADO = 0`; nombres de esquema `dwh`; mapeos de columnas oficiales (p. ej. región Ventas — decisión en 4.2/4.3). |
| **Flags de ejecución** | dry-run, skip validation, solo una fuente. |

No se escriben valores secretos en el documento ni en el repo.

---

## 7. Logging

| Evento | Contenido mínimo |
|--------|------------------|
| Inicio de corrida | timestamp, versión/commit opcional, modo (full), fuentes a procesar |
| Fin de corrida | timestamp, duración total, estado OK/ERROR |
| Por etapa | extract / transform / rules / load_dim / load_fact / validate |
| Errores | excepción, contexto (archivo, columna, fila si aplica), stack resumido |
| Tiempos | duración por etapa y por tabla |
| Registros | leídos, descartados (dedupe), insertados, actualizados, mapeados a `sk=0` |
| Nivel | `INFO` operativo; `WARNING` calidad; `ERROR` fallo; `DEBUG` opcional en desarrollo |

Salida: consola + archivo de log de corrida (ruta bajo `logs/` o `data/processed/` — a fijar en implementación; no versionar logs).

---

## 8. Manejo de errores

| Escenario | Estrategia |
|-----------|------------|
| Archivo inexistente en `data/raw/` | Abortar corrida (`ERROR`); no continuar con fuentes parciales salvo flag explícito `allow_partial`. |
| Columnas faltantes / renombradas | Validar contrato de columnas post-extract; abortar con lista de faltantes. |
| Tipos inválidos | Coerción controlada en transform; filas no coercibles → rechazo a staging de errores + contador; umbral configurable de fallos máximos. |
| Error de conexión BD | Reintento limitado (utils); si persiste → abortar sin carga parcial inconsistente. |
| Error de integridad (FK/PK/UNIQUE) | Transacción por tabla o lote; rollback del lote; log del registro ofensor; abortar o continuar según política (default: abortar hechos si dims OK). |
| Error inesperado | Captura global; log `ERROR`; exit code ≠ 0; no silenciar excepciones. |

Principio: **fallar explícito** preferible a cargar datos inconsistentes en `dwh`.

---

## 9. Validaciones

### 9.1 Pre-carga (antes de escribir `dwh`)

1. Existencia y legibilidad de los 3 `.xlsb`.
2. Contrato de columnas mínimas por fuente.
3. Esquema `dwh` y tablas destino presentes (reutilizar lógica de `validate_dw.ps1` o equivalente Python).
4. Seeds `sk=0` y `dim_validez_venta` presentes.
5. Conteos de nulos críticos y % de filas a `sk=0` (alerta si supera umbral).
6. Dedupe aplicado / reportado.
7. Resolución de SK: 0 huérfanos sin política.

### 9.2 Post-carga

1. Conteos hechos ≈ filas transformadas esperadas (tolerancia documentada).
2. 0 violaciones FK (consulta metadatos / left anti-join).
3. `fact_gestion_tmk` sin columna canal (regresión de diseño).
4. `codigo_factura` puede ser NULL; `sk_venta` siempre poblado.
5. Ejecución opcional de `scripts/validate_dw.ps1` como gate operativo.

---

## 10. Principios de diseño

| Principio | Aplicación |
|-----------|------------|
| Modularidad | Un módulo por responsabilidad (`extract` / `transform` / `business_rules` / `load`). |
| Idempotencia | Misma corrida full sobre las mismas fuentes → mismo estado analítico reproducible (seeds preservados). |
| Trazabilidad | `fecha_carga_dw`, logs de corrida, conteos por etapa. |
| Reproducibilidad | Config vía `.env` + raw versionable; sin dependencias ocultas. |
| Separación de responsabilidades | Negocio en Python (`business_rules`); Airflow solo orquesta (Fase 5); PostgreSQL almacena. |
| Mantenibilidad | Sin hardcode de secretos; nombres alineados al Modelo Físico; sin anticipar Snowflake/Kafka/etc. |
| Fidelidad al modelo | No inventar columnas/tablas; no cambiar granos; no usar `Código Factura` como PK. |

---

## 11. Roadmap de implementación (Fase 4)

| Subfase | Nombre | Entregable esperado | Código en esta sesión |
|---------|--------|---------------------|------------------------|
| **4.0** | Diseño arquitectura ETL | Este documento | ✅ (solo docs) |
| **4.1** | Extracción | Módulos `etl/extract/` + lectura `.xlsb` | No |
| **4.2** | Transformación | Módulos `etl/transform/` | No |
| **4.3** | Reglas de negocio | Módulos `etl/business_rules/` | No |
| **4.4** | Carga dimensiones | Módulos `etl/load/` (dims) | No |
| **4.5** | Carga hechos | Módulos `etl/load/` (facts) | No |
| **4.6** | Validación | Checks pre/post + integración con runner | No |

Cada subfase requiere Gate en `PROJECT_STATE.md` antes de iniciar la siguiente.

---

## 12. Conclusión

La arquitectura ETL queda especificada para guiar la Fase 4 sin anticipar código. Respeta el Star Schema congelado, el orden dims→hechos, seeds `sk=0`, full load inicial y la separación extract / transform / business_rules / load.

**Próximo paso autorizado:** Subfase **4.1 — Extracción** (tras aprobación de este documento por Tech Lead / Project Owner).
