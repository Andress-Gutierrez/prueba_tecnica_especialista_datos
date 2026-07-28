-- =============================================================================
-- Script   : 08_dim_marca.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_marca)
-- =============================================================================
-- Descripción:
--   Crea la dimensión exclusiva dwh.dim_marca (Ventas).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_marca (
    sk_marca      BIGINT       NOT NULL,
    marca_nk      VARCHAR(80)  NOT NULL,
    nombre_marca  VARCHAR(80)  NOT NULL,

    CONSTRAINT pk_dim_marca
        PRIMARY KEY (sk_marca),

    CONSTRAINT uq_dim_marca_nk
        UNIQUE (marca_nk)
);

COMMENT ON TABLE dwh.dim_marca IS
    'Dimensión exclusiva de marca (Ventas). Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_marca.sk_marca IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_marca.marca_nk IS
    'Marca';
COMMENT ON COLUMN dwh.dim_marca.nombre_marca IS
    'Display';
