# 02 — Reglas de Negocio

Fase: **Análisis**  
Fecha: 2026-07-25  
Insumos: `01_Perfilado_Datos.md`, `Prueba_Tecnica.pdf`, `03_Requisitos_Funcionales.md`

> Este documento separa dos orígenes de información:
>
> 1. **Reglas observadas** — derivadas del perfilado de datos (evidencia empírica).
> 2. **Reglas oficiales confirmadas** — derivadas únicamente del PDF del enunciado.
>
> No deben mezclarse. Donde una observación se alinea con el PDF, se indica en la sección de reglas oficiales.

---

## 1. Dominios de negocio identificados

| Fuente | Dominio | Descripción observada |
|--------|---------|----------------------|
| `Ventas.xlsb` | Venta cerrada | Reservas/transacciones tramitadas con valor monetario, canal, jerarquía comercial, aliado y marca del equipo |
| `Presupuesto.xlsb` | Meta comercial | Presupuesto mensual por región/canal/jerarquía/aliado, en tres medidas monetarias |
| `Registros.xlsb` | Gestión de contactabilidad | Actividad de campañas: intentos de contacto y su tipificación |

El negocio corresponde a una **operación comercial de venta telefónica y digital** (telemarketing + e-commerce) organizada por regiones, canales y jerarquía comercial (gerente → jefe → especialista), operada mediante aliados.

---

## 2. Reglas observadas por dominio

### 2.1 Ventas

| # | Regla observada | Evidencia |
|---|-----------------|-----------|
| V1 | Una venta pertenece a un único estado; el universo cargado está casi todo `Tramitada` | 243 363 de 243 414 filas; 51 `Activated` |
| V2 | Las notas de crédito se marcan con flag `SI`; la ausencia de valor implica venta sin nota de crédito | `Nota_credito`: solo `SI` (5 864) o nulo |
| V3 | Solo una minoría de ventas es financiada en cuotas (6, 12, 18, 24, 36) | `Cuotas` con 94.8% nulos |
| V4 | Una venta proviene de uno de dos orígenes operativos | `Archivo`: `Reposiciones TMK y Terminales libres` (198 852) o `Tecnologia` (44 562) |
| V5 | El valor de negocio se registra **antes de IVA** | Columna `Valor Antes de iva` |
| V6 | Un cliente puede tener múltiples compras | `Identificación` 205 143 únicos vs 243 414 filas |
| V7 | Una factura puede amparar más de una fila (posibles líneas o eventos) | 1 451 duplicados de `Código Factura` |
| V8 | El vendedor puede no estar identificado | `Cédula Vendedor` = `-` |
| V9 | Existen ventas históricas previas al periodo presupuestado | `Fecha Venta` desde 2023-09-25 |

### 2.2 Presupuesto

| # | Regla observada | Evidencia |
|---|-----------------|-----------|
| P1 | El presupuesto se define a nivel **mensual** (YYYYMM), no diario | `MES` 202601–202606 |
| P2 | El presupuesto se asigna por combinación región + canal + subcanal + categoría + unidad de gestión + jerarquía + aliado | Estructura de la hoja |
| P3 | Hay tres medidas presupuestadas: `TERMINALES`, `TECNOLOGIA` y `T&T` | Columnas monetarias |
| P4 | `T&T` se comporta como el **total** de TERMINALES + TECNOLOGIA | En muestras: 3 552 987 = 3 094 690 + 458 297; sumas globales consistentes (282 090 M + 81 463 M ≈ 363 553 M) |
| P5 | El presupuesto cubre el primer semestre 2026 | 202601–202606 |
| P6 | Un mismo cruce dimensional puede aparecer más de una vez con **medidas distintas** (no son copias idénticas) | 5 cruces × 2 filas; duplicados exactos = 0 — ver `02_Declaracion_Grano.md` |

### 2.3 Registros (gestión)

| # | Regla observada | Evidencia |
|---|-----------------|-----------|
| R1 | La gestión se clasifica en tres resultados: `CONTACTOS EFECTIVOS`, `CONTACTOS NO EFECTIVOS`, `NO CONTACTOS` | `TIPO_CONTACTO` |
| R2 | Cada tipo de contacto se detalla con una tipificación (`DETALLE1`): NO_VENTA, NO CONTESTAN, CONTESTADOR, VOLVER A LLAMAR, CLIENTE CUELGA, TELEFONO ERRADO, etc. | 13 valores |
| R3 | La gestión se organiza por **campañas** con convención de nombre `SEGMENTO_DETALLE_MONTO` (p. ej. `MIGRACION_MOVIL_GR_30K`) | 96 campañas |
| R4 | Los segmentos de negocio incluyen: MIGRACION, PORTABILIDAD, TT, Fijo, Adicionales, Movil | `SEGMENTO` (con variantes sucias del mismo concepto) |
| R5 | La gestión registra `CANTIDAD` (volumen) e `INTENTOS` (esfuerzo de marcación) | Medidas |
| R6 | Los datos se cargan por lotes (`FECHA_CARGUE`), típicamente al inicio de mes con recargas posteriores | 22 fechas de cargue; concentración en día 1 |
| R7 | Parte de la gestión no tiene región asignada | `SIN_REGION`, `SIN REGION COMERCIAL` |
| R8 | La atribución a jefe/especialista solo existe para ~31% de los registros | 68.9% nulos en ambas columnas |

---

## 3. Reglas transversales (conformidad entre fuentes)

| # | Regla observada | Implicación |
|---|-----------------|-------------|
| T1 | Región, Canal, CANAL2 y CATEGORIA comparten catálogo entre Presupuesto y Ventas | Atributos integrables directamente |
| T2 | La jerarquía comercial (gerente → jefe → especialista) existe en las tres fuentes pero con **catálogos de distinto alcance** | Se requiere catálogo maestro; no forzar cruces estrictos |
| T3 | El aliado aparece con nombre distinto por fuente (`DESCRIP2`, `GV_Desc2`, `ALIADO`) pero mismo dominio de valores | Homologación de nombre de campo |
| T4 | El periodo es la unidad natural de comparación entre dominios (venta real vs presupuesto vs gestión) | Comparaciones válidas solo en rango común (202604–202606 para las tres fuentes; 202601–202606 para venta vs presupuesto) |
| T5 | Los nombres de persona/aliado están anonimizados (`Especialista 000xx`, `Aliado 000xx`) | Datos de prueba; aún así hay PII real en cédulas/identificaciones |

---

## 4. Preguntas abiertas (estado tras validación del PDF)

| # | Pregunta original | Estado | Comentario |
|---|-------------------|--------|------------|
| 1 | ¿Grano oficial de una venta (`Código Factura` duplicado)? | **Abierta** | El PDF no define el grano |
| 2 | ¿Duplicados dimensionales de Presupuesto: sumar o depurar? | **Abierta** | El PDF no lo define |
| 3 | ¿Ventas históricas fuera del semestre entran al alcance? | **Resuelta (PDF)** — **análisis histórico** | El enunciado menciona ventas de los últimos seis meses. **Análisis histórico realizado durante el diseño. No corresponde al comportamiento final implementado.** (no hay filtro de horizonte en el ETL vigente). |
| 4 | ¿`Activated` cuenta como venta válida? | **Parcialmente resuelta** | El PDF define validez solo por factura + sin nota crédito; no menciona el estado |
| 5 | ¿Las notas de crédito restan / excluyen del cumplimiento? | **Resuelta (PDF)** | Ventas con nota crédito **no** son válidas |
| 6 | ¿Columna oficial de región en Ventas? | **Abierta** | El PDF no indica cuál de las columnas de región usar |
| 7 | ¿Política de PII para publicación? | **Abierta** | Fuera del enunciado; decisión de portafolio/PO |

Vacíos adicionales del PDF (fórmulas de % gestión/contactabilidad, medida de presupuesto vs ventas, recalculo dinámico detallado, festivos, nivel de meta diaria): ver `03_Requisitos_Funcionales.md` §8.

---

## 5. REGLAS OFICIALES CONFIRMADAS

> Origen: **únicamente** `Prueba_Tecnica.pdf`.  
> Detalle y trazabilidad de requisitos: `03_Requisitos_Funcionales.md`.

| # | Regla oficial | Relación con observaciones de datos |
|---|---------------|--------------------------------------|
| O1 | Ventas válidas (Reto 1) = tienen **código de factura** y **no** presentan nota crédito | Compatible con V2 (`Nota_credito` = `SI` o nulo) y con nulos/duplicados de `Código Factura` (V7): las sin factura quedan fuera |
| O2 | Días hábiles = lunes a sábado; excluir domingos y festivos nacionales de Colombia | No observable en las fuentes; regla de calendario externa |
| O3 | Meta diaria = meta mensual ÷ días hábiles del mes | Presupuesto llega mensual (P1); el desglose diario es regla de negocio, no columna fuente |
| O4 | Si no se cumple la meta diaria, el déficit se acumula al siguiente día hábil | Regla de cálculo; no está materializada en las fuentes |
| O5 | Si se supera la meta diaria, el excedente **no** se descuenta del día siguiente | Regla de cálculo; no está materializada en las fuentes |
| O6 | La meta se recalcula dinámicamente según avance y días hábiles restantes | Regla de cálculo; detalle de fórmula no especificado en el PDF |
| O7 | Reto 1 monitorea Región, Aliado, Gerente, Jefe y Especialista | Alineado con atributos presentes en Ventas/Presupuesto |
| O8 | Reto 2 aplica a registros del canal **TMK Outbound** | Compatible con presencia de `TMK OUT BOUND` en canales de otras fuentes; filtrado oficial al canal indicado |
| O9 | Horizontes: Ventas y Presupuesto = últimos 6 meses; Registros = últimos 3 meses | Compatible con cobertura observada en perfilado (P5; Registros PERIODO 202604–202606). **Análisis histórico realizado durante el diseño. No corresponde al comportamiento final implementado.** |
| O10 | Indicadores mínimos Reto 2: registros entregados, % Gestión, % Contactabilidad, % Contactos efectivos, % Contactos no efectivos | Tipos de contacto observados (R1) pueden alimentar estos %; **fórmulas exactas no están en el PDF** |

---

## 6. Trazabilidad

- Evidencia cuantitativa → `01_Perfilado_Datos.md`
- Requisitos funcionales del enunciado → `03_Requisitos_Funcionales.md`
- Diseño dimensional → Fase 2 (`docs/modelo/03_Modelo_Dimensional.md`) — **no iniciado en esta fase**
- Modelo físico → Fase 3 (`docs/modelo/04_Modelo_Fisico.md`) — **no iniciado en esta fase**
