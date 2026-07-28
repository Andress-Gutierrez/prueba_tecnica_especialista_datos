# Documento Técnico Final

**Proyecto:** Prueba Técnica — Especialista de Datos (Proceso ETL y Visualización)  
**Última actualización:** 2026-07-28  
**Estado:** versión final para entrega

---

## 1. Introducción

Este documento describe la solución implementada para la prueba técnica de Especialista de Datos. El alcance cubre la carga de archivos `.xlsb`, la transformación y depuración de datos, el diseño de un Data Warehouse local en PostgreSQL, la orquestación con Apache Airflow y la construcción de un tablero ejecutivo en Power BI.

La solución se diseñó para responder dos retos de negocio:

- Seguimiento al desempeño comercial de ventas frente a presupuesto.
- Seguimiento a la gestión de registros TMK Outbound.

## 2. Objetivos del Proyecto

El objetivo técnico fue implementar una base de datos local que funcionara como fuente confiable para Power BI, evitando análisis directos sobre archivos Excel y separando claramente las responsabilidades entre extracción, transformación, persistencia y visualización.

El objetivo analítico fue permitir al Director Comercial monitorear:

- Ventas válidas frente al presupuesto.
- Desempeño por región, aliado, gerente, jefe y especialista.
- Gestión TMK por aliado, campaña y segmento.
- Contactabilidad, contactos efectivos y contactos no efectivos.

## 3. Arquitectura de la Solución

La arquitectura implementada sigue este flujo:

```text
Archivos .xlsb
    -> Python ETL
    -> PostgreSQL local en Docker
    -> Apache Airflow para orquestación
    -> Power BI Desktop
```

Componentes principales:

- `data/raw/`: fuentes originales `Ventas.xlsb`, `Presupuesto.xlsb` y `Registros.xlsb`.
- `etl/`: extracción, transformación, reglas de negocio, carga y validación.
- `sql/ddl/` y `sql/dml/`: creación del esquema físico y seeds.
- `repository/`: persistencia desacoplada hacia PostgreSQL.
- `airflow/dags/`: DAGs de ejecución.
- `powerbi/PowerBI_ETL_Comercial.pbix`: tablero ejecutivo.

Airflow solo orquesta. La lógica de negocio reside en Python y el consumo analítico se realiza desde Power BI contra PostgreSQL.

## 4. Diseño del Modelo de Datos

Se implementó un modelo dimensional orientado a análisis, con tres procesos de negocio:

- Ventas comerciales.
- Presupuesto / metas comerciales.
- Gestión TMK Outbound.

Hechos:

- `dwh.fact_ventas`
- `dwh.fact_presupuesto`
- `dwh.fact_gestion_tmk`

Dimensiones:

- `dwh.dim_tiempo`
- `dwh.dim_region`
- `dwh.dim_canal`
- `dwh.dim_categoria`
- `dwh.dim_jerarquia_comercial`
- `dwh.dim_aliado`
- `dwh.dim_unidad_gestion`
- `dwh.dim_marca`
- `dwh.dim_vendedor`
- `dwh.dim_validez_venta`
- `dwh.dim_campana`
- `dwh.dim_segmento`
- `dwh.dim_tipo_contacto`

Granos principales:

- Ventas: una fila representa un evento transaccional de venta.
- Presupuesto: una fila representa una meta mensual en un cruce comercial.
- Gestión TMK: una fila representa un agregado de gestión por tipificación.

## 5. Justificación del Modelo Implementado

El enunciado solicita evaluar si para este escenario resulta más adecuada una arquitectura tipo estrella (Star Schema) o copo de nieve (Snowflake Schema). Para la solución implementada se eligió Star Schema como arquitectura principal.

La razón principal es que el objetivo del proyecto es analítico y ejecutivo: Power BI debe responder rápidamente preguntas de negocio sobre ventas, presupuesto y gestión TMK. El modelo estrella reduce la cantidad de saltos entre tablas, simplifica las relaciones y facilita que los usuarios consuman dimensiones de negocio directamente desde el panel de campos.

En este caso existen tres hechos (`fact_ventas`, `fact_presupuesto`, `fact_gestion_tmk`) que comparten dimensiones conformadas como tiempo, región, aliado y jerarquía comercial. Esta estructura encaja naturalmente con un Star Schema porque cada hecho se conecta de forma directa con sus dimensiones, sin depender de cadenas largas de relaciones.

Se evaluó Snowflake Schema como alternativa, especialmente para jerarquías como canal, región o jerarquía comercial. Sin embargo, se descartó porque normalizar esas dimensiones en subdimensiones aumentaría la complejidad del modelo semántico, haría más difícil la navegación en Power BI y agregaría relaciones adicionales sin un beneficio proporcional para el volumen y el tipo de análisis requerido.

Desde buenas prácticas de rendimiento en Power BI, el Star Schema ofrece ventajas claras:

- Menos relaciones activas que evaluar durante los filtros.
- Relaciones 1:N directas desde dimensiones hacia hechos.
- Tablas de hechos enfocadas en medidas y llaves surrogate.
- Dimensiones con atributos descriptivos listos para filtros, segmentadores y jerarquías.
- Modelo semántico más simple para el usuario final.

El modelo implementado en Power BI refleja la estructura dimensional creada en PostgreSQL. Las tablas `dwh.fact_*` se mantienen como hechos y las tablas `dwh.dim_*` como dimensiones. Las relaciones se configuraron desde dimensiones hacia hechos usando las claves `sk_*`, conservando la integridad del Data Warehouse.

Para mejorar la experiencia de usuario, las claves técnicas `sk_*` y columnas de auditoría como `fecha_carga_dw` se ocultaron en la vista de informe. De esta forma, el usuario de negocio ve atributos analíticos como región, aliado, gerente, jefe, especialista, campaña, segmento y medidas DAX, sin exponerse a llaves técnicas del modelo.

En conclusión, Star Schema es la opción más adecuada para este escenario porque equilibra rendimiento, claridad, trazabilidad con la base de datos y facilidad de uso en Power BI. Snowflake Schema se consideró, pero se descartó para evitar complejidad innecesaria en un tablero ejecutivo orientado a análisis comercial.

## 6. Modelo Físico

El modelo físico se implementó en PostgreSQL bajo el esquema `dwh`.

Características:

- Surrogate keys `sk_*` en dimensiones y hechos.
- Relaciones 1:N desde dimensiones hacia hechos.
- Índices analíticos sobre claves de hechos.
- Miembro `sk=0` para valores no informados.
- Tabla `dim_validez_venta` para materializar la regla de ventas válidas.
- `dim_tiempo` como calendario corporativo con festivos Colombia y bandera `es_habil`.

La carga de hechos usa estrategia Full Load: `TRUNCATE` + carga completa. Para soportar el volumen real, la carga de hechos se optimizó con PostgreSQL `COPY FROM STDIN`.

## 7. Depuraciones y Transformaciones

Transformaciones aplicadas:

- Normalización de nombres de columnas.
- Limpieza de textos y espacios.
- Conversión de fechas y periodos.
- Conversión de medidas numéricas.
- Deduplicación técnica.
- Homologación de catálogos dimensionales.
- Asignación de miembros `No informado`.
- Construcción de dimensiones conformadas.
- Resolución de surrogate keys para hechos.

Reglas de negocio destacadas:

- Venta válida: tiene código de factura y no presenta nota crédito.
- TMK Outbound: se conserva como universo de análisis de `Registros.xlsb`.
- Tipificación TMK: contactos efectivos, contactos no efectivos y no contactos.
- Presupuesto: se conserva el total `T&T` como medida monetaria de presupuesto.
- Calendario: días hábiles lunes a sábado, excluyendo festivos nacionales de Colombia según `dim_tiempo`.

## 8. Implementación del ETL

El ETL está organizado por capas:

- `etl/extract/`: lectura de archivos `.xlsb`.
- `etl/transform/`: limpieza técnica por dataset.
- `etl/business_rules/`: reglas de negocio.
- `etl/load/`: orquestación de carga de dimensiones y hechos.
- `repository/`: acceso a PostgreSQL.
- `etl/validation.py`: validación del Data Warehouse.

La ejecución final se realizó sin límite de muestra (`max_rows=None`) y cargó:

- `fact_ventas`: 243359 filas.
- `fact_presupuesto`: 731 filas.
- `fact_gestion_tmk`: 459567 filas.

Resultado de validación:

- Validación DW: OK.
- Chequeos: 38.
- Fallidos: 0.
- Orphans: 0.

## 9. Orquestación con Apache Airflow

Se implementó un DAG principal para ejecutar el pipeline comercial:

- `airflow/dags/etl_comercial_pipeline.py`

Características:

- DAG manual (`schedule=None`).
- Una tarea principal `run_etl_pipeline`.
- `PythonOperator`.
- Reintentos configurados.
- Timeout operativo.
- Logging en consola y archivo.

También se implementó infraestructura para calendario corporativo mediante `calendar_seed_dag`, que alimenta `dim_tiempo` con fechas, festivos y días hábiles.

## 10. Base de Datos PostgreSQL

La base local se ejecuta con Docker Compose y PostgreSQL 16. La configuración se maneja por variables de entorno a partir de `replace.env` y `.env`.

Validaciones implementadas:

- Existencia del esquema `dwh`.
- Existencia de 13 dimensiones.
- Existencia de 3 hechos.
- Conteos por tabla.
- Integridad referencial.
- Miembros `sk=0`.
- Dominio de `dim_validez_venta`.
- Confirmación de que `fact_gestion_tmk` no contiene `sk_canal`.

## 11. Dashboard Power BI

El archivo `powerbi/PowerBI_ETL_Comercial.pbix` contiene tres páginas:

### Resumen_Ejecutivo

Incluye KPIs principales:

- Ventas válidas.
- Presupuesto T&T.
- Cumplimiento.
- Faltante.
- Ventas vs presupuesto por región.

Tras refrescar con datos completos:

- Ventas válidas aproximadas: `$ 327 mil M`.
- Presupuesto T&T aproximado: `$ 364 mil M`.
- Cumplimiento aproximado: `90,06 %`.
- Faltante aproximado: `$ 36 mil M`.

### Detalle_Comercial

Incluye matrices por:

- Aliado.
- Gerente.
- Jefe.
- Especialista.

Permite identificar sobrecumplimientos e incumplimientos mediante ventas, presupuesto, cumplimiento y faltante.

### TMK_Outbound

Incluye:

- Registros entregados.
- `% Gestión`.
- `% Contactabilidad`.
- `% Contactos efectivos`.
- `% Contactos no efectivos`.
- Top 5 aliados por contactabilidad.
- Campañas con mejor contactabilidad.
- Campañas con mayor y menor cantidad de registros.
- Contactabilidad por segmento.

Tras refrescar con datos completos:

- Registros entregados aproximados: `55 mil`.
- Gestión: `32,34 %`.
- Contactabilidad: `18,03 %`.
- Contactos efectivos: `14,16 %`.
- Contactos no efectivos: `3,87 %`.

## 12. Principales Medidas DAX

Medidas de ventas y presupuesto:

```DAX
Ventas_$ = SUM('dwh fact_ventas'[valor_antes_iva])
```

```DAX
Ventas_Validas_$ =
CALCULATE(
    [Ventas_$],
    'dwh dim_validez_venta'[es_venta_valida] = TRUE()
)
```

```DAX
Presupuesto_TYT = SUM('dwh fact_presupuesto'[tyt])
```

```DAX
Cumplimiento_TYT_Valido_% =
DIVIDE([Ventas_Validas_$], [Presupuesto_TYT])
```

```DAX
Faltante_TYT_Valido_$ =
[Presupuesto_TYT] - [Ventas_Validas_$]
```

Medidas TMK:

```DAX
Registros_Entregados = [Gestiones_TMK]
```

```DAX
Contactos_Efectivos =
CALCULATE(
    [Gestiones_TMK],
    'dwh dim_tipo_contacto'[tipo_contacto] = "CONTACTOS EFECTIVOS"
)
```

```DAX
Contactos_No_Efectivos =
CALCULATE(
    [Gestiones_TMK],
    'dwh dim_tipo_contacto'[tipo_contacto] = "CONTACTOS NO EFECTIVOS"
)
```

```DAX
Contactos_TMK =
[Contactos_Efectivos] + [Contactos_No_Efectivos]
```

```DAX
Contactabilidad_TMK_% =
DIVIDE([Contactos_TMK], [Registros_Entregados])
```

```DAX
Contactos_Efectivos_% =
DIVIDE([Contactos_Efectivos], [Registros_Entregados])
```

```DAX
Contactos_No_Efectivos_% =
DIVIDE([Contactos_No_Efectivos], [Registros_Entregados])
```

Las fórmulas exactas de `% Gestión`, `% Contactabilidad`, `% Contactos efectivos` y `% Contactos no efectivos` no estaban especificadas en el PDF; se adoptó una definición consistente con la tipificación observada en la fuente de registros.

## 13. Novedades Identificadas Durante el Análisis

Hallazgos relevantes:

- `Código Factura` no es clave natural única de ventas.
- Ventas contiene registros sin factura y con nota crédito; por eso se creó `dim_validez_venta`.
- Presupuesto contiene medidas monetarias `terminales`, `tecnologia` y `tyt`.
- Registros TMK llega en grano agregado, no como contacto unitario.
- La jerarquía comercial no tiene cobertura completa en todos los registros.
- Existen valores sin región o sin información asignada.
- Algunas fórmulas de TMK no estaban cerradas explícitamente en el enunciado.
- Se identificó PII potencial en identificaciones de vendedores, por lo que se ocultaron campos técnicos/no necesarios en Power BI.

## 14. Uso de Herramientas de IA

Se utilizaron herramientas de IA como apoyo metodológico y de productividad:

- ChatGPT: rol de Tech Lead para planificación, revisión de decisiones, validación funcional y guía de construcción del tablero.
- Cursor: apoyo en implementación, revisión de código, documentación y actualización de bitácora.

Ejemplos de prompts utilizados:

- "Actúa como inspector visual de Power BI y describe únicamente lo que ves".
- "Guíame como Tech Lead para finalizar el proyecto y cumplir el PDF".
- "Revisa qué falta contra los requisitos de la prueba técnica".
- "Completa el documento técnico final con modelo, ETL, Power BI, DAX y uso de IA".

La IA no sustituyó las fuentes oficiales del proyecto. Las decisiones se contrastaron con el PDF, el perfilado de datos, los logs del ETL y el modelo implementado.

## 15. Conclusiones

La solución implementa un flujo completo desde fuentes `.xlsb` hasta un tablero ejecutivo en Power BI sobre PostgreSQL. El modelo dimensional permite analizar ventas, presupuesto y gestión TMK con dimensiones de negocio reutilizables.

El ETL final fue ejecutado con datos completos y validación satisfactoria del Data Warehouse. Power BI fue refrescado contra la carga completa y presenta indicadores coherentes para los dos retos solicitados.

Quedan como mejoras futuras:

- Formalizar con negocio las fórmulas exactas de TMK no especificadas en el PDF.
- Profundizar en meta diaria dinámica y acumulación de déficit con más visuales específicos.
- Publicar el tablero en Power BI Service si el entorno lo permite.
