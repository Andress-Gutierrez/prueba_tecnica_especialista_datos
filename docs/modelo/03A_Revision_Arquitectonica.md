# 03A — Revisión Arquitectónica del Modelo Dimensional (Borrador)

Fase: **2 — Diseño del Data Warehouse**  
Subfase: **2.2 — Revisión arquitectónica**  
Fecha: 2026-07-26  
Documento revisado: `docs/modelo/03_Modelo_Dimensional.md` (**no modificado** en esta sesión)

### Documentos de referencia (aprobados / oficiales)

- `docs/modelo/01_Proceso_Negocio.md`
- `docs/modelo/02_Declaracion_Grano.md`
- `docs/modelo/02A_Analisis_Claves.md`
- `docs/analisis/01_Perfilado_Datos.md`
- `docs/analisis/02_Reglas_Negocio.md`
- Enunciado oficial (`Prueba_Tecnica.pdf` / `03_Requisitos_Funcionales.md`)

> Esta es una revisión de arquitectura. No implementa SQL, DDL, ETL ni Power BI.

---

## 1. Resumen ejecutivo

El borrador `03_Modelo_Dimensional.md` propone, a nivel de hipótesis:

- Tres hechos alineados a tres dominios de fuente (Ventas, Presupuesto, Gestión).
- Dimensiones compartidas (tiempo, región, canal, jerarquía, aliado) más dimensiones específicas.
- Enfoque Star Schema por defecto, con evaluación pendiente vs Snowflake en la jerarquía.

**Hallazgo central:** la **dirección arquitectónica es correcta** respecto a los tres procesos de negocio aprobados y a la necesidad de dimensiones conformadas. Sin embargo, el documento está **desactualizado** frente a la Declaración del Grano y la Auditoría de Claves ya aprobadas: aún presenta granos “por confirmar”, lista decisiones pendientes ya resueltas en parte, y no formaliza claves sustitutas ni el tratamiento de atributos degenerados (`Código Factura`, nota crédito).

**Concepto del Tech Review:** ✔ **APROBADO CON AJUSTES**

No se requiere rediseño desde cero. Sí se requiere actualizar el borrador en Subfase 2.3 con los ajustes de severidad Alta/Media listados abajo, **antes** de considerarlo modelo dimensional definitivo.

---

## 2. Validación de las tablas de hechos

### 2.1 Hecho candidato — Ventas

| Pregunta | Evaluación |
|----------|------------|
| ¿Qué proceso de negocio representa? | Proceso A — Venta comercial (cierre) |
| ¿El proceso existe y fue aprobado? | **Sí** (`01_Proceso_Negocio.md`) |
| ¿El grano coincide exactamente con el aprobado? | **Parcial.** El borrador dice “evento/línea de venta (**grano por confirmar**)”. El grano **aprobado** es: 1 fila = 1 evento/registro transaccional de venta. La dirección es correcta; la redacción está obsoleta. |
| ¿Qué métricas almacena? | Propuestas: `valor_antes_iva`; flag nota crédito; cuotas |
| ¿Qué KPIs alimenta? | Ventas válidas vs presupuesto; desempeño por región/aliado/especialista/jefe (Reto 1), aplicando filtro oficial factura + sin nota crédito |
| ¿Riesgos si se modifica el grano? | Colapsar a factura → distorsión de cumplimiento (`02_Declaracion_Grano`, `02A`) |

**Observaciones**

| ID | Severidad | Hallazgo | Justificación |
|----|-----------|----------|---------------|
| H-V1 | **Alta** | El grano del hecho Ventas debe fijarse al aprobado y eliminar “por confirmar” | Declaración del Grano y Auditoría de Claves ya cerraron este punto |
| H-V2 | **Alta** | Debe explicitarse que el hecho **no** usa `Código Factura` como clave del evento; requiere **clave sustituta** | `02A`: no hay clave natural |
| H-V3 | **Media** | `Código Factura` y flag de nota crédito deben modelarse como atributo degenerado / indicador de validez, no como identidad | Regla oficial O1; evidencia de nulos y duplicados |
| H-V4 | **Baja** | `cuotas` es medida secundaria; no alimenta KPIs obligatorios del PDF | Puede permanecer, sin priorizar |

**Veredicto hecho Ventas:** ✔ Aceptable con ajustes H-V1..H-V3.

---

### 2.2 Hecho candidato — Presupuesto

| Pregunta | Evaluación |
|----------|------------|
| ¿Qué proceso de negocio representa? | Proceso B — Planeación y seguimiento de metas |
| ¿El proceso existe y fue aprobado? | **Sí** |
| ¿El grano coincide exactamente con el aprobado? | **Casi.** El borrador lista mes × región × canal × subcanal × categoría × unidad gestión × jerarquía × aliado — alineado al cruce aprobado. Falta explicitar los 11 atributos y la excepción de 5 cruces. |
| ¿Qué métricas almacena? | `terminales`, `tecnologia`, `tyt` |
| ¿Qué KPIs alimenta? | Cumplimiento vs ventas; meta diaria / déficit (derivados por regla de negocio, no como grano de la fuente) |
| ¿Riesgos si se modifica el grano? | Agregar demasiado → no poder contrastar por aliado/especialista/jefe; ignorar duplicados dimensionales → meta incorrecta |

**Observaciones**

| ID | Severidad | Hallazgo | Justificación |
|----|-----------|----------|---------------|
| H-P1 | **Alta** | Formalizar grano exacto aprobado (11 atributos) y regla pendiente de los **5 cruces** con medidas distintas | `02` / `02A` |
| H-P2 | **Media** | Documentar que `T&T = TERMINALES + TECNOLOGIA` (100% filas) para evitar doble conteo en KPIs | Evidencia de grano/perfilado |
| H-P3 | **Media** | La meta diaria **no** es grano del hecho de presupuesto; es cálculo sobre calendario laboral | Enunciado + `01_Proceso_Negocio` |
| H-P4 | **Baja** | Incluir “unidad de gestión” de forma explícita en el diagrama futuro | Ya está en el texto del grano tentativo |

**Veredicto hecho Presupuesto:** ✔ Aceptable con ajustes H-P1..H-P3.

---

### 2.3 Hecho candidato — Gestión / contactabilidad

| Pregunta | Evaluación |
|----------|------------|
| ¿Qué proceso de negocio representa? | Proceso C — Gestión de registros TMK Outbound |
| ¿El proceso existe y fue aprobado? | **Sí** |
| ¿El grano coincide exactamente con el aprobado? | **No aún.** El borrador dice “por confirmar (posible agregado…)”. El grano **aprobado** es: 1 fila = 1 agregado tipificado (`CANTIDAD`/`INTENTOS`). |
| ¿Qué métricas almacena? | `cantidad`, `intentos` |
| ¿Qué KPIs alimenta? | Registros entregados; % gestión; % contactabilidad; % efectivos / no efectivos; rankings (Reto 2) |
| ¿Riesgos si se modifica el grano? | Tratar 1 fila = 1 contacto → KPIs rotos (~80% filas con `CANTIDAD > 1`) |

**Observaciones**

| ID | Severidad | Hallazgo | Justificación |
|----|-----------|----------|---------------|
| H-G1 | **Alta** | Fijar grano agregado tipificado; eliminar “por confirmar” | `02_Declaracion_Grano` / `02A` |
| H-G2 | **Alta** | Requiere clave sustituta; no hay clave natural | `02A` |
| H-G3 | **Media** | Las métricas de % no están en el hecho como columnas; se calculan — el borrador debe aclararlo y señalar vacío de fórmulas del PDF | `03_Requisitos_Funcionales` V1 |
| H-G4 | **Media** | Filtrar/documentar alcance TMK Outbound y filas sin tipificación (1.5%) | Regla O8 + evidencia |

**Veredicto hecho Gestión:** ✔ Aceptable con ajustes H-G1..H-G3.

---

### 2.4 Separación de procesos en hechos

| Criterio | Resultado |
|----------|-----------|
| ¿Hay un solo hecho mezclando venta + presupuesto + gestión? | **No** — el borrador separa tres hechos |
| ¿Es coherente con los 3 procesos aprobados? | **Sí** |

**Observación H-X1 (Baja):** conviene renombrar formalmente los hechos en 2.3 (p. ej. `fact_ventas`, `fact_presupuesto`, `fact_gestion_tmk`) solo tras aprobación del naming — no bloquea la revisión.

---

## 3. Validación de dimensiones

Evaluación de las dimensiones candidatas del borrador frente a procesos, hechos y claves.

| Dimensión (borrador) | Qué describe | Hechos que la usan | ¿Conformada? | ¿Surrogate Key? | ¿Clave natural en origen? | Observaciones |
|----------------------|--------------|--------------------|--------------|-----------------|---------------------------|---------------|
| Tiempo | Calendario de análisis (día/mes) | Ventas, Presupuesto, Gestión | **Sí** | **Sí** | Parcial (fechas/periodos en fuentes; formatos heterogéneos) | Severidad **Alta**: debe incorporar atributos de día hábil / festivo CO para reglas de meta (`O2`–`O6`) |
| Región | División geográfica comercial | Los tres | **Sí** | **Sí** | Texto (`REGION`, `Región Comercial`, etc.) — no ID | Severidad **Alta**: falta decidir columna oficial en Ventas (vacío V9) |
| Canal (CANAL / CANAL2 / SUB CANAL) | Forma de operación comercial | Ventas, Presupuesto (Gestión vía filtro TMK) | **Sí** (Ventas/Presupuesto) | **Sí** | Texto | Aceptable; normalizar nombres |
| Categoría | Categoría comercial | Ventas, Presupuesto | **Sí** | **Sí** | Texto | Ventas tiene valores extra vs Presupuesto — miembro “No informado”/extensión |
| Jerarquía comercial | Gerente → Jefe → Especialista | Los tres (Registros incompleto) | **Sí** (deseable) | **Sí** | Texto anonimizado; catálogos no 1:1 | Severidad **Media**: Star desnormalizado vs snowflake — pendiente; no bloquear 2.2 |
| Aliado | Socio operativo | Los tres | **Sí** | **Sí** | Texto (`DESCRIP2`/`GV_Desc2`/`ALIADO`) | Homologar nombres de campo |
| Marca | Marca del equipo | Solo Ventas | No | **Sí** | Texto | Aceptable |
| Campaña | Campaña TMK | Solo Gestión | No | **Sí** | Texto (`NOMBRE_CAMPAÑA`) | Aceptable |
| Segmento | Segmento de gestión | Solo Gestión | No | **Sí** | Texto sucio | Severidad **Media**: requiere normalización (`Adicionales_`/`adicionales`) |
| Tipo de contacto (+ detalle) | Tipificación | Solo Gestión | No | **Sí** | Texto | Puede ser una dim o dim+atributo; evitar duplicar dims |
| Vendedor | Ejecutor de la venta | Solo Ventas | No | **Sí** | `Cédula Vendedor` (PII; valor `-`) | Severidad **Media**: política PII; no es clave natural limpia |

### Dimensiones / objetos ausentes en el borrador (recomendados)

| Faltante | Severidad | Justificación |
|----------|-----------|---------------|
| Atributo/dim degenerada de **validez de venta** (factura presente, nota crédito) | **Alta** | KPI Reto 1 depende filtro oficial |
| **Unidad de gestión** (explícita) | **Media** | Forma parte del grano aprobado de Presupuesto |
| **Cliente** (`Identificación`) | **Baja** | No es KPI obligatorio del PDF; opcional; PII |
| Calendario laboral / festivos (si no va dentro de Tiempo) | **Alta** | Reglas O2–O6 |

### Observaciones transversales de dimensiones

| ID | Severidad | Hallazgo |
|----|-----------|----------|
| D-01 | **Alta** | El borrador no declara explícitamente **surrogate keys** pese a `02A` (sin claves naturales) |
| D-02 | **Media** | No marca formalmente qué dims son conformadas vs privadas |
| D-03 | **Media** | Riesgo de dimensiones duplicadas si se separan CANAL/CANAL2/SUB CANAL en tablas innecesarias sin necesidad analítica — preferir una dim Canal desnormalizada (Star) salvo justificación |
| D-04 | **Baja** | SCD no definido — aplazable a 2.3 |

---

## 4. Validación de relaciones

| Criterio | Resultado | Severidad si falla |
|----------|-----------|--------------------|
| ¿M:N innecesarias? | El borrador **no define** relaciones físicas aún; a nivel conceptual hechos→dims es N:1. No se observan bridges M:N propuestos | — |
| ¿Dimensiones duplicadas? | Riesgo potencial Canal vs Subcanal vs Categoría solapados; jerarquía vs dims separadas gerente/jefe/especialista | Media (D-03) |
| ¿Hechos mezclando procesos? | **No** — tres hechos / tres procesos | OK |
| ¿Respeto al grano declarado? | Texto del borrador **desactualizado** en Ventas y Gestión | Alta (H-V1, H-G1) |
| ¿Consistencia con Star Schema? | Dirección Star correcta; alternativa Snowflake solo mencionada para jerarquía — aceptable como pendiente de 2.3 | Baja/Media |
| ¿Relación Ventas–Presupuesto? | Correctamente vía dims conformadas (no FK transaccional) — alineado a `01_Proceso_Negocio` | OK |
| ¿Relación Registros–Ventas? | No forzada en el borrador — correcto (relación indirecta) | OK |

**Observación R-01 (Alta):** al actualizar el modelo en 2.3, cada hecho debe listar FKs lógicas solo hacia dimensiones de su grano; Presupuesto no debe apuntar a Marca/Campaña/TipoContacto; Gestión no debe depender de Marca/Vendedor.

**Observación R-02 (Media):** comparar Ventas vs Presupuesto solo en miembros conformados comunes; documentar miembros huérfanos (`REGIONAL`, `SIN_REGION`, etc.).

---

## 5. Validación respecto al proceso de negocio

| Requisito de negocio (`01`) | ¿Cubierto por el borrador? |
|-----------------------------|----------------------------|
| 3 procesos distintos | ✔ Tres hechos |
| Cumplimiento ventas vs presupuesto | ✔ Hechos Ventas + Presupuesto + dims compartidas |
| Eficiencia TMK Outbound | ✔ Hecho Gestión + campaña/segmento/tipificación |
| Actores jerarquía / aliado / región | ✔ Dims propuestas |
| Meta diaria / déficit | ⚠ Parcial — falta modelar calendario hábil en Tiempo |
| Filtro ventas válidas | ⚠ Parcial — no explícito en el borrador |

**Observación P-01 (Alta):** completar cobertura de reglas oficiales de meta y de ventas válidas en el documento dimensional (sin implementar aún).

---

## 6. Validación respecto al grano

| Hecho | Grano en borrador | Grano aprobado | ¿Coincide? |
|-------|-------------------|----------------|------------|
| Ventas | Evento/línea “por confirmar” | 1 fila = 1 evento transaccional | Dirección ✔ / Formalización ✖ |
| Presupuesto | Cruce mes×región×canal×… | Cruce 11 atributos mensuales | ✔ Casi |
| Gestión | “Por confirmar / posible agregado” | 1 fila = agregado tipificado | Dirección ✔ / Formalización ✖ |

**Observación G-01 (Alta):** el borrador debe reemplazar todo lenguaje “por confirmar” por los granos de `02_Declaracion_Grano.md`.

---

## 7. Validación respecto a las claves

| Fuente | Hallazgo `02A` | ¿Lo refleja el borrador? |
|--------|----------------|--------------------------|
| Ventas | Sin clave natural; `Código Factura` descartada | **No** — no menciona surrogate ni descarta factura como PK |
| Presupuesto | Clave compuesta casi única; 5 excepciones | **Parcial** — no documenta excepciones ni surrogate |
| Registros | Sin clave natural; agregado | **No** — grano aún “por confirmar” |

**Observación K-01 (Alta):** en 2.3, declarar política: **todas las tablas de hechos y dimensiones usan surrogate key**; atributos de negocio (factura, textos) son descriptivos/degenerados.

**Observación K-02 (Media):** resolver regla de negocio de los 5 cruces de Presupuesto antes del modelo definitivo.

---

## 8. Riesgos encontrados

| ID | Severidad | Riesgo |
|----|-----------|--------|
| RK1 | Alta | Congelar el borrador actual sin actualizar granos → modelo inconsistente con documentación aprobada |
| RK2 | Alta | Usar `Código Factura` como llave → sobre/subconteo de ventas y cumplimiento |
| RK3 | Alta | Modelar Gestión a grano de contacto → KPIs Reto 2 incorrectos |
| RK4 | Media | No modelar calendario hábil → imposible cumplir lógica de meta diaria/déficit |
| RK5 | Media | No decidir columna oficial de región en Ventas → cumplimiento regional inconsistente |
| RK6 | Media | Fórmulas % gestión/contactabilidad indefinidas en PDF → ambigüedad de métricas derivadas |
| RK7 | Baja | PII (cliente/vendedor) si se publican dims sin política |

---

## 9. Recomendaciones de mejora (para Subfase 2.3)

1. **Actualizar** `03_Modelo_Dimensional.md` (solo tras OK de esta revisión) con:
   - Granos aprobados literales.
   - Surrogate keys obligatorias.
   - Matriz de bus (procesos × dimensiones conformadas).
   - Diagrama Star de tres hechos.
   - Tratamiento de ventas válidas y calendario laboral.
2. **Cerrar** con PO/Tech Lead: regla de 5 cruces Presupuesto; columna región Ventas; fórmulas % Reto 2.
3. **Mantener** Star Schema como opción preferida; justificar Snowflake solo si la jerarquía lo exige por mantenimiento — no por defecto.
4. **No** crear hecho único de “desempeño” que mezcle venta y presupuesto.
5. **No** iniciar modelo físico (`04`) hasta 2.3 aprobado.

---

## 10. Conclusión del Tech Review

### Concepto

# ✔ APROBADO CON AJUSTES

### Fundamento

- La arquitectura de **tres hechos / tres procesos**, dimensiones conformadas y orientación **Star Schema** es **consistente** con `01_Proceso_Negocio`, el enunciado y las buenas prácticas del proyecto.
- El borrador **no requiere rediseño total**.
- Sí requiere **ajustes obligatorios** (severidad Alta) para alinearse a la Declaración del Grano y a la Auditoría de Claves ya aprobadas, y para cubrir reglas oficiales de validez de venta y calendario de metas.

### Condición para pasar a Subfase 2.3

El Tech Lead y el Project Owner aceptan este concepto **APROBADO CON AJUSTES**.  
Solo entonces se autorizará la actualización de `docs/modelo/03_Modelo_Dimensional.md` incorporando los ajustes H-V1/2, H-P1, H-G1/2, D-01, G-01, K-01 y P-01.

### Estado de `03_Modelo_Dimensional.md` tras esta sesión

**Sin cambios.** Permanece como BORRADOR (No aprobado) hasta la actualización autorizada en 2.3.
