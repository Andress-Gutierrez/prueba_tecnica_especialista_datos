-- =============================================================================
-- Script   : 13_dim_tipo_contacto.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_tipo_contacto)
-- =============================================================================
-- Descripción:
--   Crea la dimensión exclusiva dwh.dim_tipo_contacto (Gestión TMK).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_tipo_contacto (
    sk_tipo_contacto      BIGINT        NOT NULL,
    tipo_contacto         VARCHAR(80)   NOT NULL,
    detalle_contacto      VARCHAR(120)  NULL,
    nombre_tipo_contacto  VARCHAR(160)  NOT NULL,

    CONSTRAINT pk_dim_tipo_contacto
        PRIMARY KEY (sk_tipo_contacto),

    CONSTRAINT uq_dim_tipo_contacto
        UNIQUE (tipo_contacto, detalle_contacto)
);

COMMENT ON TABLE dwh.dim_tipo_contacto IS
    'Dimensión exclusiva de tipificación de contacto TMK. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_tipo_contacto.sk_tipo_contacto IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_tipo_contacto.tipo_contacto IS
    'TIPO_CONTACTO';
COMMENT ON COLUMN dwh.dim_tipo_contacto.detalle_contacto IS
    'DETALLE1';
COMMENT ON COLUMN dwh.dim_tipo_contacto.nombre_tipo_contacto IS
    'Display';
