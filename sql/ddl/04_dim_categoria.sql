-- =============================================================================
-- Script   : 04_dim_categoria.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_categoria)
-- =============================================================================
-- Descripción:
--   Crea la dimensión conformada dwh.dim_categoria.
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_categoria (
    sk_categoria      BIGINT       NOT NULL,
    categoria_nk      VARCHAR(80)  NOT NULL,
    nombre_categoria  VARCHAR(80)  NOT NULL,

    CONSTRAINT pk_dim_categoria
        PRIMARY KEY (sk_categoria),

    CONSTRAINT uq_dim_categoria_nk
        UNIQUE (categoria_nk)
);

COMMENT ON TABLE dwh.dim_categoria IS
    'Dimensión conformada de categoría comercial. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_categoria.sk_categoria IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_categoria.categoria_nk IS
    'Categoría';
COMMENT ON COLUMN dwh.dim_categoria.nombre_categoria IS
    'Display';
