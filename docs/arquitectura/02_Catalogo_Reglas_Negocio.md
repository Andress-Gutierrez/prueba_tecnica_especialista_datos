# 02 — Catálogo Oficial de Reglas de Negocio

----------------------------------------------------
ESTADO: CATÁLOGO OFICIAL — Subfase 4.3A  
Única fuente oficial para implementar la Subfase **4.3B** (código).  
**No inventa reglas.** Lo no documentado se marca **Pendiente**.
----------------------------------------------------

Proyecto: prueba_tecnica_especialista_datos  
Fecha: 2026-07-27  
Autor: Cursor (Senior Software Developer)

### Fuentes utilizadas

- `docs/analisis/01_Perfilado_Datos.md`
- `docs/analisis/02_Reglas_Negocio.md`
- `docs/analisis/03_Requisitos_Funcionales.md`
- `docs/modelo/02_Declaracion_Grano.md`
- `docs/modelo/03_Modelo_Dimensional.md`
- `docs/modelo/04_Modelo_Fisico.md`
- `docs/arquitectura/01_Arquitectura_ETL.md`
- Bitácora: `PROJECT_STATE.md`, `DECISION_LOG.md`, `CHANGELOG.md`, `CONTEXTO.md`

---

## 1. Resumen general

Este catálogo consolida:

1. **Reglas oficiales del enunciado** (O1–O10).
2. **Decisiones arquitectónicas de modelado** que condicionan el ETL (granos, SK, validez, sin canal físico en gestión).
3. **Reglas transversales / de calidad** documentadas con evidencia (homologación, T&T, dedupe exacto).
4. **Pendientes explícitos** (vacíos del PDF y aperturas de diseño) que **no** deben implementarse como comportamiento inventado en 4.3B.

| Categoría | Cantidad |
|-----------|----------|
| Reglas con estado **Lista** | 21 |
| Reglas / ítems con estado **Pendiente** | 11 |
| **Total ítems catalogados** | **33** |

---

## 2. Reglas documentadas (detalle)

### RN-001 — Ventas válidas (O1)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Ventas válidas Reto 1 |
| **Descripción** | Una venta es válida si tiene **código de factura presente** y **no** presenta nota crédito. |
| **Dataset origen** | Ventas |
| **Columnas involucradas** | `Código Factura` / `codigo_factura`; `Nota_credito` / `nota_credito` |
| **Tipo** | Derivación / Validación |
| **Prioridad** | Alta |
| **Salida esperada** | Flags / `sk_validez` con `es_venta_valida = tiene_factura ∧ ¬tiene_nota_credito` |
| **Tabla destino** | `dwh.dim_validez_venta`, `dwh.fact_ventas` |
| **Dimensión o hecho afectado** | `dim_validez_venta`, `fact_ventas` |
| **Dependencias** | Seed dominio validez; mapeo `Nota_credito = SI` → nota crédito |
| **Fuente documental** | `02_Reglas_Negocio.md` O1; `03_Requisitos_Funcionales.md` §4.1; `03_Modelo_Dimensional.md` D9 |
| **Estado** | Lista |

### RN-002 — Días hábiles Colombia (O2)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Calendario hábil corporativo (única fuente `dim_tiempo`) |
| **Descripción** | Días hábiles = no domingo y no festivo nacional CO. La **única fuente oficial** es `dwh.dim_tiempo` (`es_habil`, `es_festivo`, `nombre_festivo`), poblada por `calendar_seed_dag` / API `festivos.com.co`. El ETL comercial **no** recalcula festivos ni días hábiles de forma independiente. |
| **Dataset origen** | Master Data calendario → `dim_tiempo` |
| **Columnas involucradas** | `es_habil`, `es_festivo`, `nombre_festivo` (+ compat. `es_dia_habil`, `es_festivo_co`) |
| **Tipo** | Derivación / Master Data |
| **Prioridad** | Alta |
| **Salida esperada** | Atributos de `dim_tiempo` oficiales para meta diaria / Presupuesto |
| **Tabla destino** | `dwh.dim_tiempo` |
| **Dimensión o hecho afectado** | `dim_tiempo` |
| **Dependencias** | `calendar_seed_dag`; RN-003…RN-006 |
| **Fuente documental** | `02_Reglas_Negocio.md` O2; `04_Modelo_Fisico.md` §4.1 `dim_tiempo`; Subfase 5.5.3 |
| **Estado** | Lista — materializada en `dim_tiempo` |

### RN-003 — Meta diaria (O3)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Meta diaria = meta mensual ÷ días hábiles del mes |
| **Descripción** | La meta diaria se calcula a partir de la meta mensual y los días hábiles del mes. |
| **Dataset origen** | Presupuesto (+ calendario) |
| **Columnas involucradas** | Medidas presupuesto (`TERMINALES` / `TECNOLOGIA` / `T&T` — cuál usar: Pendiente); atributos `dim_tiempo` |
| **Tipo** | Derivación |
| **Prioridad** | Alta |
| **Salida esperada** | Valor de meta diaria por cruce y día hábil (consumo analítico / DAX o vista; **no** es grano de `fact_presupuesto`) |
| **Tabla destino** | Cálculo sobre `fact_presupuesto` + `dim_tiempo` (no nuevo hecho) |
| **Dimensión o hecho afectado** | `fact_presupuesto`, `dim_tiempo` |
| **Dependencias** | RN-002; RN-P03 (medida); RN-P10 (nivel) |
| **Fuente documental** | O3; `03_Modelo_Dimensional.md` D10 |
| **Estado** | Lista *(principio)* |

### RN-004 — Acumulación de déficit (O4)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Déficit acumula al siguiente día hábil |
| **Descripción** | Si no se cumple la meta diaria, el déficit se acumula al siguiente día hábil. |
| **Dataset origen** | Derivado (Ventas válidas vs Presupuesto) |
| **Columnas involucradas** | Medidas de venta válida vs meta diaria |
| **Tipo** | Derivación |
| **Prioridad** | Alta |
| **Salida esperada** | Déficit acumulado día a día hábil |
| **Tabla destino** | Capa analítica / DAX / vista (no hecho adicional documentado) |
| **Dimensión o hecho afectado** | Consumo Reto 1 |
| **Dependencias** | RN-001, RN-003; detalle de fórmula con RN-006 → Pendiente RN-P04 |
| **Fuente documental** | O4; `03_Requisitos_Funcionales.md` |
| **Estado** | Lista *(principio)* |

### RN-005 — Excedente no descuenta (O5)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Excedente no reduce meta del día siguiente |
| **Descripción** | Si se supera la meta diaria, el excedente no se descuenta de la meta del día siguiente. |
| **Dataset origen** | Derivado |
| **Columnas involucradas** | Meta diaria / ventas válidas |
| **Tipo** | Derivación |
| **Prioridad** | Alta |
| **Salida esperada** | Cumplimiento diario sin arrastre negativo del excedente |
| **Tabla destino** | Capa analítica / DAX / vista |
| **Dimensión o hecho afectado** | Consumo Reto 1 |
| **Dependencias** | RN-003, RN-004 |
| **Fuente documental** | O5 |
| **Estado** | Lista |

### RN-006 — Recalculo dinámico de meta (O6)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Recalculo dinámico según avance y días hábiles restantes |
| **Descripción** | La meta se recalcula dinámicamente según avance y días hábiles restantes. |
| **Dataset origen** | Derivado |
| **Columnas involucradas** | Meta mensual, días hábiles restantes, avance |
| **Tipo** | Derivación |
| **Prioridad** | Alta |
| **Salida esperada** | Meta ajustada dinámicamente |
| **Tabla destino** | Capa analítica / DAX / vista |
| **Dimensión o hecho afectado** | Consumo Reto 1 |
| **Dependencias** | RN-002…RN-005; **fórmula exacta Pendiente (RN-P04)** |
| **Fuente documental** | O6; vacío V4 en `03_Requisitos_Funcionales.md` |
| **Estado** | Lista *(principio)* / detalle **Pendiente** |

### RN-007 — Dimensiones de monitoreo Reto 1 (O7)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Monitoreo por Región, Aliado, Gerente, Jefe, Especialista |
| **Descripción** | El Reto 1 monitorea desempeño en Región, Aliado, Gerente, Jefe y Especialista. |
| **Dataset origen** | Ventas, Presupuesto |
| **Columnas involucradas** | Región(es); aliado; gerente; jefe; especialista |
| **Tipo** | Validación (alcance analítico) |
| **Prioridad** | Alta |
| **Salida esperada** | KPIs filtrables por esas dimensiones |
| **Tabla destino** | `fact_ventas`, `fact_presupuesto` + dims conformadas |
| **Dimensión o hecho afectado** | `dim_region`, `dim_aliado`, `dim_jerarquia_comercial` |
| **Dependencias** | Homologación de jerarquía/aliado |
| **Fuente documental** | O7 |
| **Estado** | Lista |

### RN-008 — Alcance TMK Outbound (O8)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Reto 2 = canal TMK Outbound |
| **Descripción** | El seguimiento de gestión aplica a registros del canal **TMK Outbound**. |
| **Dataset origen** | Registros (+ filtro de negocio; fuente sin columna CANAL homónima) |
| **Columnas involucradas** | N/A en Registros; filtro documentado como regla de negocio, no FK `sk_canal` en hecho |
| **Tipo** | Validación / Transformación (filtro) |
| **Prioridad** | Alta |
| **Salida esperada** | Universo Reto 2 acotado a TMK Outbound |
| **Tabla destino** | `fact_gestion_tmk` (sin `sk_canal` físico) |
| **Dimensión o hecho afectado** | `fact_gestion_tmk` |
| **Dependencias** | Decisión Bus Matrix / Modelo Físico: sin `sk_canal` en el hecho |
| **Fuente documental** | O8; `03_Modelo_Dimensional.md`; `04_Modelo_Fisico.md` |
| **Estado** | Lista |

### RN-010 — Indicadores mínimos Reto 2 (O10)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | KPIs mínimos gestión TMK |
| **Descripción** | Deben existir: registros entregados, % Gestión, % Contactabilidad, % Contactos efectivos, % Contactos no efectivos. |
| **Dataset origen** | Registros |
| **Columnas involucradas** | `CANTIDAD`, `INTENTOS`, `TIPO_CONTACTO`, `DETALLE1` (y posiblemente otras) |
| **Tipo** | Derivación |
| **Prioridad** | Alta |
| **Salida esperada** | Medidas / DAX / vistas con esos nombres de KPI |
| **Tabla destino** | Consumo sobre `fact_gestion_tmk` + dims |
| **Dimensión o hecho afectado** | `fact_gestion_tmk`, `dim_tipo_contacto` |
| **Dependencias** | **Fórmulas exactas Pendiente (RN-P01, RN-P02)** |
| **Fuente documental** | O10; R1 observado |
| **Estado** | Lista *(existencia de KPIs)* / fórmulas **Pendiente** |

### RN-011 — Grano de Ventas

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Grano Ventas = 1 evento/fila fuente |
| **Descripción** | No colapsar por `Código Factura`. 1 fila en origen transformado = 1 fila en `fact_ventas`. |
| **Dataset origen** | Ventas |
| **Columnas involucradas** | Todas las de la fila; `codigo_factura` degenerado |
| **Tipo** | Validación |
| **Prioridad** | Alta |
| **Salida esperada** | `fact_ventas` al grano declarado |
| **Tabla destino** | `dwh.fact_ventas` |
| **Dimensión o hecho afectado** | `fact_ventas` |
| **Dependencias** | RN-012 |
| **Fuente documental** | `02_Declaracion_Grano.md`; `03_Modelo_Dimensional.md` D3 |
| **Estado** | Lista |

### RN-012 — Código Factura no es clave natural

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Prohibido usar Código Factura como PK/identidad |
| **Descripción** | `Código Factura` no es BK única; se usa SK + atributo degenerado. |
| **Dataset origen** | Ventas |
| **Columnas involucradas** | `Código Factura` |
| **Tipo** | Validación |
| **Prioridad** | Alta |
| **Salida esperada** | `sk_venta` generado por ETL |
| **Tabla destino** | `fact_ventas` |
| **Dimensión o hecho afectado** | `fact_ventas` |
| **Dependencias** | DEC-007 / 02A |
| **Fuente documental** | `02A_Analisis_Claves.md`; D5 |
| **Estado** | Lista |

### RN-013 — Surrogate keys obligatorias

| Campo | Contenido |
|-------|-----------|
| **Nombre** | SK obligatorias en dims y hechos |
| **Descripción** | Toda dimensión y hecho usa `sk_*`; lookup por NK en carga. |
| **Dataset origen** | Todos |
| **Columnas involucradas** | NK por dimensión; SKs en hechos |
| **Tipo** | Transformación |
| **Prioridad** | Alta |
| **Salida esperada** | Integridad referencial Star |
| **Tabla destino** | Todas las tablas `dwh.*` |
| **Dimensión o hecho afectado** | Todas |
| **Dependencias** | Seeds `sk=0` |
| **Fuente documental** | D4; `04_Modelo_Fisico.md` |
| **Estado** | Lista |

### RN-014 — Miembro No informado (sk = 0)

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Miembro desconocido sk=0 |
| **Descripción** | Ante nulo / no homologable → mapear a `sk = 0` (“No informado”), sin inventar miembros de negocio. |
| **Dataset origen** | Todos (especialmente Registros jerarquía/región) |
| **Columnas involucradas** | FKs dimensionales |
| **Tipo** | Transformación |
| **Prioridad** | Alta |
| **Salida esperada** | Hechos siempre con SK resuelta |
| **Tabla destino** | Dims + hechos |
| **Dimensión o hecho afectado** | Conformadas/exclusivas con seed |
| **Dependencias** | DML seed `01_seed_miembro_no_informado.sql` |
| **Fuente documental** | `04_Modelo_Fisico.md` convenciones; `01_Arquitectura_ETL.md` §5 |
| **Estado** | Lista |

### RN-015 — Validez materializada como dimensión

| Campo | Contenido |
|-------|-----------|
| **Nombre** | `dim_validez_venta` materializada |
| **Descripción** | La validez O1 se materializa como dimensión (no solo flags opacos en el hecho). |
| **Dataset origen** | Ventas |
| **Columnas involucradas** | Factura / nota crédito → `sk_validez` |
| **Tipo** | Derivación |
| **Prioridad** | Alta |
| **Salida esperada** | FK `fact_ventas.sk_validez` |
| **Tabla destino** | `dim_validez_venta`, `fact_ventas` |
| **Dimensión o hecho afectado** | Ambos |
| **Dependencias** | RN-001; seed `02_seed_dim_validez_venta.sql` |
| **Fuente documental** | `04_Modelo_Fisico.md`; modelo dimensional |
| **Estado** | Lista |

### RN-016 — Meta diaria no es grano de Presupuesto

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Meta diaria = cálculo sobre Tiempo |
| **Descripción** | No crear cuarto proceso ni cambiar el grano mensual de `fact_presupuesto`. |
| **Dataset origen** | Presupuesto |
| **Columnas involucradas** | Medidas mensuales + `dim_tiempo` |
| **Tipo** | Validación (diseño) |
| **Prioridad** | Alta |
| **Salida esperada** | Presupuesto permanece mensual |
| **Tabla destino** | `fact_presupuesto` |
| **Dimensión o hecho afectado** | `fact_presupuesto`, `dim_tiempo` |
| **Dependencias** | RN-003…RN-006 |
| **Fuente documental** | D10; `01_Arquitectura_ETL.md` |
| **Estado** | Lista |

### RN-017 — Sin sk_canal en fact_gestion_tmk

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Gestión sin FK de canal física |
| **Descripción** | `fact_gestion_tmk` no incluye `sk_canal`; el filtro TMK Outbound es regla de negocio (RN-008). |
| **Dataset origen** | Registros |
| **Columnas involucradas** | N/A en hecho |
| **Tipo** | Validación |
| **Prioridad** | Alta |
| **Salida esperada** | DDL/carga sin columna canal en el hecho |
| **Tabla destino** | `fact_gestion_tmk` |
| **Dimensión o hecho afectado** | `fact_gestion_tmk` |
| **Dependencias** | RN-008 |
| **Fuente documental** | `04_Modelo_Fisico.md`; Bus Matrix |
| **Estado** | Lista |

### RN-018 — Grano Presupuesto mensual

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Grano Presupuesto = asignación mensual al cruce |
| **Descripción** | 1 fila = 1 meta mensual al cruce de atributos dimensionales documentados. |
| **Dataset origen** | Presupuesto |
| **Columnas involucradas** | MES + REGION + CANAL + CANAL2 + SUB CANAL + CATEGORIA + UNIDAD DE GESTION + ESPECIALISTA + JEFE + GERENTE + DESCRIP2 + medidas |
| **Tipo** | Validación |
| **Prioridad** | Alta |
| **Salida esperada** | `fact_presupuesto` al grano declarado |
| **Tabla destino** | `fact_presupuesto` |
| **Dimensión o hecho afectado** | `fact_presupuesto` |
| **Dependencias** | Tratamiento de 5 cruces → Pendiente RN-P08 |
| **Fuente documental** | `02_Declaracion_Grano.md` |
| **Estado** | Lista |

### RN-019 — Grano Gestión TMK agregado

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Grano Gestión = agregado tipificado |
| **Descripción** | 1 fila = agregado con `cantidad`/`intentos`; no modelar contacto unitario. |
| **Dataset origen** | Registros |
| **Columnas involucradas** | `CANTIDAD`, `INTENTOS`, tipificación, dims |
| **Tipo** | Validación |
| **Prioridad** | Alta |
| **Salida esperada** | `fact_gestion_tmk` al grano agregado |
| **Tabla destino** | `fact_gestion_tmk` |
| **Dimensión o hecho afectado** | `fact_gestion_tmk` |
| **Dependencias** | — |
| **Fuente documental** | `02_Declaracion_Grano.md`; modelo dimensional |
| **Estado** | Lista |

### RN-020 — Homologación de aliado entre fuentes

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Homologar DESCRIP2 / GV_Desc2 / ALIADO |
| **Descripción** | Mismo dominio de aliado con nombres de campo distintos por fuente. |
| **Dataset origen** | Presupuesto, Ventas, Registros |
| **Columnas involucradas** | `DESCRIP2`, `GV_Desc2`, `ALIADO` |
| **Tipo** | Transformación |
| **Prioridad** | Media |
| **Salida esperada** | `dim_aliado` única / `aliado_nk` |
| **Tabla destino** | `dim_aliado` |
| **Dimensión o hecho afectado** | `dim_aliado` + hechos |
| **Dependencias** | RN-013 |
| **Fuente documental** | T3 `02_Reglas_Negocio.md`; modelo físico observaciones |
| **Estado** | Lista |

### RN-021 — T&T como total TERMINALES + TECNOLOGIA

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Consistencia T&T |
| **Descripción** | Observado: `T&T` se comporta como total de TERMINALES + TECNOLOGIA (100% filas en evidencia). |
| **Dataset origen** | Presupuesto |
| **Columnas involucradas** | `TERMINALES`, `TECNOLOGIA`, `T&T` |
| **Tipo** | Validación |
| **Prioridad** | Media |
| **Salida esperada** | Carga de las tres medidas; CHECK opcional documentado en físico |
| **Tabla destino** | `fact_presupuesto` |
| **Dimensión o hecho afectado** | `fact_presupuesto` |
| **Dependencias** | — |
| **Fuente documental** | P4 `02_Reglas_Negocio.md`; `04_Modelo_Fisico.md` |
| **Estado** | Lista |

### RN-022 — Nota crédito = SI o nulo

| Campo | Contenido |
|-------|-----------|
| **Nombre** | Semántica observada de Nota_credito |
| **Descripción** | Flag `SI` indica nota crédito; ausencia (nulo) implica sin nota crédito (soporta O1). |
| **Dataset origen** | Ventas |
| **Columnas involucradas** | `Nota_credito` |
| **Tipo** | Transformación |
| **Prioridad** | Alta |
| **Salida esperada** | `tiene_nota_credito` booleano |
| **Tabla destino** | `dim_validez_venta` / hecho |
| **Dimensión o hecho afectado** | Validez |
| **Dependencias** | RN-001 |
| **Fuente documental** | V2 `02_Reglas_Negocio.md` |
| **Estado** | Lista |

---

## 3. Reglas / ítems RN-P*

### 3.1 Implementadas

| ID | Nombre | Descripción | Prioridad | Fuente | Estado |
|----|--------|-------------|-----------|--------|--------|
| RN-P05 | Fuente festivos Colombia | `calendar_seed_dag` + API oficial `festivos.com.co` + `dwh.dim_tiempo` (`es_habil` / `es_festivo` / `nombre_festivo`) | Alta | V5; F3 físico; Subfases 5.6 / 5.5.3 | **Implementada** |

### 3.2 Pendientes

| ID | Nombre | Descripción (solo lo documentado como vacío) | Prioridad | Fuente | Estado |
|----|--------|-----------------------------------------------|-----------|--------|--------|
| RN-P01 | Fórmulas % Reto 2 | Numerador/denominador de % Gestión, Contactabilidad, Efectivos, No efectivos | Alta | V1 requisitos | Pendiente |
| RN-P02 | Definición “registros entregados” | ¿Suma `CANTIDAD` vs conteo de filas? | Alta | V2 | Pendiente |
| RN-P03 | Medida presupuesto vs ventas | ¿`TERMINALES` / `TECNOLOGIA` / `T&T`? | Alta | V3 | Pendiente |
| RN-P04 | Detalle recalculo + déficit | Orden de operaciones / fórmula exacta | Alta | V4; O6 | Pendiente |
| RN-P06 | Estado reserva en validez | ¿`Tramitada`/`Activated` además de O1? | Media | V6 | Pendiente |
| RN-P07 | Grano vs factura duplicada (operativo ETL) | PDF no define; **modelo sí fijó grano=fila** (RN-011). Pendiente solo si se reabre | Baja | V7 (cerrado en diseño) | Pendiente *(solo si Gate reabre)* |
| RN-P08 | 5 cruces Presupuesto | Sumar u otra consolidación de medidas distintas | Alta | V8; P6; físico §9 | Pendiente |
| RN-P09 | Columna región oficial Ventas | ¿`Región Comercial` / `GV-Division` / `D_Division`? | Alta | V9 | Pendiente |
| RN-P10 | Nivel de meta diaria | ¿Aliado / especialista / región / todos? | Alta | V10 | Pendiente |
| RN-P11 | Campo “cantidad” de Ventas en PDF | Identificación del campo en fuente | Baja | V11 | Pendiente |
| RN-P12 | Normalización SEGMENTO | Limpieza variantes (`Adicionales_` → `Adicionales`) documentada como pendiente ETL | Media | `04_Modelo_Fisico.md` / análisis | Pendiente |

---

## 4. Clasificación por dataset

| Dataset | Reglas Lista | Pendientes relacionadas |
|---------|--------------|-------------------------|
| Ventas | RN-001, 007, 011, 012, 015, 020, 022 | RN-P06, P09, P11 |
| Presupuesto | RN-003, 007, 016, 018, 020, 021 | RN-P03, P08, P10 |
| Registros / TMK | RN-008, 010, 017, 019, 020 | RN-P01, P02, P12 |
| Calendario / transversal | RN-002, 004, 005, 006, 013, 014 (+ RN-P05 implementada) | RN-P04 |

---

## 5. Clasificación por tabla destino

| Tabla / capa | Reglas |
|--------------|--------|
| `dim_tiempo` | RN-002, 003, 016 |
| `dim_validez_venta` / `fact_ventas` | RN-001, 011, 012, 015, 022 |
| `fact_presupuesto` | RN-003, 016, 018, 021 |
| `fact_gestion_tmk` | RN-008, 010, 017, 019 |
| `dim_aliado` / jerarquía / región | RN-007, 014, 020 |
| Capa analítica / DAX / vistas | RN-003…006, 010 |

---

## 6. Clasificación por prioridad

| Prioridad | Lista | Pendiente |
|-----------|-------|-----------|
| Alta | RN-001…019, 022 (mayoría; sin RN-009) | RN-P01…P04, P08…P10 |
| Media | RN-020, 021 | RN-P06, P12 |
| Baja | — | RN-P07, P11 |

---

## 7. Reglas reutilizables

Aplican a más de un dataset o a toda la carga:

- RN-013 Surrogate keys  
- RN-014 Miembro `sk=0`  
- RN-020 Homologación de aliado  
- RN-002 Calendario hábil (única fuente: `dim_tiempo` / `calendar_seed_dag`)

---

## 8. Reglas pendientes (lista corta)

Ver §3 (RN-P01 … RN-P12). **No implementar comportamiento inventado** en 4.3B hasta decisión PO/Tech Lead registrada.

---

## 9. Riesgos

| Riesgo | Origen |
|--------|--------|
| Implementar % Reto 2 con fórmula no oficial | RN-P01 |
| Elegir mal columna de región | RN-P09 |
| Consolar mal los 5 cruces de Presupuesto | RN-P08 |
| Festivos incorrectos → meta diaria errónea | Mitigado: RN-P05 implementada (`calendar_seed_dag` + API + `dim_tiempo`) |
| Confundir meta diaria con grano de presupuesto | Mitigado por RN-016 |

---

## 10. Supuestos (solo documentados)

1. Las fuentes `data/raw/*.xlsb` son inmutables (`01_Arquitectura_ETL.md`).  
2. Full load inicial en Fase 4 (`01_Arquitectura_ETL.md`).  
3. Power BI consume solo PostgreSQL (`CONTEXTO.md`).  
4. Airflow no contiene lógica de negocio (`CONTEXTO.md`).  
5. Arquitectura dimensional/física congelada (DEC-012).

---

## 11. Fuera de alcance de este catálogo / 4.3B

- Código Python de reglas (Subfase **4.3B**).  
- Carga a PostgreSQL (4.4–4.5).  
- Orquestación Airflow (Fase 5).  
- Medidas DAX definitivas en Power BI (Fase 6), salvo que reutilicen este catálogo.  
- Inventar fórmulas para RN-P01…P12.

---

## 12. Conclusión

El catálogo deja **22 reglas Lista** (oficiales + de modelado/ETL documentadas) y **12 pendientes** explícitos. La Subfase **4.3B** deberá implementar únicamente ítems **Lista**, y registrar en `DECISION_LOG` / `PROJECT_STATE` cualquier resolución de pendientes antes de codificarlos.

**Próximo paso autorizado:** Gate de este documento → Subfase **4.3B Implementación de reglas de negocio en código**.
