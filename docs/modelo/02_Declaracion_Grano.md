# 02 — Declaración del Grano

Fase: **2 — Diseño del Data Warehouse**  
Subfase: **2.1.1 — Declaración del grano**  
Fecha: 2026-07-26  
Insumos: `data/raw/*.xlsb`, `01_Proceso_Negocio.md`, `docs/analisis/01_Perfilado_Datos.md`  
Scripts de evidencia: `scripts/declare_grain_evidence.py`, `scripts/declare_grain_evidence_2.py`

> Toda conclusión de este documento está respaldada por evidencia observada en las fuentes.  
> No se asume clave natural sin medirla.

---

## Correcciones / refinamientos respecto a la Fase 1

| Tema | Fase 1 | Evidencia 2.1.1 | Acción |
|------|--------|-----------------|--------|
| `Código Factura` no único | Afirmado (1 451 dups no nulos) | **Confirmado**: 2 897 filas en grupos de factura repetida; 1 446 códigos distintos repetidos; además existe el código anómalo `ENCI` (7 filas) | Se mantiene; se refuerza con detalle de columnas que cambian |
| Duplicados dimensionales Presupuesto (5) | Detectados | **Refinado**: no son filas idénticas; para el mismo cruce dimensional las medidas **difieren** (2 valores distintos de TERMINALES/TECNOLOGIA/T&T). Filas exactas duplicadas = **0** | Se actualiza el matiz en perfilado (ver abajo) |
| Grano de Registros | No declarado formalmente | **Nuevo**: ~80.22% de filas tienen `CANTIDAD > 1` → la fila es un **agregado**, no un contacto individual | Declaración formal en este documento |

No se encontró evidencia de que `Código Factura` sea único. La conclusión de Fase 1 sobre ese punto **no era incorrecta**.

---

# Fuente 1 — Ventas.xlsb

## 1. Proceso de negocio

**Venta comercial (cierre)** — registro del resultado comercial de una transacción.

## 2. Fuente analizada

`data/raw/Ventas.xlsb` — hoja `Ventas` — **243 414** filas × **24** columnas.

## 3. Pregunta de investigación

¿Qué representa exactamente una fila?

## 4. Evidencia encontrada

| Hecho medido | Valor |
|--------------|------:|
| Filas totales | 243 414 |
| Filas 100% idénticas (duplicado exacto) | 55 |
| `Código Factura` nulos | 669 |
| `Código Factura` no nulos | 242 745 |
| Valores distintos de `Código Factura` (no nulos) | 241 294 |
| Filas adicionales por repetición de factura (`duplicated` sobre factura no nula) | 1 451 |
| Filas que pertenecen a un código de factura repetido | 2 897 |
| Códigos de factura distintos que se repiten | 1 446 |
| Código anómalo `ENCI` | 7 filas, con clientes/marcas/valores/fechas distintos |
| Patrón dominante de repetición | La mayoría de códigos repetidos aparecen **2 veces** |
| Clientes distintos (`Identificación`) | 205 143 |
| Ventas con factura y sin nota crédito `SI` | 236 881 |

En un código de factura repetido de ejemplo, cambian entre filas (entre otras): `Fecha Venta`, `Identificación`, `Cédula Vendedor`, `Marca`, `Valor Antes de iva`, jerarquía (`GV-Especialista`, `GV_Desc2`), región y categoría.

Ranking de columnas que más varían dentro de grupos de la misma factura (conteo de facturas donde la columna no es constante): `Cédula Vendedor` (1 385), `GV_Desc2` (1 318), `GV-Especialista` (1 293), `GV-JEFE…` (1 155), `CANAL2` (1 139), `Región Comercial` (1 093), `Marca`/`Valor` también varían con frecuencia.

Pruebas de unicidad (sobre filas con factura no nula):

| Candidato de clave | Filas duplicadas (`duplicated`) |
|--------------------|--------------------------------:|
| `Código Factura` | 1 451 |
| `Código Factura` + `Marca` | 1 443 |
| `Código Factura` + `Valor Antes de iva` | 1 184 |
| `Código Factura` + `Fecha Venta` | 977 |
| `Código Factura` + `Identificación` | 979 |
| `Código Factura` + `Cédula Vendedor` | 65 |
| `Código Factura` + `Marca` + `Valor` + `Fecha Venta` | 974 |

## 5. Análisis

- **¿Existe una clave natural?**  
  **No.** `Código Factura` no identifica de forma única la fila. Ninguna combinación comercial evaluada elimina por completo los duplicados. La unicidad solo se acerca al nivel de la fila completa (quedan 55 duplicados exactos).

- **¿Qué columnas identifican el evento?**  
  El evento se expresa por el conjunto de atributos de la fila: fecha, cliente, vendedor, factura (si existe), valor, marca, canal, jerarquía, aliado, región. No hay un identificador de negocio único en la fuente.

- **¿Hay duplicados?**  
  Sí: 55 exactos; 2 897 filas en grupos de factura repetida.

- **Si existen duplicados de factura, ¿qué cambia?**  
  Cambia el contenido comercial (cliente, valor, marca, fechas, jerarquía, aliado, región). Por tanto, **no** se puede interpretar “misma factura = mismo evento”.

- **¿Cuál es el nivel mínimo de detalle?**  
  El nivel mínimo disponible en la fuente es **la fila**: un registro transaccional de venta. No hay un nivel más fino (p. ej. componente dentro de la línea) en el archivo.

## 6. Conclusión — grano propuesto (Ventas)

**Grano:** una fila = **un evento / registro transaccional de venta** en la fuente operativa.

**No es:** una factura única, ni un cliente único, ni un día-aliado agregado.

**Justificación:** la fuente no aporta clave natural estable; `Código Factura` se reutiliza entre eventos distintos; el detalle más fino observable es la propia fila.

## 7. Riesgos si el grano fuera incorrecto

| Error de grano | Consecuencia |
|----------------|--------------|
| Modelar 1 fila = 1 factura | Inflar/descuadrar ventas al colapsar eventos distintos que comparten código; distorsionar cumplimiento vs presupuesto |
| Ignorar filas sin factura o con nota crédito sin filtro de negocio | Contar ventas no válidas según el enunciado |
| Deduplicar solo por factura | Borrar ventas reales distintas |
| Tratar los 55 duplicados exactos como eventos independientes sin regla | Sobreconteo menor pero real |

---

# Fuente 2 — Presupuesto.xlsb

## 1. Proceso de negocio

**Planeación y seguimiento de metas (presupuesto).**

## 2. Fuente analizada

`data/raw/Presupuesto.xlsb` — hoja `Presupuesto` — **731** filas × **14** columnas.

## 3. Pregunta de investigación

¿Qué representa exactamente una fila?

## 4. Evidencia encontrada

| Hecho medido | Valor |
|--------------|------:|
| Filas totales | 731 |
| Duplicados exactos (todas las columnas) | **0** |
| Columnas dimensionales candidatas | `MES`, `REGION`, `CANAL`, `CANAL2`, `SUB CANAL`, `CATEGORIA`, `UNIDAD DE GESTION`, `ESPECIALISTA`, `JEFE`, `GERENTE`, `DESCRIP2` |
| Combinaciones distintas de ese cruce | 726 |
| Filas cuya clave dimensional se repite | 10 (5 cruces × 2 filas) |
| Medidas | `TERMINALES`, `TECNOLOGIA`, `T&T` |
| Filas donde `T&T ≠ TERMINALES + TECNOLOGIA` | **0** (delta máxima 0) |

Ejemplo de cruce repetido (202603 / REGION CENTRO / TELEFONICO VENTA / TMK IN BOUND / MASIVO / … / Aliado 00008):

- Fila A: TERMINALES ≈ 3.18e9 ; TECNOLOGIA ≈ 7.64e8 ; T&T ≈ 3.95e9  
- Fila B: TERMINALES ≈ 6.78e8 ; TECNOLOGIA ≈ 1.63e8 ; T&T ≈ 8.41e8  

Las medidas **no son iguales**: son dos asignaciones numéricas distintas para el mismo cruce descriptivo.

## 5. Análisis

- **¿Existe una clave natural?**  
  **Casi.** El cruce de las 11 columnas dimensionales identifica de forma única **726/731** filas. En **5** cruces hay ambigüedad (2 filas con medidas distintas). No hay un ID de presupuesto en la fuente.

- **¿Qué columnas identifican el evento?**  
  El “evento” es la **asignación de meta mensual** al cruce comercial completo (periodo + región + canal/subcanal/categoría/unidad + jerarquía + aliado).

- **¿Hay duplicados?**  
  Exactos: no. Por clave dimensional: sí (5 cruces).

- **Si existen, ¿qué cambia?**  
  Cambian únicamente las **medidas** monetarias.

- **¿Cuál es el nivel mínimo de detalle?**  
  Meta mensual al nivel del cruce dimensional completo. No hay meta diaria en la fuente (la meta diaria es regla de negocio derivada).

## 6. Conclusión — grano propuesto (Presupuesto)

**Grano:** una fila = **una asignación de meta mensual** para el cruce  
`MES + REGION + CANAL + CANAL2 + SUB CANAL + CATEGORIA + UNIDAD DE GESTION + ESPECIALISTA + JEFE + GERENTE + DESCRIP2 (aliado)`,  
con medidas `TERMINALES`, `TECNOLOGIA` y `T&T` (donde `T&T = TERMINALES + TECNOLOGIA` en el 100% de las filas).

**Pendiente de regla de negocio (no inventada aquí):** para los 5 cruces duplicados, decidir si las medidas se **suman** o si existe un atributo faltante. La evidencia muestra que no son copias idénticas.

## 7. Riesgos si el grano fuera incorrecto

| Error de grano | Consecuencia |
|----------------|--------------|
| Agregar a nivel más grueso (solo región-mes) | Perder capacidad de comparar vs ventas por aliado/especialista/jefe |
| Ignorar los 5 cruces duplicados o quedarse con una sola fila | Subestimar o sobrestimar la meta |
| Tratar `T&T` y `TERMINALES`+`TECNOLOGIA` como independientes sin coherencia | Doble conteo de meta |
| Forzar meta diaria como grano de la fuente | Inventar detalle que la fuente no trae |

---

# Fuente 3 — Registros.xlsb

## 1. Proceso de negocio

**Gestión de registros TMK Outbound** (contactabilidad / tipificación).

## 2. Fuente analizada

`data/raw/Registros.xlsb` — hoja `Registros` — **459 592** filas × **16** columnas.

## 3. Pregunta de investigación

¿Qué representa exactamente una fila?

## 4. Evidencia encontrada

| Hecho medido | Valor |
|--------------|------:|
| Filas totales | 459 592 |
| Duplicados exactos | 25 |
| Filas con `CANTIDAD = 1` | 19.78% |
| Filas con `CANTIDAD > 1` | **80.22%** |
| `CANTIDAD` máxima | 222 259 |
| `INTENTOS` máxima | 415 713 |
| `FECHA_GESTION` / `TIPO_CONTACTO` nulos | 1.5% (6 873 filas) |
| Suma de `CANTIDAD` en filas sin tipificación | 9 738 049 |

Pruebas de unicidad (atributos de negocio, tipificación no nula — 452 719 filas):

| Clave candidata | Duplicados |
|-----------------|-----------:|
| Campaña + periodo + fecha gestión + aliado + tipo + detalle | 329 184 |
| + división comercial | 57 836 |
| + segmento | 57 836 |
| + fecha cargue + (sin jerarquía) | 3 080 |
| Atributos amplios incl. jerarquía/área/día | 13 |

Cuando la clave campaña+periodo+fecha+aliado+tipo+detalle+división+segmento+fecha_cargue se repite, lo que cambia es típicamente `CANTIDAD`, `INTENTOS` y/o `AREA_COMERCIAL`.

En grupos con tipificación nula, filas del mismo cruce grueso difieren por `CANTIDAD` y `FECHA_CARGUE` (ejemplo: misma campaña/periodo/región con cantidades 60 057 vs 48 vs 41…).

## 5. Análisis

- **¿Existe una clave natural?**  
  **No.** No hay un ID de registro/contacto. Ninguna clave de negocio evaluada deja la tabla 100% única sin incluir las medidas o atributos inestables (`AREA_COMERCIAL`).

- **¿Qué columnas identifican el evento?**  
  La fila describe un **recorte agregado** de gestión: campaña, periodo, fecha de gestión (si existe), tipificación (`TIPO_CONTACTO`/`DETALLE1`), aliado, región/división, segmento, y a veces fecha de cargue / jerarquía.

- **¿Hay duplicados?**  
  Sí: 25 exactos; miles de colisiones en claves de negocio sin medidas.

- **Si existen, ¿qué cambia?**  
  Principalmente `CANTIDAD`, `INTENTOS` y a veces `AREA_COMERCIAL` / `FECHA_CARGUE`.

- **¿Cuál es el nivel mínimo de detalle?**  
  **No es el contacto individual.** El 80% de las filas ya consolidan volumen (`CANTIDAD > 1`). El nivel mínimo observable es el **agregado tipificado** (slice de gestión), no la persona contactada.

## 6. Conclusión — grano propuesto (Registros)

**Grano:** una fila = **un agregado de gestión TMK Outbound**  
(volumen `CANTIDAD` + esfuerzo `INTENTOS`)  
para un cruce de campaña / periodo / fecha de gestión / tipificación / aliado / región / segmento (y atributos de carga/jerarquía cuando existen).

**No es:** un registro-persona ni un intento unitario.

**Justificación:** la distribución de `CANTIDAD` e `INTENTOS` demuestra agregación; la ausencia de ID de contacto y la colisión de claves confirman que la fuente no entrega el nivel atómico de contacto.

## 7. Riesgos si el grano fuera incorrecto

| Error de grano | Consecuencia |
|----------------|--------------|
| Tratar cada fila como 1 contacto | Subcontar masivamente (ignorar `CANTIDAD`) o malinterpretar KPIs de contactabilidad |
| Sumar filas sin sumar `CANTIDAD` | KPIs de “registros entregados” incorrectos |
| Colapsar a campaña-aliado sin tipificación | Perder % efectivos / no efectivos |
| Ignorar filas sin tipificación (1.5%) sin regla | Sesgo en volumen entregado (millones de `CANTIDAD`) |

---

## Síntesis de granos (Subfase 2.1.1)

| Proceso | Fuente | Grano declarado |
|---------|--------|-----------------|
| Venta comercial | `Ventas.xlsb` | 1 fila = 1 evento/registro transaccional de venta |
| Metas / presupuesto | `Presupuesto.xlsb` | 1 fila = 1 asignación de meta mensual al cruce comercial completo |
| Gestión TMK Outbound | `Registros.xlsb` | 1 fila = 1 agregado tipificado de gestión (`CANTIDAD`/`INTENTOS`) |

Estos granos son la base obligatoria para la Subfase 2.2 (revisión del borrador dimensional). No se ha modificado el modelo dimensional ni el físico en esta sesión.
