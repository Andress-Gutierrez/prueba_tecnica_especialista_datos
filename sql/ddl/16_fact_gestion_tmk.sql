-- =============================================================================
-- Script   : 16_fact_gestion_tmk.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.2 dwh.fact_gestion_tmk)
-- =============================================================================
-- Descripción:
--   Crea el hecho dwh.fact_gestion_tmk (grano = 1 agregado tipificado).
--   Sin sk_canal (filtro TMK Outbound es regla de negocio, no atributo origen).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
--   Sin índices, CHECK, INSERT ni seeds.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.fact_gestion_tmk (
    sk_gestion          BIGINT         NOT NULL,
    sk_tiempo           BIGINT         NOT NULL,
    sk_region           BIGINT         NOT NULL,
    sk_jerarquia        BIGINT         NOT NULL,
    sk_aliado           BIGINT         NOT NULL,
    sk_campana          BIGINT         NOT NULL,
    sk_segmento         BIGINT         NOT NULL,
    sk_tipo_contacto    BIGINT         NOT NULL,
    cantidad            BIGINT         NOT NULL,
    intentos            NUMERIC(18,2)  NULL,
    fecha_carga_dw      TIMESTAMP      NOT NULL,

    CONSTRAINT pk_fact_gestion_tmk
        PRIMARY KEY (sk_gestion),

    CONSTRAINT fk_fact_gestion_tmk_tiempo
        FOREIGN KEY (sk_tiempo) REFERENCES dwh.dim_tiempo (sk_tiempo),

    CONSTRAINT fk_fact_gestion_tmk_region
        FOREIGN KEY (sk_region) REFERENCES dwh.dim_region (sk_region),

    CONSTRAINT fk_fact_gestion_tmk_jerarquia
        FOREIGN KEY (sk_jerarquia) REFERENCES dwh.dim_jerarquia_comercial (sk_jerarquia),

    CONSTRAINT fk_fact_gestion_tmk_aliado
        FOREIGN KEY (sk_aliado) REFERENCES dwh.dim_aliado (sk_aliado),

    CONSTRAINT fk_fact_gestion_tmk_campana
        FOREIGN KEY (sk_campana) REFERENCES dwh.dim_campana (sk_campana),

    CONSTRAINT fk_fact_gestion_tmk_segmento
        FOREIGN KEY (sk_segmento) REFERENCES dwh.dim_segmento (sk_segmento),

    CONSTRAINT fk_fact_gestion_tmk_tipo_contacto
        FOREIGN KEY (sk_tipo_contacto) REFERENCES dwh.dim_tipo_contacto (sk_tipo_contacto)
);

COMMENT ON TABLE dwh.fact_gestion_tmk IS
    'Hecho de gestión TMK Outbound. Grano: 1 agregado tipificado (cantidad/intentos). Sin sk_canal. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_gestion IS
    'SK';
COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_tiempo IS
    'Fecha gestión / periodo';
COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_region IS
    'Región';
COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_jerarquia IS
    'Puede ser "No informado"';
COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_aliado IS
    'Aliado';
COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_campana IS
    'Campaña';
COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_segmento IS
    'Segmento';
COMMENT ON COLUMN dwh.fact_gestion_tmk.sk_tipo_contacto IS
    'Tipificación';
COMMENT ON COLUMN dwh.fact_gestion_tmk.cantidad IS
    'Medida volumen';
COMMENT ON COLUMN dwh.fact_gestion_tmk.intentos IS
    'Medida esfuerzo';
COMMENT ON COLUMN dwh.fact_gestion_tmk.fecha_carga_dw IS
    'Auditoría ETL';
