=========================================================
FASE 1 – ANÁLISIS
=========================================================

Estado:
APROBADA

Fecha de aprobación: 2026-07-25  
Aprobadores: Project Owner y Tech Lead

---------------------------------------------------------
Objetivo
---------------------------------------------------------

Completar el análisis de fuentes y del enunciado oficial: perfilar datos, documentar reglas observadas, traducir el PDF a requisitos funcionales y dejar la Fase 1 lista para Gate de Aprobación, sin iniciar diseño dimensional ni implementación.

---------------------------------------------------------
Entregables realizados
---------------------------------------------------------

- [✔] `docs/analisis/01_Perfilado_Datos.md` — inventario, calidad, claves candidatas, relaciones
- [✔] `docs/analisis/02_Reglas_Negocio.md` — reglas observadas + sección de reglas oficiales confirmadas
- [✔] `docs/analisis/03_Requisitos_Funcionales.md` — requisitos del PDF (objetivo, alcance, KPIs, reglas, entregables, restricciones, criterios, vacíos)
- [✔] Validación contra `Prueba_Tecnica.pdf`
- [✔] Gate de aprobación — aprobado explícitamente por Project Owner y Tech Lead

---------------------------------------------------------
Hallazgos principales
---------------------------------------------------------

1. Tres dominios de datos: Ventas, Presupuesto y Registros (gestión TMK), integrables por dimensiones compartidas, no por clave transaccional común.
2. Regla oficial de ventas válidas: código de factura presente y sin nota crédito.
3. Reglas oficiales de meta: días hábiles lun–sáb (sin domingos/festivos CO); meta diaria desde meta mensual; déficit acumula; excedente no reduce el día siguiente; recalculo dinámico.
4. Dos bloques de KPIs obligatorios (desempeño comercial y gestión TMK Outbound) definidos en el PDF.
5. Calidad de datos relevante: `Código Factura` no único; fechas heterogéneas; jerarquía comercial no 1:1 entre fuentes; PII en Ventas.

---------------------------------------------------------
Riesgos pendientes
---------------------------------------------------------

- Vacíos del PDF en fórmulas de % Gestión / Contactabilidad / Contactos efectivos / no efectivos.
- Medida de presupuesto a contrastar con ventas (`TERMINALES` / `TECNOLOGIA` / `T&T`) no especificada.
- Detalle operativo del recalculo dinámico + acumulación de déficit no formalizado en el PDF.
- Grano de ventas y columna oficial de región aún abiertos.
- Fecha límite oficial de la prueba: 28 de julio de 2026, 6:00 pm.

---------------------------------------------------------
Preguntas resueltas
---------------------------------------------------------

- Alcance temporal de ventas/presupuesto: últimos seis meses (PDF).
- Tratamiento de notas crédito: excluyen la venta del análisis válido (PDF).
- Criterio mínimo de venta válida: factura + sin nota crédito (PDF).
- Canal del Reto 2: TMK Outbound (PDF).

---------------------------------------------------------
Preguntas abiertas
---------------------------------------------------------

- Grano oficial de venta con facturas duplicadas.
- Tratamiento de 5 duplicados dimensionales en Presupuesto.
- Columna oficial de región en Ventas.
- Fórmulas exactas de los % del Reto 2.
- Nivel al que aplica la meta diaria (jerarquía).
- Calendario de festivos a usar.
- Política de PII para publicación del repositorio.

Detalle: `03_Requisitos_Funcionales.md` §8 y `02_Reglas_Negocio.md` §4.

---------------------------------------------------------
Recomendación del desarrollador para iniciar la Fase 2
---------------------------------------------------------

Se recomienda **aprobar la Fase 1** tras revisión de este acta, e iniciar la Fase 2 (Modelo dimensional) con estos insumos:

- Requisitos y KPIs oficiales (`03_Requisitos_Funcionales.md`).
- Reglas oficiales O1–O10 (`02_Reglas_Negocio.md` §5).
- Hallazgos de calidad y claves candidatas (`01_Perfilado_Datos.md`).

En Fase 2 deberán resolverse explícitamente (con decisión documentada) los vacíos V1–V12 que el PDF no define, sin contradecir el enunciado.  
**No** iniciar ETL, PostgreSQL, Airflow ni Power BI hasta aprobar el modelo dimensional.

=========================================================
Gate cerrado con aprobación explícita del Project Owner y del Tech Lead.
La Fase 2 queda lista para iniciar cuando el Tech Lead emita
su planificación y lineamientos.
=========================================================
