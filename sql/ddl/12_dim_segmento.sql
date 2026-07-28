-- =============================================================================
-- Script   : 12_dim_segmento.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_segmento)
-- =============================================================================
-- Descripción:
--   Crea la dimensión exclusiva dwh.dim_segmento (Gestión TMK).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_segmento (
    sk_segmento            BIGINT       NOT NULL,
    segmento_nk            VARCHAR(80)  NOT NULL,
    segmento_normalizado   VARCHAR(80)  NOT NULL,
    nombre_segmento        VARCHAR(80)  NOT NULL,

    CONSTRAINT pk_dim_segmento
        PRIMARY KEY (sk_segmento),

    CONSTRAINT uq_dim_segmento_nk
        UNIQUE (segmento_nk)
);

COMMENT ON TABLE dwh.dim_segmento IS
    'Dimensión exclusiva de segmento de gestión TMK. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_segmento.sk_segmento IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_segmento.segmento_nk IS
    'Valor origen';
COMMENT ON COLUMN dwh.dim_segmento.segmento_normalizado IS
    'Valor limpio';
COMMENT ON COLUMN dwh.dim_segmento.nombre_segmento IS
    'Display';
