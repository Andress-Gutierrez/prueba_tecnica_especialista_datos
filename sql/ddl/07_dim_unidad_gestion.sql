-- =============================================================================
-- Script   : 07_dim_unidad_gestion.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_unidad_gestion)
-- =============================================================================
-- Descripción:
--   Crea la dimensión exclusiva dwh.dim_unidad_gestion (Presupuesto).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_unidad_gestion (
    sk_unidad_gestion       BIGINT        NOT NULL,
    unidad_gestion_nk       VARCHAR(120)  NOT NULL,
    nombre_unidad_gestion   VARCHAR(120)  NOT NULL,

    CONSTRAINT pk_dim_unidad_gestion
        PRIMARY KEY (sk_unidad_gestion),

    CONSTRAINT uq_dim_unidad_gestion_nk
        UNIQUE (unidad_gestion_nk)
);

COMMENT ON TABLE dwh.dim_unidad_gestion IS
    'Dimensión exclusiva de unidad de gestión (Presupuesto). Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_unidad_gestion.sk_unidad_gestion IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_unidad_gestion.unidad_gestion_nk IS
    'UNIDAD DE GESTION';
COMMENT ON COLUMN dwh.dim_unidad_gestion.nombre_unidad_gestion IS
    'Display';
