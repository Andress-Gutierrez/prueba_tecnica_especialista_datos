-- =============================================================================
-- Script   : 06_dim_aliado.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_aliado)
-- =============================================================================
-- Descripción:
--   Crea la dimensión conformada dwh.dim_aliado.
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_aliado (
    sk_aliado      BIGINT        NOT NULL,
    aliado_nk      VARCHAR(80)   NOT NULL,
    nombre_aliado  VARCHAR(120)  NOT NULL,

    CONSTRAINT pk_dim_aliado
        PRIMARY KEY (sk_aliado),

    CONSTRAINT uq_dim_aliado_nk
        UNIQUE (aliado_nk)
);

COMMENT ON TABLE dwh.dim_aliado IS
    'Dimensión conformada de aliado / socio operativo. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_aliado.sk_aliado IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_aliado.aliado_nk IS
    'Código/texto homologado';
COMMENT ON COLUMN dwh.dim_aliado.nombre_aliado IS
    'Display';
