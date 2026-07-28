-- =============================================================================
-- Script   : 10_dim_validez_venta.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_validez_venta)
-- =============================================================================
-- Descripción:
--   Crea la dimensión exclusiva dwh.dim_validez_venta (Ventas / Reto 1).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_validez_venta (
    sk_validez           BIGINT       NOT NULL,
    tiene_factura        BOOLEAN      NOT NULL,
    tiene_nota_credito   BOOLEAN      NOT NULL,
    es_venta_valida      BOOLEAN      NOT NULL,
    descripcion          VARCHAR(80)  NOT NULL,

    CONSTRAINT pk_dim_validez_venta
        PRIMARY KEY (sk_validez),

    CONSTRAINT uq_dim_validez_venta_flags
        UNIQUE (tiene_factura, tiene_nota_credito)
);

COMMENT ON TABLE dwh.dim_validez_venta IS
    'Dimensión exclusiva de validez de venta (factura presente ∧ sin nota crédito). Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_validez_venta.sk_validez IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_validez_venta.tiene_factura IS
    'Código factura presente';
COMMENT ON COLUMN dwh.dim_validez_venta.tiene_nota_credito IS
    'Nota crédito = SI';
COMMENT ON COLUMN dwh.dim_validez_venta.es_venta_valida IS
    'tiene_factura ∧ ¬tiene_nota_credito';
COMMENT ON COLUMN dwh.dim_validez_venta.descripcion IS
    'Etiqueta';
