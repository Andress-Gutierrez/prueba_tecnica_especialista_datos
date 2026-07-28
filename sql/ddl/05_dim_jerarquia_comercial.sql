-- =============================================================================
-- Script   : 05_dim_jerarquia_comercial.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_jerarquia_comercial)
-- =============================================================================
-- Descripción:
--   Crea la dimensión conformada dwh.dim_jerarquia_comercial (desnormalizada).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_jerarquia_comercial (
    sk_jerarquia   BIGINT       NOT NULL,
    gerente        VARCHAR(80)  NULL,
    jefe           VARCHAR(80)  NULL,
    especialista   VARCHAR(80)  NULL,

    CONSTRAINT pk_dim_jerarquia_comercial
        PRIMARY KEY (sk_jerarquia),

    CONSTRAINT uq_dim_jerarquia_comercial
        UNIQUE (gerente, jefe, especialista)
);

COMMENT ON TABLE dwh.dim_jerarquia_comercial IS
    'Dimensión conformada de jerarquía comercial (gerente → jefe → especialista), desnormalizada. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_jerarquia_comercial.sk_jerarquia IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_jerarquia_comercial.gerente IS
    'Nivel gerente';
COMMENT ON COLUMN dwh.dim_jerarquia_comercial.jefe IS
    'Nivel jefe';
COMMENT ON COLUMN dwh.dim_jerarquia_comercial.especialista IS
    'Nivel especialista';
