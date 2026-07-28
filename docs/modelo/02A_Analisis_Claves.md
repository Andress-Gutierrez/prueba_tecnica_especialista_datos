# 02A — Análisis de Claves Naturales

Fase: **2 — Diseño del Data Warehouse**  
Subfase: **2.2 (precursor) — Validación de claves naturales**  
Fecha: 2026-07-26  
Insumos: `data/raw/*.xlsb`  
Scripts: `scripts/audit_natural_keys.py`, `scripts/summarize_key_audit.py`  
Anexo: `docs/modelo/anexo_ventas_codigos_factura_duplicados.csv` (listado completo de códigos duplicados)

> Auditoría solicitada por el Tech Lead.  
> Toda afirmación está respaldada por evidencia cuantitativa.  
> No se diseñan hechos, dimensiones ni implementaciones en esta sesión.

---

# 1. Ventas.xlsb — auditoría de claves

## 1.1 ¿Existe una clave natural?

**No.** No se observó ninguna columna ni combinación evaluada que identifique de forma única, no nula y estable cada evento de venta.

## 1.2 ¿Qué columna(s) la conformarían (candidatas)?

Candidata principal evaluada: **`Código Factura`**.  
Otras candidatas evaluadas: `Identificación`; combinaciones con fecha, vendedor, marca y valor.

## 1.3 ¿Es única?

**`Código Factura`: No.**

## 1.4 ¿Contiene valores nulos?

**Sí:** 669 nulos.

## 1.5 ¿Es estable?

**No como identificador del evento.** El mismo código puede asociarse a clientes, valores, marcas, fechas y jerarquías distintas.

## 1.6 ¿Representa realmente el evento de negocio?

**No de forma unívoca.** Una fila representa el evento/registro transaccional; `Código Factura` es un atributo frecuente pero **no** el identificador único del evento.

---

# 2. Auditoría completa — `Código Factura`

### Hipótesis bajo prueba (Subfase 2.1.1)

> “`Código Factura` no es clave natural.”

### Evidencia cuantitativa

| Métrica | Valor |
|---------|------:|
| Número total de filas | **243 414** |
| Valores no nulos de `Código Factura` | **242 745** |
| Valores nulos | **669** |
| Valores distintos (no nulos) | **241 294** |
| Valores distintos que aparecen más de una vez | **1 446** |
| Filas que pertenecen a esos valores duplicados | **2 897** |
| Filas “extra” por repetición (`sum(count-1)`) | **1 451** |
| Distribución de repeticiones | **1 445** códigos aparecen **2** veces; **1** código (`ENCI`) aparece **7** veces |

### Relación aritmética (demostración de no unicidad)

```
valores distintos no nulos + filas extra por duplicación + nulos
= 241 294 + 1 451 + 669
= 243 414  (= total de filas)
```

Si `Código Factura` fuera única y no nula, se cumpliría:

`valores distintos = total de filas` → **falso** (241 294 ≠ 243 414).

### Listado de valores duplicados

Listado **completo** de los **1 446** códigos duplicados con su frecuencia:

→ `docs/modelo/anexo_ventas_codigos_factura_duplicados.csv`

Muestra (máxima frecuencia y ejemplos):

| Código Factura | Ocurrencias |
|----------------|------------:|
| ENCI | 7 |
| 3227034 | 2 |
| 3140498 | 2 |
| 3126364 | 2 |
| … (1 442 códigos más con 2 ocurrencias) | 2 |

### Qué columnas cambian entre registros del mismo código

Frecuencia: en cuántos de los 1 446 códigos duplicados la columna **no es constante**:

| Columna | # códigos donde varía |
|---------|----------------------:|
| Cédula Vendedor | 1 385 |
| GV_Desc2 (aliado) | 1 318 |
| GV-Especialista | 1 293 |
| GV-JEFE 1 CANAL REGIONAL | 1 155 |
| CANAL2 | 1 139 |
| Región Comercial | 1 093 |
| CATEGORIA | 1 081 |
| Fecha Venta | 471 |
| Identificación (cliente) | 467 |
| Valor Antes de iva | 263 |
| Marca | 5 |

Resumen de estabilidad del significado de negocio en códigos duplicados:

| Condición | # códigos duplicados afectados |
|-----------|-------------------------------:|
| Más de una `Fecha Venta` | 471 |
| Más de un cliente (`Identificación`) | 467 |
| Más de un `Valor Antes de iva` | 263 |
| Más de una `Marca` | 5 |

### Ejemplos demostrativos

**A) `ENCI` (7 filas)** — mismo “código”, eventos distintos:

| Fecha Venta | Identificación | Vendedor | Marca | Valor | Aliado |
|-------------|----------------|----------|-------|------:|--------|
| 20260228 | 1000111790 | 1000231 | HONOR | 1 680 588 | Aliado 00023 |
| 20260331 | 1000163833 | 1000368 | SONY | 2 773 025 | Aliado 00023 |
| 20260331 | 1000065728 | 1000368 | HONOR | 1 099 520 | Aliado 00023 |
| … | … | … | … | … | … |

Conclusión del ejemplo: `ENCI` no identifica un único evento.

**B) `3140498` (2 filas)** — mismo código, distinto cliente/fecha/vendedor/aliado/especialista:

| Fecha Venta | Identificación | Vendedor | Especialista | Aliado | Valor | Marca |
|-------------|----------------|----------|--------------|--------|------:|-------|
| 20260129 | 1000109972 | 1000269 | Especialista 00009 | Aliado 00023 | 3 025 126 | HP |
| 20251231 | 1000145250 | 1000841 | Especialista 00007 | Aliado 00028 | 3 025 126 | HP |

**C) `3227034` (2 filas)** — casi idénticas (posible retrabajo/duplicado operativo); aún así el código solo no basta como PK de negocio porque el patrón global no es 1:1.

### Otras candidatas (también descartadas como clave natural única)

| Candidata | Nulos en clave | Duplicados (filas) | ¿Única? |
|-----------|---------------:|------------------:|---------|
| `Identificación` | 32 | 38 239 | No |
| `Código Factura` + `Identificación` | 701 | 979 | No |
| `Código Factura` + `Fecha Venta` + `Identificación` | 701 | 975 | No |
| `Código Factura` + `Cédula Vendedor` + `Fecha Venta` + `Valor` + `Marca` | 669 | 53 | No |

### Veredicto `Código Factura`

**CONFIRMADO: no es clave natural.**

Motivos demostrados:

1. Tiene **nulos** (669).  
2. No es **única** (1 446 valores repetidos).  
3. No es **estable** como identidad del evento (mismas facturas con distinto cliente/valor/jerarquía).  
4. Por tanto **no representa unívocamente** el evento de negocio.

La afirmación de la Subfase 2.1.1 **se mantiene**. **No requiere corrección.**

---

# 3. Presupuesto.xlsb — auditoría de claves

## 3.1 ¿Existe una clave natural?

**No de forma perfecta.** Existe una **clave compuesta candidata** (cruce dimensional) que es casi única, pero **no** cumple unicidad total.

## 3.2 ¿Qué columna(s) la conforman?

```
MES + REGION + CANAL + CANAL2 + SUB CANAL + CATEGORIA
+ UNIDAD DE GESTION + ESPECIALISTA + JEFE + GERENTE + DESCRIP2
```

No existe un ID de presupuesto en la fuente.

## 3.3 ¿Es única?

**No al 100%.**  
- Combinaciones distintas: **726**  
- Filas totales: **731**  
- Claves con más de una fila: **5** (cada una con 2 filas)  
- Filas duplicadas exactas (todas las columnas): **0**

## 3.4 ¿Contiene valores nulos?

**No** en ninguna de las 11 columnas de la clave compuesta (0 nulos en cada una).

## 3.5 ¿Es estable?

Parcialmente: describe el cruce de meta, pero en 5 casos el mismo cruce tiene **dos montos distintos**, por lo que la clave compuesta no identifica una sola asignación monetaria.

## 3.6 ¿Representa realmente el evento de negocio?

Representa la **asignación de meta mensual** al cruce comercial. Es el mejor candidato descriptivo, pero **no** es una clave natural limpia hasta resolver la regla de los 5 cruces.

### Detalle de las 5 claves duplicadas (evidencia)

Todas en `MES=202603`, canal telefónico TMK IN BOUND, Especialista 00019, Jefe 00007, Gerente 00005, Aliado 00008; cambian por `REGION` y las medidas:

| REGION | TERMINALES (fila1 / fila2) | TECNOLOGIA | T&T |
|--------|----------------------------|------------|-----|
| REGION CENTRO | 3.18e9 / 6.78e8 | 7.64e8 / 1.63e8 | 3.95e9 / 8.41e8 |
| REGION COSTA | 6.07e6 / 1.29e6 | 5.28e6 / 1.13e6 | 1.14e7 / 2.42e6 |
| REGION NOROCCIDENTE | 2.86e6 / 6.09e5 | 8.18e6 / 1.74e6 | 1.10e7 / 2.35e6 |
| REGION OCCIDENTE | 5.17e8 / 1.10e8 | 1.13e8 / 2.40e7 | 6.30e8 / 1.34e8 |
| REGION ORIENTE | 3.47e8 / 7.39e7 | 8.76e7 / 1.87e7 | 4.34e8 / 9.25e7 |

**Veredicto:** no hay clave natural única perfecta; la compuesta dimensional es candidata operativa con excepción documentada (5 cruces).

---

# 4. Registros.xlsb — auditoría de claves

## 4.1 ¿Existe una clave natural?

**No.**

## 4.2 ¿Qué columna(s) la conformarían?

No hay columna ID. Se probaron cruces de negocio (campaña, periodo, fecha, aliado, tipificación, región, segmento, fecha cargue) y la fila completa.

## 4.3 ¿Es única?

| Candidata | Filas evaluadas | Duplicados |
|-----------|----------------:|-----------:|
| Fila completa (todas las columnas) | 459 592 | **25** |
| Campaña+periodo+fecha+aliado+tipo+detalle+división+segmento+fecha_cargue (sin nulos en clave) | 438 696 | **3 080** |
| Misma sin `FECHA_CARGUE` | 438 696 | **54 822** |

## 4.4 ¿Contiene valores nulos?

**Sí**, en columnas del cruce de negocio (p. ej. tipificación/fecha/aliado en parte de las filas). Cualquier clave compuesta queda incompleta.

## 4.5 ¿Es estable?

No como identificador de un contacto atómico: ~**80.22%** de filas tienen `CANTIDAD > 1` (agregado).

## 4.6 ¿Representa realmente el evento de negocio?

La fila representa un **agregado de gestión**, no un registro-persona ni un ID natural de contacto.

**Veredicto:** no existe clave natural. Coherente con el grano declarado en 2.1.1.

---

# 5. VALIDACIÓN DEL TECH LEAD

## Hipótesis confirmadas

| Hipótesis | Estado | Evidencia |
|-----------|--------|-----------|
| `Código Factura` **no** es clave natural en Ventas | **CONFIRMADA** | 669 nulos; 1 446 códigos duplicados; 2 897 filas en grupos; mismos códigos con distinto cliente/valor/jerarquía |
| Ventas no tiene clave natural observada en origen | **CONFIRMADA** | Ninguna candidata evaluada es única y no nula |
| Presupuesto: cruce dimensional casi único, con 5 excepciones de medidas distintas | **CONFIRMADA** | 726 claves / 731 filas; 5×2 con montos distintos; 0 duplicados exactos |
| Registros no tiene clave natural; la fila es agregada | **CONFIRMADA** | Sin ID; duplicados en cruces; 80.22% `CANTIDAD > 1` |

## Hipótesis descartadas

| Hipótesis | Estado | Motivo |
|-----------|--------|--------|
| “`Código Factura` podría ser clave natural del sistema origen” | **DESCARTADA** | Falla unicidad, nulidad y estabilidad semántica |
| “`Identificación` podría ser clave de la venta” | **DESCARTADA** | 38 239 duplicados |
| “Existe ID de contacto en Registros” | **DESCARTADA** | No hay columna ID; claves compuestas no únicas |

## Documentos corregidos

**Ninguna corrección de sentido contrario a 2.1.1 fue necesaria.**

Se **refuerza** (no se revierte) la conclusión de `02_Declaracion_Grano.md` sobre `Código Factura`.

Documentos actualizados solo por trazabilidad de esta validación:

- Creación de este archivo `02A_Analisis_Claves.md`
- Anexo CSV de códigos duplicados
- Bitácora (`CHANGELOG.md`, `DECISION_LOG.md`, `PROJECT_STATE.md`)

No se modificó el modelo dimensional ni el físico.
