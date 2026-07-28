# 04 — Modelo Físico (PostgreSQL)

----------------------------------------------------
ESTADO: MODELO FÍSICO OFICIAL — PENDIENTE DE GATE / IMPLEMENTACIÓN SQL

Documento oficial del diseño físico del Data Warehouse.  
Traduce `03_Modelo_Dimensional.md` a estructuras PostgreSQL.  
**No incluye scripts DDL** en esta subfase.
----------------------------------------------------

Fase: **2 — Diseño del Data Warehouse**  
Subfase: **2.4 — Modelo Físico**  
Fecha: 2026-07-26  
Motor: **PostgreSQL**

### Fuentes

- `03_Modelo_Dimensional.md` (oficial)
- `02B_Bus_Matrix.md`
- `02A_Analisis_Claves.md`
- Documentos de análisis y requisitos oficiales

---

## 1. Objetivo del modelo físico

Definir cómo se materializarán en PostgreSQL las tablas de hechos y dimensiones del Star Schema aprobado, de forma que:

1. Respeten granos, claves surrogate y Bus Matrix.
2. Sean aptas para consumo desde Power BI.
3. Permitan al ETL (Fase 4) cargar datos sin lógica de negocio en la base ni en Airflow.
4. Dejen documentados tipos, PK/FK, NULL e índices **antes** de escribir `CREATE TABLE`.

---

## 2. Convenciones de nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Esquema analítico | `dwh` | `dwh.fact_ventas` |
| Esquema staging (futuro ETL) | `stg` | `stg.ventas_raw` (fuera del alcance de esta subfase DDL) |
| Dimensiones | `dim_<nombre>` | `dim_tiempo` |
| Hechos | `fact_<nombre>` | `fact_ventas` |
| Surrogate key | `sk_<entidad>` | `sk_venta`, `sk_tiempo` |
| Business / natural key | `<atributo>_nk` | `aliado_nk` |
| Booleanos | `es_` / `tiene_` | `es_dia_habil`, `tiene_factura` |
| Fechas | `fecha_*` | `fecha_venta` (en staging); en dim: `fecha` |
| Medidas monetarias | snake_case | `valor_antes_iva` |
| Identifiers | snake_case, minúsculas, sin acentos | `codigo_factura` |
| Miembro desconocido | `sk_* = 0` | “No informado” |

Idioma de objetos físicos: **español técnico sin acentos** en nombres de columna (alineado al modelo dimensional).

---

## 3. Esquema de base de datos

| Esquema | Propósito |
|---------|-----------|
| `dwh` | Star Schema oficial (dims + facts) consumido por Power BI |
| `stg` | Capa de aterrizaje / limpieza previa (diseño de uso; DDL en Fase 3/4) |

Base de datos propuesta: `claro_dw` (nombre orientativo; fijar en implementación Docker).

---

## 4. Definición de tablas

Convención de columnas en las tablas siguientes:

- **NULL:** `NO` = NOT NULL; `SÍ` = permite NULL.
- **PK / FK:** según modelo dimensional (SK obligatorias).

### 4.1 Dimensiones

#### `dwh.dim_tiempo`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_tiempo | `BIGINT` | PK | — | NO | Surrogate key |
| fecha | `DATE` | — | — | SÍ | Fecha día (NULL solo para filas de grano mes puro si se usan) |
| anio | `INTEGER` | — | — | NO | Año (YYYY) |
| mes | `INTEGER` | — | — | NO | Mes (1–12) |
| dia | `INTEGER` | — | — | SÍ | Día del mes |
| periodo_yyyymm | `INTEGER` | — | — | NO | Periodo AAAAMM |
| nombre_mes | `VARCHAR(20)` | — | — | SÍ | Nombre del mes |
| dia_semana | `INTEGER` | — | — | SÍ | 1=lunes … 7=domingo |
| es_dia_habil | `BOOLEAN` | — | — | NO | Lun–sáb y no festivo CO |
| es_festivo_co | `BOOLEAN` | — | — | NO | Festivo nacional Colombia |
| es_fin_semana | `BOOLEAN` | — | — | SÍ | Sábado/domingo |

**Tipo:** Dimensión (conformada).  
**Restricciones:** `UNIQUE (periodo_yyyymm, fecha)` o `UNIQUE (fecha)` cuando fecha NOT NULL; `CHECK (mes BETWEEN 1 AND 12)`.  
**Observaciones:** alimenta meta diaria (O2–O6). Fuente de festivos → pendiente de implementación.

#### `dwh.dim_region`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_region | `BIGINT` | PK | — | NO | Surrogate key |
| region_nk | `VARCHAR(100)` | — | — | NO | Texto de negocio normalizado |
| nombre_region | `VARCHAR(100)` | — | — | NO | Etiqueta display |
| es_sin_region | `BOOLEAN` | — | — | NO | Miembros tipo SIN_REGION |

**Restricciones:** `UNIQUE (region_nk)`.  
**Observaciones:** mapeo columna oficial Ventas → ETL.

#### `dwh.dim_canal`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_canal | `BIGINT` | PK | — | NO | Surrogate key |
| canal | `VARCHAR(80)` | — | — | NO | CANAL |
| canal2 | `VARCHAR(80)` | — | — | SÍ | CANAL2 |
| sub_canal | `VARCHAR(80)` | — | — | SÍ | SUB CANAL |

**Restricciones:** `UNIQUE (canal, canal2, sub_canal)`.  
**Observaciones:** dim desnormalizada (Star).

#### `dwh.dim_categoria`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_categoria | `BIGINT` | PK | — | NO | Surrogate key |
| categoria_nk | `VARCHAR(80)` | — | — | NO | Categoría |
| nombre_categoria | `VARCHAR(80)` | — | — | NO | Display |

**Restricciones:** `UNIQUE (categoria_nk)`.

#### `dwh.dim_jerarquia_comercial`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_jerarquia | `BIGINT` | PK | — | NO | Surrogate key |
| gerente | `VARCHAR(80)` | — | — | SÍ | Nivel gerente |
| jefe | `VARCHAR(80)` | — | — | SÍ | Nivel jefe |
| especialista | `VARCHAR(80)` | — | — | SÍ | Nivel especialista |

**Restricciones:** `UNIQUE (gerente, jefe, especialista)`.  
**Observaciones:** desnormalizada; nulos permitidos por cobertura incompleta en Registros.

#### `dwh.dim_aliado`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_aliado | `BIGINT` | PK | — | NO | Surrogate key |
| aliado_nk | `VARCHAR(80)` | — | — | NO | Código/texto homologado |
| nombre_aliado | `VARCHAR(120)` | — | — | NO | Display |

**Restricciones:** `UNIQUE (aliado_nk)`.  
**Observaciones:** homologar DESCRIP2 / GV_Desc2 / ALIADO en ETL.

#### `dwh.dim_unidad_gestion`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_unidad_gestion | `BIGINT` | PK | — | NO | Surrogate key |
| unidad_gestion_nk | `VARCHAR(120)` | — | — | NO | UNIDAD DE GESTION |
| nombre_unidad_gestion | `VARCHAR(120)` | — | — | NO | Display |

**Restricciones:** `UNIQUE (unidad_gestion_nk)`.  
**Tipo:** Exclusiva Presupuesto.

#### `dwh.dim_marca`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_marca | `BIGINT` | PK | — | NO | Surrogate key |
| marca_nk | `VARCHAR(80)` | — | — | NO | Marca |
| nombre_marca | `VARCHAR(80)` | — | — | NO | Display |

**Restricciones:** `UNIQUE (marca_nk)`.  
**Tipo:** Exclusiva Ventas.

#### `dwh.dim_vendedor`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_vendedor | `BIGINT` | PK | — | NO | Surrogate key |
| cedula_vendedor_nk | `VARCHAR(40)` | — | — | NO | Cédula o `-` |
| nombre_vendedor | `VARCHAR(120)` | — | — | SÍ | Opcional |

**Restricciones:** `UNIQUE (cedula_vendedor_nk)`.  
**Observaciones:** PII — no exponer en repo público sin política.

#### `dwh.dim_validez_venta`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_validez | `BIGINT` | PK | — | NO | Surrogate key |
| tiene_factura | `BOOLEAN` | — | — | NO | Código factura presente |
| tiene_nota_credito | `BOOLEAN` | — | — | NO | Nota crédito = SI |
| es_venta_valida | `BOOLEAN` | — | — | NO | tiene_factura ∧ ¬tiene_nota_credito |
| descripcion | `VARCHAR(80)` | — | — | NO | Etiqueta |

**Restricciones:** `UNIQUE (tiene_factura, tiene_nota_credito)`.  
**Justificación física:** se materializa como dimensión (opción aprobada en modelo lógico) para filtros Power BI del Reto 1.

#### `dwh.dim_campana`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_campana | `BIGINT` | PK | — | NO | Surrogate key |
| campana_nk | `VARCHAR(200)` | — | — | NO | NOMBRE_CAMPAÑA |
| nombre_campana | `VARCHAR(200)` | — | — | NO | Display |

**Restricciones:** `UNIQUE (campana_nk)`.  
**Tipo:** Exclusiva Gestión.

#### `dwh.dim_segmento`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_segmento | `BIGINT` | PK | — | NO | Surrogate key |
| segmento_nk | `VARCHAR(80)` | — | — | NO | Valor origen |
| segmento_normalizado | `VARCHAR(80)` | — | — | NO | Valor limpio |
| nombre_segmento | `VARCHAR(80)` | — | — | NO | Display |

**Restricciones:** `UNIQUE (segmento_nk)`.  
**Observaciones:** normalización en ETL (`Adicionales_` → `Adicionales`).

#### `dwh.dim_tipo_contacto`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_tipo_contacto | `BIGINT` | PK | — | NO | Surrogate key |
| tipo_contacto | `VARCHAR(80)` | — | — | NO | TIPO_CONTACTO |
| detalle_contacto | `VARCHAR(120)` | — | — | SÍ | DETALLE1 |
| nombre_tipo_contacto | `VARCHAR(160)` | — | — | NO | Display |

**Restricciones:** `UNIQUE (tipo_contacto, detalle_contacto)`.  
**Tipo:** Exclusiva Gestión.

---

### 4.2 Hechos

#### `dwh.fact_ventas`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_venta | `BIGINT` | PK | — | NO | SK del evento (no es Código Factura) |
| sk_tiempo | `BIGINT` | — | → dim_tiempo | NO | Fecha venta |
| sk_region | `BIGINT` | — | → dim_region | NO | Región |
| sk_canal | `BIGINT` | — | → dim_canal | NO | Canal |
| sk_categoria | `BIGINT` | — | → dim_categoria | NO | Categoría |
| sk_jerarquia | `BIGINT` | — | → dim_jerarquia_comercial | NO | Jerarquía |
| sk_aliado | `BIGINT` | — | → dim_aliado | NO | Aliado |
| sk_marca | `BIGINT` | — | → dim_marca | NO | Marca |
| sk_vendedor | `BIGINT` | — | → dim_vendedor | NO | Vendedor |
| sk_validez | `BIGINT` | — | → dim_validez_venta | NO | Validez Reto 1 |
| codigo_factura | `VARCHAR(40)` | — | — | SÍ | Degenerado; puede ser NULL |
| valor_antes_iva | `NUMERIC(18,2)` | — | — | NO | Medida |
| cuotas | `NUMERIC(8,2)` | — | — | SÍ | Medida opcional |
| fecha_carga_dw | `TIMESTAMP` | — | — | NO | Auditoría ETL |

**Tipo:** Hecho.  
**Restricciones:** FK a todas las dims listadas; `CHECK (valor_antes_iva >= 0)` (si negocio lo confirma en ETL).  
**Observaciones:** grano = 1 evento; 55 duplicados exactos de origen se resuelven en ETL (pendiente regla).

#### `dwh.fact_presupuesto`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_presupuesto | `BIGINT` | PK | — | NO | SK |
| sk_tiempo | `BIGINT` | — | → dim_tiempo | NO | Periodo mes |
| sk_region | `BIGINT` | — | → dim_region | NO | Región |
| sk_canal | `BIGINT` | — | → dim_canal | NO | Canal |
| sk_categoria | `BIGINT` | — | → dim_categoria | NO | Categoría |
| sk_unidad_gestion | `BIGINT` | — | → dim_unidad_gestion | NO | Unidad gestión |
| sk_jerarquia | `BIGINT` | — | → dim_jerarquia_comercial | NO | Jerarquía |
| sk_aliado | `BIGINT` | — | → dim_aliado | NO | Aliado |
| terminales | `NUMERIC(20,4)` | — | — | NO | Medida |
| tecnologia | `NUMERIC(20,4)` | — | — | NO | Medida |
| tyt | `NUMERIC(20,4)` | — | — | NO | Medida (= terminales + tecnologia) |
| fecha_carga_dw | `TIMESTAMP` | — | — | NO | Auditoría ETL |

**Tipo:** Hecho.  
**Restricciones:** FK a dims; opcional `CHECK (ABS(tyt - (terminales + tecnologia)) < 0.01)`.  
**Observaciones:** `NUMERIC(20,4)` por magnitud de metas; regla de 5 cruces duplicados → ETL.

#### `dwh.fact_gestion_tmk`

| Columna | Tipo PostgreSQL | PK | FK | NULL | Descripción |
|---------|-----------------|----|----|------|-------------|
| sk_gestion | `BIGINT` | PK | — | NO | SK |
| sk_tiempo | `BIGINT` | — | → dim_tiempo | NO | Fecha gestión / periodo |
| sk_region | `BIGINT` | — | → dim_region | NO | Región |
| sk_jerarquia | `BIGINT` | — | → dim_jerarquia_comercial | NO | Puede ser “No informado” |
| sk_aliado | `BIGINT` | — | → dim_aliado | NO | Aliado |
| sk_campana | `BIGINT` | — | → dim_campana | NO | Campaña |
| sk_segmento | `BIGINT` | — | → dim_segmento | NO | Segmento |
| sk_tipo_contacto | `BIGINT` | — | → dim_tipo_contacto | NO | Tipificación |
| cantidad | `BIGINT` | — | — | NO | Medida volumen |
| intentos | `NUMERIC(18,2)` | — | — | SÍ | Medida esfuerzo |
| fecha_carga_dw | `TIMESTAMP` | — | — | NO | Auditoría ETL |

**Tipo:** Hecho.  
**Restricciones:** FK a dims listadas; `CHECK (cantidad >= 0)`.  
**Observaciones:** **sin** `sk_canal` físico (filtro TMK es regla de negocio, no columna origen). Grano = agregado.

---

## 5. Relaciones físicas

```
dim_tiempo                1 ─── * fact_ventas
dim_region                1 ─── * fact_ventas
dim_canal                 1 ─── * fact_ventas
dim_categoria             1 ─── * fact_ventas
dim_jerarquia_comercial   1 ─── * fact_ventas
dim_aliado                1 ─── * fact_ventas
dim_marca                 1 ─── * fact_ventas
dim_vendedor              1 ─── * fact_ventas
dim_validez_venta         1 ─── * fact_ventas

dim_tiempo                1 ─── * fact_presupuesto
dim_region                1 ─── * fact_presupuesto
dim_canal                 1 ─── * fact_presupuesto
dim_categoria             1 ─── * fact_presupuesto
dim_unidad_gestion        1 ─── * fact_presupuesto
dim_jerarquia_comercial   1 ─── * fact_presupuesto
dim_aliado                1 ─── * fact_presupuesto

dim_tiempo                1 ─── * fact_gestion_tmk
dim_region                1 ─── * fact_gestion_tmk
dim_jerarquia_comercial   1 ─── * fact_gestion_tmk
dim_aliado                1 ─── * fact_gestion_tmk
dim_campana               1 ─── * fact_gestion_tmk
dim_segmento              1 ─── * fact_gestion_tmk
dim_tipo_contacto         1 ─── * fact_gestion_tmk
```

No hay relaciones físicas M:N. No hay FK entre hechos (cumplimiento vía dims conformadas).

---

## 6. Índices recomendados

| Tabla | Índice propuesto | Columnas | Motivo |
|-------|------------------|----------|--------|
| fact_ventas | `ix_fact_ventas_tiempo` | sk_tiempo | Series temporales / Power BI |
| fact_ventas | `ix_fact_ventas_validez` | sk_validez | Filtro ventas válidas |
| fact_ventas | `ix_fact_ventas_region_aliado` | sk_region, sk_aliado | Rankings Reto 1 |
| fact_ventas | `ix_fact_ventas_jerarquia` | sk_jerarquia | Cumplimiento especialista/jefe |
| fact_presupuesto | `ix_fact_presupuesto_tiempo` | sk_tiempo | Periodo |
| fact_presupuesto | `ix_fact_presupuesto_cruce` | sk_region, sk_aliado, sk_jerarquia | Join analítico vs ventas |
| fact_gestion_tmk | `ix_fact_gestion_tiempo` | sk_tiempo | Periodo gestión |
| fact_gestion_tmk | `ix_fact_gestion_campana_aliado` | sk_campana, sk_aliado | Rankings Reto 2 |
| fact_gestion_tmk | `ix_fact_gestion_tipo` | sk_tipo_contacto | % tipificación |
| dim_tiempo | `ix_dim_tiempo_periodo` | periodo_yyyymm | Lookup ETL |
| dim_aliado | (UNIQUE ya cubre) | aliado_nk | Lookup ETL |
| dim_region | (UNIQUE ya cubre) | region_nk | Lookup ETL |

PK = índice clustered lógico; UNIQUE de NK en dims = índices de lookup para ETL.

---

## 7. Justificación de decisiones físicas

| Decisión | Justificación |
|----------|---------------|
| Esquema `dwh` | Separar consumo analítico de staging futuro |
| `BIGINT` para SK | Volumen Ventas/Registros; margen de crecimiento |
| `NUMERIC` para dinero | Precisión; metas con magnitudes altas |
| `dim_validez_venta` materializada | Facilita filtro Power BI Reto 1 sin DAX opaco |
| Sin `sk_canal` en `fact_gestion_tmk` | Bus Matrix: canal en Gestión es filtro de negocio, no atributo origen |
| `sk_* = 0` No informado | Cubrir nulos de jerarquía/región en Registros |
| FK físicas en hechos | Integridad referencial Star; Power BI refleja relaciones |
| No DDL en esta subfase | Metodología: diseño → Gate → implementación SQL (Fase 3) |

---

## 8. Riesgos

| ID | Riesgo | Severidad | Mitigación |
|----|--------|-----------|------------|
| F1 | Elegir mal columna región Ventas | Alta | Decisión explícita en ETL + diccionario |
| F2 | 5 cruces Presupuesto sin regla de suma | Alta | Definir antes del DDL de carga |
| F3 | Festivos CO incorrectos | Media | Seed oficial de calendario |
| F4 | Fórmulas % Reto 2 ambiguas | Media | Documentar en vistas/DAX al implementar |
| F5 | PII en `dim_vendedor` | Media | Exclusión/pseudonimización en publicación |
| F6 | Over-indexing | Baja | Empezar con índices de §6; medir en Power BI |

---

## 9. Pendientes para la implementación SQL

1. Emitir scripts `CREATE SCHEMA` / `CREATE TABLE` / `ALTER TABLE … FK` en `sql/ddl/` (Fase 3).  
2. Seeds: miembro `sk=0`, calendario festivos CO, filas de `dim_validez_venta`.  
3. Decidir nombre final de base (`claro_dw` u otro).  
4. Regla ETL: 5 cruces Presupuesto; dedupe 55 filas exactas Ventas; 25 Registros.  
5. Mapeo región oficial Ventas.  
6. Vistas de consumo (`sql/views/`) para Power BI (opcional pero recomendado).  
7. `docker-compose.yml` con servicio PostgreSQL.  
8. Credenciales vía `.env` (ignorado por Git).  
9. Pruebas de integridad FK post-carga.  
10. Documentar fórmulas % Gestión / Contactabilidad / Efectivos al crear vistas o modelo PBI.

---

## 10. Conclusión

El Modelo Físico queda **diseñado y documentado** para PostgreSQL, alineado al Modelo Dimensional oficial:

- 13 dimensiones + 3 hechos en esquema `dwh`.  
- Tipos, PK, FK, NULL e índices recomendados.  
- Sin scripts DDL en esta subfase (según alcance).

### ¿Listo para iniciar la implementación SQL?

**Sí, condicionado al Gate** de Tech Lead / Project Owner sobre este documento.

Tras la aprobación, la siguiente actividad técnica es generar el DDL en `sql/ddl/` (inicio formal de la implementación PostgreSQL / Fase 3), **sin** adelantar ETL completo ni Power BI.
