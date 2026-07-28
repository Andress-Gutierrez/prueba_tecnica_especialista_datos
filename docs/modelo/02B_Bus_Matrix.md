# 02B — Bus Matrix del Data Warehouse

Fase: **2 — Diseño del Data Warehouse**  
Subfase: **2.2.1 — Bus Matrix**  
Fecha: 2026-07-26

### Documentos de referencia (únicamente)

- `docs/modelo/01_Proceso_Negocio.md`
- `docs/modelo/02_Declaracion_Grano.md`
- `docs/modelo/02A_Analisis_Claves.md`
- `docs/modelo/03A_Revision_Arquitectonica.md`
- `docs/analisis/01_Perfilado_Datos.md`
- `docs/analisis/02_Reglas_Negocio.md`
- Enunciado oficial (`Prueba_Tecnica.pdf` / `03_Requisitos_Funcionales.md`)

> Esta matriz no es el modelo estrella definitivo.  
> Es el puente entre procesos aprobados y el Modelo Dimensional Definitivo (Subfase 2.3).

---

## 1. Procesos de negocio aprobados

| # | Nombre | Descripción | Grano aprobado |
|---|--------|-------------|----------------|
| A | **Venta comercial (cierre)** | Registro del resultado comercial cuando se concreta una venta/reserva (valor, canal, jerarquía, aliado, marca, factura/nota crédito) | **1 fila = 1 evento / registro transaccional de venta** (`Ventas.xlsb`). No es 1 factura. |
| B | **Planeación y seguimiento de metas (presupuesto)** | Asignación de meta mensual por cruce comercial (región, canal, categoría, jerarquía, aliado, etc.) | **1 fila = 1 asignación de meta mensual** al cruce `MES + REGION + CANAL + CANAL2 + SUB CANAL + CATEGORIA + UNIDAD DE GESTION + ESPECIALISTA + JEFE + GERENTE + DESCRIP2` |
| C | **Gestión de registros TMK Outbound** | Agregados de tipificación/contactabilidad de registros entregados a aliados TMK Outbound | **1 fila = 1 agregado tipificado de gestión** (`CANTIDAD` + `INTENTOS`) por cruce campaña/periodo/fecha/tipificación/aliado/región/segmento (y atributos de carga/jerarquía cuando existen) |

**Justificación:** los tres procesos fueron declarados en `01_Proceso_Negocio.md` y sus granos en `02_Declaracion_Grano.md` (claves validadas en `02A`).

---

## 2. Dimensiones candidatas

| Dimensión | Qué describe | Fuente(s) de origen | Posible clave natural | ¿Surrogate Key? | Observaciones |
|-----------|--------------|---------------------|----------------------|-----------------|---------------|
| **Tiempo** | Día / mes / año; soporte a meta diaria | Ventas (`Fecha Venta`, AÑO/MES/DIA), Presupuesto (`MES`), Registros (`FECHA_GESTION`, `PERIODO`, `FECHA_CARGUE`) | Fechas/periodos en origen (formatos heterogéneos) | **Sí** | Debe incluir atributos de **día hábil** y festivos CO (reglas O2–O6). Conformada. |
| **Región** | División geográfica comercial | Ventas (`Región Comercial`, `GV-Division`, `D_Division`), Presupuesto (`REGION`), Registros (`DIVISION_COMERCIAL`, `AREA_COMERCIAL`) | Texto de región (sin ID) | **Sí** | **Pendiente:** columna oficial en Ventas (vacío V9). Miembros huérfanos: `REGIONAL`, `SIN_REGION`. |
| **Canal** | CANAL / CANAL2 / SUB CANAL | Ventas, Presupuesto | Texto | **Sí** | Preferir **una** dimensión desnormalizada (Star), no tres tablas. Gestión se filtra a TMK Outbound. |
| **Categoría** | Categoría comercial | Ventas, Presupuesto | Texto | **Sí** | Ventas tiene valores extra vs Presupuesto. |
| **Unidad de gestión** | Unidad operativa del presupuesto | Presupuesto (`UNIDAD DE GESTION`) | Texto | **Sí** | Parte del grano aprobado de Presupuesto; en Ventas no aparece como columna homónima. |
| **Jerarquía comercial** | Gerente → Jefe → Especialista | Ventas (`GV-*`), Presupuesto, Registros (`gerente`/`jefe`/`Especialista`, muy nulos) | Textos anonimizados | **Sí** | Catálogos no 1:1 entre fuentes. Star desnormalizado preferido (`03A`). |
| **Aliado** | Socio operativo | Ventas (`GV_Desc2`), Presupuesto (`DESCRIP2`), Registros (`ALIADO`) | Texto | **Sí** | Homologar nombres de campo; dimensión conformada clave para Retos 1 y 2. |
| **Marca** | Marca del equipo/producto | Solo Ventas | Texto | **Sí** | Exclusiva de Venta. |
| **Vendedor** | Ejecutor de la venta | Solo Ventas (`Cédula Vendedor`) | Cédula (PII; valor `-`) | **Sí** | No es clave natural limpia; política PII pendiente. |
| **Campaña** | Campaña TMK | Solo Registros (`NOMBRE_CAMPAÑA`) | Texto | **Sí** | Exclusiva de Gestión. |
| **Segmento** | Segmento de gestión | Solo Registros (`SEGMENTO`) | Texto (sucio) | **Sí** | Requiere normalización (`Adicionales_` / `adicionales`). |
| **Tipo de contacto** | Tipificación (`TIPO_CONTACTO` + `DETALLE1`) | Solo Registros | Texto | **Sí** | Puede ser una dim con atributos de detalle; evita dims duplicadas. |
| **Validez de venta** *(atributo / dim degenerada)* | Factura presente + sin nota crédito | Solo Ventas | Flags / código factura (no PK) | **Sí** (si se materializa como dim) o degenerada en hecho | Obligatoria para KPIs Reto 1 (regla O1). `Código Factura` **no** es clave natural (`02A`). |

---

## 3. Bus Matrix

Leyenda:

- **X** = la dimensión participa en el proceso  
- **C** = dimensión **conformada** (compartida entre ≥2 procesos)  
- **E** = dimensión **exclusiva** de un proceso  
- **P** = **pendiente de validación** (decisión de negocio/técnica abierta)

### 3.1 Matriz procesos × dimensiones

| Dimensión \ Proceso | A — Venta | B — Presupuesto | C — Gestión TMK | Clasificación | Justificación |
|---------------------|:---------:|:---------------:|:---------------:|---------------|---------------|
| Tiempo | X | X | X | **C** | Comparación temporal y meta diaria; presente en las tres fuentes |
| Región | X | X | X | **C** (+ **P** columna Ventas) | Cumplimiento y rankings por región; homologación pendiente en Ventas |
| Canal | X | X | X* | **C** | Compartido Venta/Presupuesto; en Gestión aplica filtro TMK Outbound (*) |
| Categoría | X | X | — | **C** | Cruce comercial común Venta–Presupuesto |
| Unidad de gestión | — | X | — | **E** | Solo en grano de Presupuesto |
| Jerarquía comercial | X | X | X | **C** | KPIs por gerente/jefe/especialista; en Registros muy incompleta |
| Aliado | X | X | X | **C** | Actor central Reto 1 y Reto 2 |
| Marca | X | — | — | **E** | Solo Ventas |
| Vendedor | X | — | — | **E** (+ **P** PII) | Solo Ventas; política de publicación pendiente |
| Campaña | — | — | X | **E** | Solo Gestión TMK |
| Segmento | — | — | X | **E** | Solo Gestión TMK |
| Tipo de contacto | — | — | X | **E** | Solo Gestión TMK |
| Validez de venta | X | — | — | **E** (o degenerada) | Solo aplica al proceso de venta / Reto 1 |

\* Gestión no trae CANAL como columna homónima; el alcance TMK Outbound es regla de negocio del enunciado (O8), no un join transaccional a Canal de Ventas.

### 3.2 Resumen de clasificación

| Tipo | Dimensiones |
|------|-------------|
| **Conformadas** | Tiempo, Región, Canal, Categoría, Jerarquía comercial, Aliado |
| **Exclusivas** | Unidad de gestión (Presupuesto); Marca, Vendedor, Validez de venta (Venta); Campaña, Segmento, Tipo de contacto (Gestión) |
| **Pendientes de validación** | Columna oficial de Región en Ventas; política PII de Vendedor/Cliente; regla de los 5 cruces de Presupuesto (afecta carga, no la celda de la matriz); fórmulas % Reto 2 (métricas derivadas, no dims) |

### 3.3 Atributos degenerados en hechos (no son dims compartidas)

| Atributo | Proceso | Motivo |
|----------|---------|--------|
| `Código Factura` | Venta | Atributo descriptivo / validez; **no** SK del evento (`02A`) |
| Flag nota crédito | Venta | Regla O1 |
| `Cuotas` | Venta | Medida/atributo secundario; no KPI obligatorio |

---

## 4. Impacto sobre el Modelo Dimensional

### 4.1 Dimensiones compartidas (conformadas)

Tiempo, Región, Canal, Categoría, Jerarquía comercial y Aliado permiten:

- Comparar **ventas válidas vs presupuesto** en los mismos miembros de negocio (Reto 1).
- Analizar Gestión TMK por región/aliado/jerarquía sin inventar un cuarto proceso.
- Evitar “versiones” distintas de Región/Aliado por hecho (drift semántico).

### 4.2 Dimensiones exclusivas

- **Venta:** Marca, Vendedor, Validez de venta → detalle del cierre comercial sin contaminar Presupuesto/Gestión.  
- **Presupuesto:** Unidad de gestión → respeta el grano mensual aprobado.  
- **Gestión:** Campaña, Segmento, Tipo de contacto → soportan KPIs de contactabilidad sin mezclarlos con facturación.

### 4.3 Beneficios de este diseño

1. Alineación 1:1 con los **3 procesos** aprobados.  
2. Respeto estricto al **grano** aprobado (sin colapsar a factura ni a contacto unitario).  
3. Base clara para **Star Schema** con hechos separados y dims conformadas (`03A`).  
4. Surrogate keys obligatorias donde no hay clave natural (`02A`).  
5. Menor riesgo de hechos “dios” que mezclen venta + meta + tipificación.

### 4.4 Riesgos que se evitan

| Riesgo evitado | Cómo lo evita la Bus Matrix |
|----------------|-----------------------------|
| Usar `Código Factura` como llave | Queda fuera de dims conformadas; solo degenerado |
| 1 fila Gestión = 1 contacto | Grano agregado + dims de tipificación, no ID persona |
| Mezclar procesos en un solo hecho | Tres columnas de proceso en la matriz |
| Comparar venta vs meta en catálogos distintos | Dims conformadas Región/Canal/Aliado/Jerarquía |
| Meta diaria como grano de Presupuesto | Tiempo conformado + cálculo; Presupuesto sigue mensual |

---

## 5. Conclusión

### ¿La Bus Matrix respalda el borrador del modelo dimensional existente?

# **Sí.**

El borrador `03_Modelo_Dimensional.md` ya apuntaba a:

- tres hechos (uno por proceso),
- dimensiones compartidas (tiempo, región, canal, jerarquía, aliado),
- dimensiones exclusivas (marca, campaña, segmento, tipificación, vendedor),
- orientación Star Schema.

La Bus Matrix **confirma** esa dirección y la hace **trazable** a procesos y granos aprobados.

### Ajustes necesarios para convertir el borrador en Modelo Dimensional Definitivo (Subfase 2.3)

1. **Fijar granos literales** aprobados (eliminar “por confirmar”).  
2. Declarar **surrogate keys** en hechos y dimensiones.  
3. Incorporar **Tiempo** con atributos de día hábil / festivos CO.  
4. Explicitar **Validez de venta** (filtro factura + sin nota crédito).  
5. Incluir **Unidad de gestión** en el modelo de Presupuesto.  
6. Formalizar dims **conformadas vs exclusivas** según esta matriz.  
7. Documentar pendientes: región oficial Ventas, 5 cruces Presupuesto, PII, fórmulas % Reto 2.  
8. Elaborar diagrama Star + matriz de bus embebida en `03_Modelo_Dimensional.md` (solo tras OK Tech Lead).

### ¿Listo para construir el Modelo Dimensional Definitivo?

**Condicionalmente sí:** la arquitectura de bus está lista como insumo de la Subfase **2.3**, siempre que el Tech Lead / PO aprueben esta Bus Matrix y el concepto previo **APROBADO CON AJUSTES** (`03A`).

**No** se modifica aún `03_Modelo_Dimensional.md` ni `04_Modelo_Fisico.md` en esta sesión.
