# 03 — Requisitos Funcionales

Fase: **Análisis**  
Fecha: 2026-07-25  
Fuente oficial: `Prueba_Tecnica.pdf`  
Ubicación del PDF: `C:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica\Prueba_Tecnica.pdf`

> Este documento traduce el enunciado oficial a requisitos funcionales.
> Contiene **únicamente** información respaldada por el PDF.
> No incluye soluciones técnicas, arquitectura, tablas ni modelo dimensional.

Convención de este documento:

- **Requisito oficial:** texto o implicación directa del PDF.
- **Vacío del PDF:** aspecto no definido explícitamente en el enunciado.
- **Supuesto:** no se incluyen supuestos de implementación en este documento (salvo que se etiqueten explícitamente como tal; por defecto no se usan).

---

## 1. Objetivo del proyecto

**Requisito oficial**

Diseñar e implementar una base de datos local que sirva como fuente de información para un tablero de control en Power BI, midiendo habilidades en:

- Gestión y modelado de datos.
- Procesos ETL.
- Visualización en Power BI bajo un escenario de negocio.

Para ello el candidato debe:

- Cargar y estructurar la información suministrada.
- Realizar las transformaciones y depuraciones necesarias.
- Diseñar un modelo dimensional optimizado para análisis.
- Implementar las reglas de negocio requeridas.
- Construir un tablero ejecutivo en Power BI que permita responder los retos planteados.

El modelo de datos implementado en Power BI deberá reflejar correctamente la estructura dimensional creada en la base de datos.

---

## 2. Alcance

### 2.1 Información suministrada (requisito oficial)

| Archivo | Contenido según PDF |
|---------|---------------------|
| `Ventas.xlsb` | Detalle transaccional de ventas de los **últimos seis meses** (fecha, región, marca, vendedor, valor de venta, cantidad y demás atributos relevantes). *Descripción del enunciado PDF — **análisis histórico realizado durante el diseño. No corresponde al comportamiento final implementado** (el ETL no filtra por horizonte).* |
| `Presupuesto.xlsb` | Metas comerciales de los **últimos seis meses**, segmentadas por canal, subcanal, región, categoría, especialista, jefe, gerente, aliado y demás atributos. *Descripción del enunciado PDF — **análisis histórico realizado durante el diseño. No corresponde al comportamiento final implementado** (el ETL no filtra por horizonte).* |
| `Registros.xlsb` | Registros asignados a los aliados del canal **TMK Outbound** durante los **últimos tres meses** (campaña, segmento, tipo de contacto, región y demás atributos de gestión) |

### 2.2 Alcance funcional (requisito oficial)

- Base de datos local como fuente del tablero.
- Transformaciones y depuraciones de las fuentes.
- Modelo dimensional (el PDF exige evaluar Star Schema vs Snowflake Schema y justificar).
- Reglas de negocio de metas y de ventas válidas.
- Dos retos de visualización en Power BI (desempeño comercial y gestión TMK Outbound).
- Documentación explicativa.

### 2.3 Fuera de alcance explícito del PDF

El PDF no define stack tecnológico obligatorio (motor de BD, orquestador, lenguaje). Esas decisiones pertenecen a la arquitectura del proyecto (fuera de este documento de requisitos).

---

## 3. KPIs obligatorios

### 3.1 Reto 1 — Desempeño comercial (requisito oficial)

El tablero debe permitir monitorear ventas a nivel de **Región, Aliado, Gerente, Jefe y Especialista**, y responder como mínimo:

| ID | Pregunta / indicador |
|----|----------------------|
| KPI-C1 | ¿Cómo van las ventas frente al presupuesto? |
| KPI-C2 | ¿Qué región presenta el mejor desempeño? |
| KPI-C3 | ¿Qué aliado está sobrecumpliendo o incumpliendo? |
| KPI-C4 | ¿Qué especialista está sobrecumpliendo o incumpliendo? |
| KPI-C5 | ¿Qué jefe está sobrecumpliendo o incumpliendo? |

Se espera lectura ejecutiva, clara y accionable (oportunidades, alertas, focos de gestión).

### 3.2 Reto 2 — Gestión de registros TMK Outbound (requisito oficial)

Identificar, por **segmento, campaña y aliado**:

| ID | Indicador |
|----|-----------|
| KPI-G1 | Cantidad de registros entregados |
| KPI-G2 | % Gestión |
| KPI-G3 | % Contactabilidad |
| KPI-G4 | % Contactos efectivos |
| KPI-G5 | % Contactos no efectivos |

Preguntas mínimas del tablero:

| ID | Pregunta |
|----|----------|
| KPI-G6 | ¿Cuál es el Top 5 de aliados con mejor contactabilidad? |
| KPI-G7 | ¿Cuál o cuáles campañas presentan mejor contactabilidad? |
| KPI-G8 | ¿Cuáles campañas tienen mayor cantidad de registros asignados? |
| KPI-G9 | ¿Cuáles campañas tienen menor cantidad de registros asignados? |

---

## 4. Reglas oficiales del negocio (extraídas del PDF)

### 4.1 Ventas válidas (requisito oficial)

Para el análisis del Reto 1, **únicamente** se consideran ventas válidas las que cumplan **ambas** condiciones:

1. Tienen código de factura.
2. No presentan nota crédito.

### 4.2 Cálculo de metas (requisito oficial)

- Los días hábiles corresponden a **lunes a sábado**.
- Deben excluirse **domingos** y **festivos nacionales de Colombia**.
- La **meta diaria** debe calcularse a partir de la **meta mensual** y los **días hábiles del mes**.

### 4.3 Lógica de cumplimiento (requisito oficial)

- Si no se alcanza la meta diaria, el **déficit debe acumularse** para el siguiente día hábil.
- Si se supera la meta diaria, el **excedente no debe descontarse** de la meta del día siguiente.
- La meta deberá **recalcularse dinámicamente** considerando el avance y los días hábiles restantes.

### 4.4 Alcance del Reto 2 (requisito oficial)

El seguimiento de gestión aplica a registros entregados al canal **TMK Outbound**.

---

## 5. Entregables oficiales solicitados

**Requisito oficial**

1. Scripts de creación y transformación de datos.
2. Archivo Power BI (`.pbix`).
3. Documento de explicación, que debe incluir:
   - Diseño del modelo de datos.
   - Depuraciones o transformaciones realizadas.
   - Novedades identificadas en la información.
   - Justificación del modelo implementado.
   - Principales cálculos DAX utilizados.
   - Uso de herramientas de IA (si aplica), incluyendo los prompts utilizados.

**Fecha límite oficial:** martes 28 de julio de 2026, 6:00 pm.

---

## 6. Restricciones identificadas

**Requisito oficial / derivadas del PDF**

| ID | Restricción |
|----|-------------|
| R1 | Power BI debe reflejar la estructura dimensional de la base de datos. |
| R2 | Debe evaluarse y justificarse Star Schema vs Snowflake Schema. |
| R3 | Ventas del Reto 1 filtradas por regla de validez (factura + sin nota crédito). |
| R4 | Metas diarias sujetas a calendario laboral Colombia (lun–sáb, sin festivos). |
| R5 | Déficit se acumula; excedente no se descuenta del día siguiente. |
| R6 | Reto 2 limitado al canal TMK Outbound. |
| R7 | Horizontes temporales del enunciado: Ventas/Presupuesto 6 meses; Registros 3 meses. **Análisis histórico realizado durante el diseño. No corresponde al comportamiento final implementado.** |
| R8 | Entrega con fecha y hora límite definidas. |

---

## 7. Criterios de aceptación derivados del PDF

La solución será aceptable respecto al enunciado si:

1. Existe una base de datos local alimentada con las tres fuentes.
2. Se aplicaron transformaciones/depuraciones documentadas.
3. Existe un modelo dimensional justificado (estrella o copo de nieve).
4. Están implementadas las reglas de ventas válidas y de metas/cumplimiento.
5. El `.pbix` responde las preguntas mínimas del Reto 1 y del Reto 2.
6. Se entregan los tres artefactos oficiales (scripts, `.pbix`, documento).
7. El documento cubre los puntos de documentación esperada listados en el PDF.
8. La entrega se realiza antes de la fecha límite.

---

## 8. Preguntas o vacíos que el PDF no responde explícitamente

| ID | Vacío |
|----|-------|
| V1 | Fórmulas exactas de `% Gestión`, `% Contactabilidad`, `% Contactos efectivos` y `% Contactos no efectivos` (numerador/denominador). |
| V2 | Definición operativa de “registros entregados” vs filas de `Registros.xlsb` (¿suma de `CANTIDAD`? ¿conteo de filas?). |
| V3 | Qué medida de presupuesto usar frente a ventas (`TERMINALES`, `TECNOLOGIA`, `T&T` u otra). |
| V4 | Cómo se compone exactamente el “recalculo dinámico” de la meta junto con la acumulación de déficit (orden de operaciones / fórmula). |
| V5 | Fuente oficial del calendario de festivos de Colombia a utilizar. |
| V6 | Si el estado de la reserva (`Tramitada`, `Activated`, etc.) interviene además de factura y nota crédito. |
| V7 | Grano oficial de la venta cuando hay códigos de factura duplicados. |
| V8 | Tratamiento de filas de presupuesto dimensionalmente duplicadas. |
| V9 | Cuál columna de región es la oficial cuando existen varias en Ventas. |
| V10 | Nivel exacto al que se aplica la meta diaria (¿aliado? ¿especialista? ¿región? ¿todas las jerarquías?). |
| V11 | Si “cantidad” mencionada para Ventas en el PDF corresponde a un campo específico de la fuente (el enunciado la menciona; la identificación del campo queda para el análisis de datos). |
| V12 | Stack tecnológico obligatorio (motor BD, lenguaje ETL, orquestación). |

Estos vacíos **no** son requisitos inventados; deben resolverse en fases posteriores con decisión documentada del PO/Tech Lead o con definición explícita en el diseño, sin contradecir el PDF.

---

## 9. Trazabilidad

- Evidencia de datos → `01_Perfilado_Datos.md`
- Reglas observadas + reglas oficiales confirmadas → `02_Reglas_Negocio.md`
- Diseño dimensional → Fase 2 (`docs/modelo/03_Modelo_Dimensional.md`) — **no iniciado por este documento**
