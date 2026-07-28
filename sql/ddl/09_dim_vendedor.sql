-- =============================================================================
-- Script   : 09_dim_vendedor.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_vendedor)
-- =============================================================================
-- Descripción:
--   Crea la dimensión exclusiva dwh.dim_vendedor (Ventas). Contiene PII.
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_vendedor (
    sk_vendedor         BIGINT        NOT NULL,
    cedula_vendedor_nk  VARCHAR(40)   NOT NULL,
    nombre_vendedor     VARCHAR(120)  NULL,

    CONSTRAINT pk_dim_vendedor
        PRIMARY KEY (sk_vendedor),

    CONSTRAINT uq_dim_vendedor_nk
        UNIQUE (cedula_vendedor_nk)
);

COMMENT ON TABLE dwh.dim_vendedor IS
    'Dimensión exclusiva de vendedor (Ventas). Contiene PII. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_vendedor.sk_vendedor IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_vendedor.cedula_vendedor_nk IS
    'Cédula o -';
COMMENT ON COLUMN dwh.dim_vendedor.nombre_vendedor IS
    'Opcional';
