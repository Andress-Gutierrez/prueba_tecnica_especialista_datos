-- =============================================================================
-- Script   : 02_dim_region.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_region)
-- =============================================================================
-- Descripción:
--   Crea la dimensión conformada dwh.dim_region.
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_region (
    sk_region       BIGINT        NOT NULL,
    region_nk       VARCHAR(100)  NOT NULL,
    nombre_region   VARCHAR(100)  NOT NULL,
    es_sin_region   BOOLEAN       NOT NULL,

    CONSTRAINT pk_dim_region
        PRIMARY KEY (sk_region),

    CONSTRAINT uq_dim_region_nk
        UNIQUE (region_nk)
);

COMMENT ON TABLE dwh.dim_region IS
    'Dimensión conformada de región geográfica comercial. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_region.sk_region IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_region.region_nk IS
    'Texto de negocio normalizado';
COMMENT ON COLUMN dwh.dim_region.nombre_region IS
    'Etiqueta display';
COMMENT ON COLUMN dwh.dim_region.es_sin_region IS
    'Miembros tipo SIN_REGION';
