# Checklist de Entrega

**Proyecto:** Prueba Técnica — Especialista de Datos  
**Fecha límite:** martes 28 de julio de 2026, 6:00 pm  
**Estado:** listo para revisión final

---

## Documentación esperada

| Requisito del PDF | Estado | Evidencia |
|---|---:|---|
| Diseño del modelo de datos | Cumplido | `docs/Documento_Tecnico_Final.md` secciones 4, 5 y 6 |
| Depuraciones o transformaciones realizadas | Cumplido | `docs/Documento_Tecnico_Final.md` secciones 7 y 8 |
| Novedades identificadas en la información | Cumplido | `docs/Documento_Tecnico_Final.md` sección 13 |
| Justificación del modelo implementado | Cumplido | `docs/Documento_Tecnico_Final.md` sección 5 |
| Principales cálculos DAX utilizados | Cumplido | `docs/Documento_Tecnico_Final.md` sección 12 |
| Uso de herramientas de IA y prompts | Cumplido | `docs/Documento_Tecnico_Final.md` sección 14 |

## Entregables solicitados

| Entregable del PDF | Estado | Ruta |
|---|---:|---|
| Scripts de creación de datos | Cumplido | `sql/ddl/`, `sql/dml/` |
| Scripts de transformación de datos | Cumplido | `etl/`, `repository/`, `scripts/` |
| Archivo Power BI `.pbix` | Cumplido | `powerbi/PowerBI_ETL_Comercial.pbix` |
| Documento de explicación | Cumplido | `docs/Documento_Tecnico_Final.md` y `docs/entregables/Documento_Tecnico_Final.pdf` |

## Evidencia de validación

Ejecución final del ETL completo:

- `fact_ventas`: 243359 filas.
- `fact_presupuesto`: 731 filas.
- `fact_gestion_tmk`: 459567 filas.
- Validación DW: OK.
- Chequeos: 38.
- Fallidos: 0.
- Orphans: 0.

Evidencia: `logs/latest.log`.

## Nota de revisión final

Antes de enviar, verificar manualmente:

- El archivo `PowerBI_ETL_Comercial.pbix` está guardado después del refresh.
- El documento PDF abre correctamente.
- El `.zip` de entrega no incluye `.env` ni credenciales locales.
