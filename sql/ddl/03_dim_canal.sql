-- =============================================================================
-- Script   : 03_dim_canal.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_canal)
-- =============================================================================
-- Descripción:
--   Crea la dimensión conformada dwh.dim_canal (desnormalizada Star).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_canal (
    sk_canal    BIGINT       NOT NULL,
    canal       VARCHAR(80)  NOT NULL,
    canal2      VARCHAR(80)  NULL,
    sub_canal   VARCHAR(80)  NULL,

    CONSTRAINT pk_dim_canal
        PRIMARY KEY (sk_canal),

    CONSTRAINT uq_dim_canal_cruce
        UNIQUE (canal, canal2, sub_canal)
);

COMMENT ON TABLE dwh.dim_canal IS
    'Dimensión conformada de canal (canal / canal2 / sub_canal desnormalizado). Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_canal.sk_canal IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_canal.canal IS
    'CANAL';
COMMENT ON COLUMN dwh.dim_canal.canal2 IS
    'CANAL2';
COMMENT ON COLUMN dwh.dim_canal.sub_canal IS
    'SUB CANAL';
