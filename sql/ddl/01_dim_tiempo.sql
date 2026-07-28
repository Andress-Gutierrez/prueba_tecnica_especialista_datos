-- =============================================================================
-- Script   : 01_dim_tiempo.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.1 dwh.dim_tiempo)
-- =============================================================================
-- Descripción:
--   Crea la dimensión conformada dwh.dim_tiempo (calendario de análisis).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
--   Sin INSERT, sin índices adicionales, sin seeds.
-- =============================================================================
-- Restricciones (Modelo Físico):
--   UNIQUE (periodo_yyyymm, fecha) — soporta filas de grano día y mes puro
--     (fecha NULL solo para mes puro, según documentación).
--   CHECK (mes BETWEEN 1 AND 12)
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.dim_tiempo (
    sk_tiempo       BIGINT       NOT NULL,
    fecha           DATE         NULL,
    anio            INTEGER      NOT NULL,
    mes             INTEGER      NOT NULL,
    dia             INTEGER      NULL,
    periodo_yyyymm  INTEGER      NOT NULL,
    nombre_mes      VARCHAR(20)  NULL,
    dia_semana      INTEGER      NULL,
    es_dia_habil    BOOLEAN      NOT NULL,
    es_festivo_co   BOOLEAN      NOT NULL,
    es_fin_semana   BOOLEAN      NULL,

    CONSTRAINT pk_dim_tiempo
        PRIMARY KEY (sk_tiempo),

    CONSTRAINT uq_dim_tiempo_periodo_fecha
        UNIQUE (periodo_yyyymm, fecha),

    CONSTRAINT ck_dim_tiempo_mes
        CHECK (mes BETWEEN 1 AND 12)
);

COMMENT ON TABLE dwh.dim_tiempo IS
    'Dimensión conformada de tiempo (calendario). Alimenta meta diaria (O2–O6). Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.dim_tiempo.sk_tiempo IS
    'Surrogate key';
COMMENT ON COLUMN dwh.dim_tiempo.fecha IS
    'Fecha día (NULL solo para filas de grano mes puro si se usan)';
COMMENT ON COLUMN dwh.dim_tiempo.anio IS
    'Año (YYYY)';
COMMENT ON COLUMN dwh.dim_tiempo.mes IS
    'Mes (1–12)';
COMMENT ON COLUMN dwh.dim_tiempo.dia IS
    'Día del mes';
COMMENT ON COLUMN dwh.dim_tiempo.periodo_yyyymm IS
    'Periodo AAAAMM';
COMMENT ON COLUMN dwh.dim_tiempo.nombre_mes IS
    'Nombre del mes';
COMMENT ON COLUMN dwh.dim_tiempo.dia_semana IS
    '1=lunes … 7=domingo';
COMMENT ON COLUMN dwh.dim_tiempo.es_dia_habil IS
    'Lun–sáb y no festivo CO';
COMMENT ON COLUMN dwh.dim_tiempo.es_festivo_co IS
    'Festivo nacional Colombia';
COMMENT ON COLUMN dwh.dim_tiempo.es_fin_semana IS
    'Sábado/domingo';
