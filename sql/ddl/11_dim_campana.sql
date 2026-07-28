-- =============================================================================
-- Script   : 11_dim_campana.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_campana)
-- =============================================================================
-- Descripción:
--   Crea la dimensión exclusiva dwh.dim_campana (Gestión TMK).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_campana (
    sk_campana      BIGINT        NOT NULL,
    campana_nk      VARCHAR(200)  NOT NULL,
    nombre_campana  VARCHAR(200)  NOT NULL,

    CONSTRAINT pk_dim_campana
        PRIMARY KEY (sk_campana),

    CONSTRAINT uq_dim_campana_nk
        UNIQUE (campana_nk)
);

COMMENT ON TABLE dwh.dim_campana IS
    'Dimensión exclusiva de campaña TMK. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_campana.sk_campana IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_campana.campana_nk IS
    'NOMBRE_CAMPAÑA';
COMMENT ON COLUMN dwh.dim_campana.nombre_campana IS
    'Display';
