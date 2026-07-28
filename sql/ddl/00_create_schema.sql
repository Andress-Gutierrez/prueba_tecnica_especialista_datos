-- =============================================================================
-- Script   : 00_create_schema.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- =============================================================================
-- Descripción:
--   Crea el esquema analítico oficial del Data Warehouse (Star Schema).
--   Base de datos de destino: dwh_comercial (definida en infraestructura Docker).
--   Este script es idempotente: puede ejecutarse múltiples veces sin error.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS dwh;

COMMENT ON SCHEMA dwh IS
    'Esquema analítico del DWH (dimensiones y hechos). Proyecto: prueba_tecnica_especialista_datos.';
