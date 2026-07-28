# 01 — Perfilado de Datos

Fase: **Análisis**  
Fecha: 2026-07-25  
Fuentes: `data/raw/Presupuesto.xlsb`, `data/raw/Ventas.xlsb`, `data/raw/Registros.xlsb`  
Herramientas: Python + `pandas` + `pyxlsb`  
Scripts de apoyo: `scripts/profile_raw_xlsb.py`, `scripts/analyze_key_overlap.py`, `scripts/summarize_profile.py`

> Alcance de este documento: hechos observados en las fuentes (estructura, calidad, claves, relaciones).
> Las hipótesis de modelado se documentan por separado en `docs/modelo/`.

---

## 1. Inventario de fuentes

| Archivo | Tamaño | Hoja | Filas | Columnas | Filas duplicadas exactas |
|---------|--------|------|------:|---------:|-------------------------:|
| `Presupuesto.xlsb` | ~33 KB | `Presupuesto` | 731 | 14 | 0 |
| `Ventas.xlsb` | ~10.3 MB | `Ventas` | 243 414 | 24 | 55 |
| `Registros.xlsb` | ~16.3 MB | `Registros` | 459 592 | 16 | 25 |

Cada archivo contiene **una sola hoja** con el mismo nombre del dominio.

---

## 2. Perfilado por fuente

### 2.1 Presupuesto (731 × 14)

| Columna | Tipo observado | Nulos % | Únicos | Observaciones |
|---------|----------------|--------:|-------:|---------------|
| MES | int (YYYYMM) | 0 | 6 | Rango 202601–202606 |
| REGION | texto | 0 | 5 | 5 regiones |
| CANAL | texto | 0 | 2 | TELEFONICO VENTA, DIGITAL |
| CANAL2 | texto | 0 | 4 | TMK OUT/IN BOUND, ECOMMERCE (NO) ASISTIDO |
| SUB CANAL | texto | 0 | 5 | Incluye WHATSAPP, TIENDA VIRTUAL |
| CATEGORIA | texto | 0 | 4 | MASIVO, WHATSAPP, TIENDA VIRTUAL, WEB |
| UNIDAD DE GESTION | texto | 0 | 5 | Unidades operativas |
| ESPECIALISTA | texto | 0 | 9 | Anonimizado (`Especialista 000xx`) |
| JEFE | texto | 0 | 3 | Anonimizado |
| GERENTE | texto | 0 | 2 | Anonimizado |
| DESCRIP2 | texto | 0 | 23 | Aliados (`Aliado 000xx`) |
| TERMINALES | float | 0 | 696 | Valores monetarios |
| TECNOLOGIA | float | 0 | 696 | Valores monetarios |
| T&T | float | 0 | 696 | Valores monetarios |

Sumas de control: TERMINALES ≈ 282 090 407 927; TECNOLOGIA ≈ 81 462 988 200; T&T ≈ 363 553 396 127.

### 2.2 Ventas (243 414 × 24)

| Columna | Tipo observado | Nulos % | Únicos | Observaciones |
|---------|----------------|--------:|-------:|---------------|
| Fecha Venta | int YYYYMMDD | 0 | 209 | Min 20230925, max 20260630 |
| Fecha Finalización Reserva | int YYYYMMDD | 0 | 179 | — |
| Descripción Estado Reserva | texto | 0 | 2 | `Tramitada` (243 363), `Activated` (51) |
| Identificación | float | 0.01 | 205 143 | Identificador de cliente (**PII**) |
| Cuotas | float | **94.77** | 6 | Solo ventas financiadas |
| Cédula Vendedor | texto | 0 | 1 291 | **PII**; contiene valor `-` |
| Región Comercial | texto | 0.91 | 5 | Mismos 5 miembros que Presupuesto |
| Archivo | texto | 0 | 2 | `Reposiciones TMK y Terminales libres`, `Tecnologia` |
| Código Factura | texto | 0.27 | 241 294 | 669 nulos; 1 451 duplicados no nulos |
| GV-Division | texto | 0 | 6 | 5 regiones + `REGIONAL` |
| GV-Especialista | texto | 0 | 22 | Catálogo más amplio que Presupuesto |
| GV-JEFE 1 CANAL REGIONAL | texto | 0 | 10 | — |
| CANAL | texto | 0 | 2 | Igual a Presupuesto |
| CANAL2 | texto | 0 | 4 | Igual a Presupuesto |
| GV_Desc2 | texto | 0 | 33 | Aliados |
| CATEGORIA | texto | 0 | 6 | 4 de Presupuesto + AUTOGESTION, AUTOGENERACION |
| AÑO | int | 0 | 2 | 25, 26 (2 dígitos) |
| MES | int | 0 | 7 | 1–6 y 12 |
| DIA | int | 0 | 31 | — |
| D_Division | texto | 0 | 6 | Tercera columna de región |
| GV-Gerente Area | texto | 0 | 6 | — |
| Valor Antes de iva | int | 0 | 1 793 | Suma total 336 834 686 474 |
| Marca | texto | 0 | 48 | Marcas de equipo (HP, ASUS, LENOVO…) |
| Nota_credito | texto | **97.59** | 1 | Solo `SI` (5 864) o nulo |

Periodos derivados (`AÑO`+`MES`): 202512, 202601–202606.

### 2.3 Registros (459 592 × 16)

| Columna | Tipo observado | Nulos % | Únicos | Observaciones |
|---------|----------------|--------:|-------:|---------------|
| CANTIDAD | int | 0 | 4 834 | Suma total 55 416 965 |
| DIVISION_COMERCIAL | texto | 3.1 | 7 | 5 regiones + `SIN_REGION`, `SIN REGION COMERCIAL` |
| NOMBRE_CAMPAÑA | texto | 0 | 96 | Campañas de gestión |
| PERIODO | int YYYYMM | 0 | 3 | 202604, 202605, 202606 |
| FECHA_GESTION | texto ISO | 1.5 | 118 | Min 2025-04-09, max 2026-07-02 |
| TIPO_CONTACTO | texto | 1.5 | 3 | NO CONTACTOS (293 481), CONTACTOS EFECTIVOS (110 532), CONTACTOS NO EFECTIVOS (48 706) |
| DETALLE1 | texto | 1.5 | 13 | Tipificación (NO_VENTA, NO CONTESTAN…) |
| INTENTOS | float | 1.5 | 9 397 | Suma total 171 344 493 |
| FECHA_CARGUE | texto ISO | 0 | 22 | Fechas de carga mensual/semanal |
| AREA_COMERCIAL | texto | **57.66** | 7 | Región alternativa, muy incompleta |
| SEGMENTO | texto | 0.03 | 9 | Valores inconsistentes (ver calidad) |
| dia | int | 0 | 32 | Incluye valores fuera de 1–31 (revisar) |
| ALIADO | texto | 0.15 | 44 | Catálogo más amplio de aliados |
| gerente | texto | 11.38 | 3 | Minúsculas en encabezado |
| jefe | texto | **68.88** | 8 | Muy incompleto |
| Especialista | texto | **68.88** | 29 | Muy incompleto |

---

## 3. Claves candidatas

| Fuente | Candidata | Veredicto observado |
|--------|-----------|---------------------|
| Ventas | `Código Factura` | **No es clave única**: 669 nulos y 1 451 duplicados no nulos |
| Ventas | `Identificación` | Identifica cliente, no transacción (205 143 únicos vs 243 414 filas) |
| Presupuesto | Combinación dimensional completa (MES + REGION + CANAL + CANAL2 + SUB CANAL + CATEGORIA + UNIDAD DE GESTION + ESPECIALISTA + JEFE + GERENTE + DESCRIP2) | Casi única: **5 duplicados** sobre ese conjunto |
| Registros | No se observa clave natural | Filas parecen agregados de gestión por campaña/fecha/tipificación |

Conclusión de análisis: **ninguna fuente trae clave primaria natural confiable**. La definición de grano/clave se decidirá en fase de modelado.

---

## 4. Calidad de datos — hallazgos

| # | Hallazgo | Severidad |
|---|----------|-----------|
| 1 | Formatos de fecha heterogéneos: int YYYYMMDD (Ventas), int YYYYMM (Presupuesto, Registros), string ISO (Registros) | Alta |
| 2 | Tres columnas de región en Ventas (`Región Comercial`, `GV-Division`, `D_Division`) con distribuciones distintas | Alta |
| 3 | Miembros de región no estándar: `REGIONAL` (Ventas), `SIN_REGION` y `SIN REGION COMERCIAL` (Registros) | Media |
| 4 | Catálogos de jerarquía comercial (especialista/jefe/gerente) no coinciden 1:1 entre fuentes | Alta |
| 5 | `Código Factura` con nulos y duplicados | Alta |
| 6 | Filas 100% duplicadas: 55 en Ventas, 25 en Registros | Media |
| 7 | `SEGMENTO` con variantes del mismo concepto: `Adicionales`/`Adicionales_`/`adicionales`, `MIGRACION`/`MIGRACION_` | Media |
| 8 | Alta nulidad: `Cuotas` 94.8%, `Nota_credito` 97.6%, `jefe`/`Especialista` 68.9% (Registros), `AREA_COMERCIAL` 57.7% | Media |
| 9 | **PII**: `Identificación` (cliente) y `Cédula Vendedor` | Alta (publicación) |
| 10 | `Cédula Vendedor` con valor `-` como texto | Baja |
| 11 | `AÑO` a 2 dígitos (25/26) en Ventas | Baja |
| 12 | `dia` en Registros con valores fuera de rango 1–31 | Baja |
| 13 | Presupuesto: 5 filas duplicadas sobre el conjunto dimensional completo | Media |
| 14 | Ventas contiene registros antiguos (desde 2023-09-25) fuera del rango presupuestado | Media |

---

## 5. Relaciones entre fuentes (solapamiento de miembros)

Comparación normalizada (mayúsculas/trim):

| Atributo | Presupuesto | Ventas | Registros | Intersección |
|----------|------------:|-------:|----------:|--------------|
| Región | 5 | 5 (+`REGIONAL` en GV-Division) | 5 (+2 valores "sin región") | 5/5 completa |
| CANAL | 2 | 2 | — | 2/2 completa |
| CANAL2 | 4 | 4 | — | 4/4 completa |
| CATEGORIA | 4 | 6 | — | 4 comunes; Ventas agrega 2 |
| ESPECIALISTA | 9 | 22 | 29 | 8 comunes P∩V; 7 P∩R |
| JEFE | 3 | 10 | 8 | 2 comunes P∩V; 3 P∩R |
| GERENTE | 2 | 6 | 3 | 2 comunes P∩V; 1 P∩R |
| Aliado | 23 | 33 | 44 | 22 comunes P∩V; 17 P∩R |
| Periodo | 202601–202606 | 202512–202606 | 202604–202606 | Presupuesto ⊆ Ventas; Registros ⊆ Presupuesto |

Observaciones:

- **No existe clave transaccional común** entre Ventas y Registros: la relación entre fuentes es por atributos compartidos (región, canal, jerarquía, aliado, periodo).
- Los catálogos de jerarquía y aliados de Presupuesto son **subconjuntos** de los de Ventas/Registros (con pocas excepciones: p. ej. `Especialista 00023` solo en Presupuesto).
- La cobertura temporal difiere entre fuentes; cualquier comparación cruzada deberá acotarse al rango común.

---

## 6. Trazabilidad

- Detalle de reglas de negocio observadas → `02_Reglas_Negocio.md`
- Hipótesis de modelo dimensional (fase de diseño) → `docs/modelo/03_Modelo_Dimensional.md`
- Modelo físico (fase de diseño/implementación) → `docs/modelo/04_Modelo_Fisico.md`

---

## 7. Errata / refinamiento (Subfase 2.1.1 — 2026-07-26)

Evidencia adicional en `docs/modelo/02_Declaracion_Grano.md`:

1. **`Código Factura` no único — CONFIRMADO.** No se corrige la Fase 1; se refuerza (2 897 filas en grupos repetidos; código anómalo `ENCI`).
2. **Presupuesto — REFINADO.** Los 5 cruces dimensionales duplicados **no** son filas idénticas: las medidas monetarias difieren. Duplicados exactos = 0.
3. **Registros — NUEVO.** ~80% de filas tienen `CANTIDAD > 1`: la fila es un **agregado de gestión**, no un contacto individual.
