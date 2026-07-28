-- =============================================================================
-- Script   : 21_alter_dim_tiempo_calendar_master.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 5.6.x — Infraestructura calendario corporativo
-- Fecha    : 2026-07-28
-- Autor    : Cursor
-- =============================================================================
-- Descripción:
--   Extiende dwh.dim_tiempo para soportar calendario corporativo oficial:
--   - es_festivo
--   - nombre_festivo
--   - es_habil
--   Mantiene compatibilidad con columnas existentes:
--   - es_festivo_co
--   - es_dia_habil
-- =============================================================================

ALTER TABLE dwh.dim_tiempo
    ADD COLUMN IF NOT EXISTS es_festivo BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE dwh.dim_tiempo
    ADD COLUMN IF NOT EXISTS nombre_festivo VARCHAR(120) NULL;

ALTER TABLE dwh.dim_tiempo
    ADD COLUMN IF NOT EXISTS es_habil BOOLEAN NOT NULL DEFAULT FALSE;

UPDATE dwh.dim_tiempo
SET
    es_festivo = COALESCE(es_festivo_co, FALSE),
    es_habil = COALESCE(es_dia_habil, FALSE)
WHERE fecha IS NOT NULL;

COMMENT ON COLUMN dwh.dim_tiempo.es_festivo IS
    'Festivo oficial corporativo (fuente API festivos.com.co)';

COMMENT ON COLUMN dwh.dim_tiempo.nombre_festivo IS
    'Nombre del festivo oficial corporativo';

COMMENT ON COLUMN dwh.dim_tiempo.es_habil IS
    'Dia habil corporativo: no domingo y no festivo';
