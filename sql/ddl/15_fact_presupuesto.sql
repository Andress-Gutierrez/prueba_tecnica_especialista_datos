-- =============================================================================
-- Script   : 15_fact_presupuesto.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.2 dwh.fact_presupuesto)
-- =============================================================================
-- Descripción:
--   Crea el hecho dwh.fact_presupuesto (grano = 1 meta mensual al cruce).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
--   Sin índices, CHECK, INSERT ni seeds.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.fact_presupuesto (
    sk_presupuesto      BIGINT         NOT NULL,
    sk_tiempo           BIGINT         NOT NULL,
    sk_region           BIGINT         NOT NULL,
    sk_canal            BIGINT         NOT NULL,
    sk_categoria        BIGINT         NOT NULL,
    sk_unidad_gestion   BIGINT         NOT NULL,
    sk_jerarquia        BIGINT         NOT NULL,
    sk_aliado           BIGINT         NOT NULL,
    terminales          NUMERIC(20,4)  NOT NULL,
    tecnologia          NUMERIC(20,4)  NOT NULL,
    tyt                 NUMERIC(20,4)  NOT NULL,
    fecha_carga_dw      TIMESTAMP      NOT NULL,

    CONSTRAINT pk_fact_presupuesto
        PRIMARY KEY (sk_presupuesto),

    CONSTRAINT fk_fact_presupuesto_tiempo
        FOREIGN KEY (sk_tiempo) REFERENCES dwh.dim_tiempo (sk_tiempo),

    CONSTRAINT fk_fact_presupuesto_region
        FOREIGN KEY (sk_region) REFERENCES dwh.dim_region (sk_region),

    CONSTRAINT fk_fact_presupuesto_canal
        FOREIGN KEY (sk_canal) REFERENCES dwh.dim_canal (sk_canal),

    CONSTRAINT fk_fact_presupuesto_categoria
        FOREIGN KEY (sk_categoria) REFERENCES dwh.dim_categoria (sk_categoria),

    CONSTRAINT fk_fact_presupuesto_unidad_gestion
        FOREIGN KEY (sk_unidad_gestion) REFERENCES dwh.dim_unidad_gestion (sk_unidad_gestion),

    CONSTRAINT fk_fact_presupuesto_jerarquia
        FOREIGN KEY (sk_jerarquia) REFERENCES dwh.dim_jerarquia_comercial (sk_jerarquia),

    CONSTRAINT fk_fact_presupuesto_aliado
        FOREIGN KEY (sk_aliado) REFERENCES dwh.dim_aliado (sk_aliado)
);

COMMENT ON TABLE dwh.fact_presupuesto IS
    'Hecho de metas comerciales mensuales. Grano: 1 asignación de meta al cruce dimensional. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.fact_presupuesto.sk_presupuesto IS
    'SK';
COMMENT ON COLUMN dwh.fact_presupuesto.sk_tiempo IS
    'Periodo mes';
COMMENT ON COLUMN dwh.fact_presupuesto.sk_region IS
    'Región';
COMMENT ON COLUMN dwh.fact_presupuesto.sk_canal IS
    'Canal';
COMMENT ON COLUMN dwh.fact_presupuesto.sk_categoria IS
    'Categoría';
COMMENT ON COLUMN dwh.fact_presupuesto.sk_unidad_gestion IS
    'Unidad gestión';
COMMENT ON COLUMN dwh.fact_presupuesto.sk_jerarquia IS
    'Jerarquía';
COMMENT ON COLUMN dwh.fact_presupuesto.sk_aliado IS
    'Aliado';
COMMENT ON COLUMN dwh.fact_presupuesto.terminales IS
    'Medida';
COMMENT ON COLUMN dwh.fact_presupuesto.tecnologia IS
    'Medida';
COMMENT ON COLUMN dwh.fact_presupuesto.tyt IS
    'Medida (= terminales + tecnologia)';
COMMENT ON COLUMN dwh.fact_presupuesto.fecha_carga_dw IS
    'Auditoría ETL';
