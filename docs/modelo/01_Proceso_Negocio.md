# 01 — Proceso de Negocio

Fase: **2 — Diseño del Data Warehouse**  
Subfase: **2.1 — Comprensión del proceso de negocio**  
Fecha: 2026-07-26  
Insumos: `docs/analisis/01_Perfilado_Datos.md`, `02_Reglas_Negocio.md`, `03_Requisitos_Funcionales.md`, `Prueba_Tecnica.pdf`

> Este documento describe el **negocio**.  
> No describe la solución técnica ni el diseño del almacén de datos.

---

## 1. Objetivo del negocio

La operación comercial se centra en vender productos y servicios a través de canales telefónicos (telemarketing) y digitales (e-commerce / tienda virtual), con apoyo de **aliados** y una jerarquía comercial (gerente → jefe → especialista).

El negocio necesita:

- Cumplir **metas comerciales** mensuales.
- Medir el **desempeño real de ventas** frente a esas metas.
- Evaluar la **eficiencia operativa** de la gestión de contactos en el canal TMK Outbound.

---

## 2. Objetivo analítico de la solución

Permitir al **Director Comercial** (y a la cadena de mando) responder de forma ejecutiva:

1. Cómo van las **ventas válidas** frente al **presupuesto**, por región, aliado, gerente, jefe y especialista.
2. Cómo se comporta la **gestión de registros** entregados a aliados TMK Outbound, por segmento, campaña y aliado (volumen entregado, gestión, contactabilidad y calidad del contacto).

La solución analítica debe soportar alertas, focos de gestión y lectura accionable, aplicando las reglas oficiales de ventas válidas y de cálculo/cumplimiento de metas.

---

## 3. Actores del negocio

| Actor | Rol en el negocio |
|-------|-------------------|
| **Director Comercial** | Consume tableros; decide focos de gestión y priorización |
| **Gerente de área** | Responsable de resultados en su ámbito; aparece en la jerarquía comercial |
| **Jefe de canal / regional** | Supervisa especialistas; sujeto de seguimiento de cumplimiento |
| **Especialista** | Nivel operativo de la jerarquía comercial; sujeto de cumplimiento |
| **Aliado** | Socio operativo que ejecuta ventas y/o gestión de contactos |
| **Vendedor** | Persona que concreta la venta (identificado en el detalle comercial) |
| **Cliente** | Persona o cuenta que compra (identificado en la transacción) |
| **Operación de campañas (TMK Outbound)** | Asigna y gestiona registros de contacto sobre campañas y segmentos |

---

## 4. Procesos de negocio identificados

Tras contrastar el enunciado, las reglas oficiales y el comportamiento de las fuentes, se identifican **tres procesos de negocio distintos**:

### Proceso A — Venta comercial (cierre)

Registro del resultado comercial cuando una reserva/venta se concreta: fecha, región, canal, jerarquía, aliado, marca, valor y atributos de facturación/nota crédito.

- Horizonte de interés analítico: últimos **seis meses**.
- Solo ciertas ventas cuentan para el desempeño oficial (ver eventos y reglas).

### Proceso B — Planeación y seguimiento de metas (presupuesto)

Definición de metas comerciales mensuales segmentadas por canal, subcanal, región, categoría, jerarquía comercial y aliado, con medidas de meta (terminales, tecnología y total T&T observado en la operación).

- Horizonte: últimos **seis meses**.
- La meta mensual se descompone a **meta diaria** con reglas de días hábiles y acumulación de déficit.

### Proceso C — Gestión de registros TMK Outbound

Asignación y tipificación de registros de contacto entregados a aliados del canal TMK Outbound: campaña, segmento, tipo de contacto, intentos y volumen gestionado.

- Horizonte: últimos **tres meses**.
- Objetivo: medir eficiencia operativa (gestión y contactabilidad), no el cierre de venta en sí.

Estos tres procesos **comparten actores y atributos de negocio** (región, aliado, jerarquía, tiempo), pero **no son el mismo proceso**: ocurren en momentos distintos, con reglas distintas y preguntas distintas.

---

## 5. Flujo del negocio (desde la generación del dato hasta el análisis)

```
Planeación comercial
        │
        ▼
Asignación de metas mensuales
(región / canal / jerarquía / aliado)
        │
        ├──────────────────────────────┐
        ▼                              ▼
Operación de ventas              Operación TMK Outbound
(canales telefónico / digital)   (campañas y registros)
        │                              │
        ▼                              ▼
Registro de la venta             Tipificación del contacto
(factura, valor, marca…)         (efectivo / no efectivo / no contacto)
        │                              │
        └──────────────┬───────────────┘
                       ▼
        Consolidación para seguimiento ejecutivo
                       │
                       ▼
     Análisis: cumplimiento vs meta + eficiencia de gestión
```

En la práctica operativa actual, esos resultados llegan consolidados en tres conjuntos de información de negocio (ventas, presupuesto y registros), que el área comercial usa para el tablero ejecutivo.

---

## 6. Eventos de negocio

| Proceso | Evento | Qué representa |
|---------|--------|----------------|
| A — Venta | **Venta registrada** | Se registra una transacción comercial con fecha, valor y atributos comerciales |
| A — Venta | **Facturación asociada** | La venta tiene (o no) código de factura |
| A — Venta | **Nota crédito** | Se marca que la venta no debe contarse como válida para el desempeño |
| B — Metas | **Asignación de meta mensual** | Se fija la meta del mes para un cruce comercial |
| B — Metas | **Evaluación diaria de cumplimiento** | Se compara avance vs meta diaria; puede acumular déficit o no aplicar excedente |
| C — TMK | **Entrega / carga de registros** | Se asignan registros a aliados/campañas |
| C — TMK | **Gestión / intento de contacto** | Se tipifica el resultado del contacto |

---

## 7. Objetos de negocio

| Objeto | Descripción |
|--------|-------------|
| **Venta** | Resultado comercial con valor y atributos de canal, región, jerarquía, aliado y producto/marca |
| **Meta / presupuesto** | Objetivo monetario mensual asignado a un cruce comercial |
| **Registro de gestión** | Unidad de trabajo de contacto en campañas TMK Outbound |
| **Región** | División geográfica comercial |
| **Canal / subcanal / categoría** | Forma de operación comercial (telefónico, digital, etc.) |
| **Aliado** | Socio que ejecuta venta o gestión |
| **Gerente / Jefe / Especialista** | Niveles de la jerarquía comercial |
| **Campaña** | Iniciativa de contacto con nombre de negocio |
| **Segmento** | Clasificación del tipo de gestión (migración, portabilidad, etc.) |
| **Tipo de contacto** | Resultado de la gestión (efectivo, no efectivo, no contacto) |
| **Cliente** | Comprador asociado a la venta |
| **Vendedor** | Ejecutor de la venta |
| **Marca** | Marca del equipo/producto vendido |
| **Calendario laboral** | Días hábiles (lun–sáb) y festivos nacionales de Colombia |

---

## 8. Relación funcional entre Ventas, Presupuesto y Registros

| Relación | Naturaleza |
|----------|------------|
| **Ventas ↔ Presupuesto** | Relación de **cumplimiento**: lo vendido (válido) se compara con la meta. Comparten región, canal, jerarquía y aliado. No es la misma operación: una es resultado; la otra es objetivo. |
| **Registros ↔ Ventas** | Relación **indirecta / operativa**: la gestión TMK busca contactar y eventualmente vender, pero el archivo de registros mide contactabilidad y tipificación, no el cierre facturado. No hay vínculo transaccional directo observado entre un contacto y una factura. |
| **Registros ↔ Presupuesto** | Relación **débil**: pueden compartir región/aliado/jerarquía en algunos casos, pero el Reto 2 no exige comparar registros vs meta; exige eficiencia de gestión. |
| **Los tres juntos** | Se articulan en el mismo **universo comercial** (misma organización y geografía), pero responden a **preguntas de negocio distintas**. |

Conclusión funcional: Ventas y Presupuesto alimentan el **seguimiento de desempeño comercial**; Registros alimenta el **seguimiento de eficiencia TMK Outbound**.

---

## 9. Preguntas que el negocio desea responder

### Desempeño comercial

- ¿Cómo van las ventas frente al presupuesto?
- ¿Qué región presenta el mejor desempeño?
- ¿Qué aliado está sobrecumpliendo o incumpliendo?
- ¿Qué especialista está sobrecumpliendo o incumpliendo?
- ¿Qué jefe está sobrecumpliendo o incumpliendo?

### Gestión TMK Outbound

- ¿Cuántos registros se entregaron por segmento, campaña y aliado?
- ¿Cuál es el % de gestión?
- ¿Cuál es el % de contactabilidad?
- ¿Cuál es el % de contactos efectivos y no efectivos?
- ¿Cuáles son el Top 5 de aliados con mejor contactabilidad?
- ¿Qué campañas tienen mejor contactabilidad?
- ¿Qué campañas tienen más / menos registros asignados?

---

## 10. KPIs que soportan esas preguntas

### Bloque desempeño comercial

| KPI | Pregunta que soporta |
|-----|----------------------|
| Ventas válidas vs presupuesto | Cumplimiento comercial |
| Desempeño por región | Mejor / peor región |
| Cumplimiento por aliado | Sobrecumplimiento / incumplimiento de aliados |
| Cumplimiento por especialista | Sobrecumplimiento / incumplimiento de especialistas |
| Cumplimiento por jefe | Sobrecumplimiento / incumplimiento de jefes |
| Meta diaria / déficit acumulado / avance dinámico | Lectura diaria del cumplimiento (regla oficial de metas) |

**Filtro oficial de ventas válidas:** tienen código de factura y no presentan nota crédito.

### Bloque gestión TMK Outbound

| KPI | Pregunta que soporta |
|-----|----------------------|
| Cantidad de registros entregados | Volumen asignado |
| % Gestión | Intensidad / cobertura de gestión |
| % Contactabilidad | Capacidad de contactar |
| % Contactos efectivos | Calidad positiva del contacto |
| % Contactos no efectivos | Contactos sin resultado efectivo |
| Ranking de aliados y campañas | Priorización operativa |

> Nota: las fórmulas exactas de los porcentajes de gestión/contactabilidad no están definidas en el enunciado; deberán formalizarse en subfases posteriores sin contradecir el PDF.

---

## 11. Conclusiones

1. El escenario comercial no es un único proceso monolítico: conviven **venta**, **meta** y **gestión de contactos**.
2. El Director Comercial necesita dos lecturas analíticas: **cumplimiento comercial** y **eficiencia TMK Outbound**.
3. Ventas y Presupuesto se relacionan por comparación de cumplimiento; Registros aporta un proceso operativo distinto.
4. Las reglas oficiales de validez de venta y de cálculo de meta diaria condicionan cualquier análisis de desempeño.
5. Existen vacíos de definición (fórmulas de %, nivel exacto de la meta diaria, etc.) que el negocio deberá cerrar antes del diseño definitivo, pero **no cambian el número de procesos**.

### Respuesta clave de la Subfase 2.1

**¿Cuántos procesos de negocio existen realmente?**

**Tres (3):**

1. **Venta comercial (cierre)**  
2. **Planeación y seguimiento de metas (presupuesto)**  
3. **Gestión de registros TMK Outbound**

Cualquier diseño posterior del almacén de datos deberá respetar esta separación de procesos y no forzarlos en un único proceso artificial.
