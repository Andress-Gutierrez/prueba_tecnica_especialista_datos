-- =============================================================================
-- Script   : 14_fact_ventas.sql
-- Proyecto : prueba_tecnica_especialista_datos
-- Fase     : 3 — Implementación PostgreSQL (Subfase 3.2 — DDL)
-- Fecha    : 2026-07-27
-- Autor    : Cursor
-- Fuente   : docs/modelo/04_Modelo_Fisico.md (§4.2 dwh.fact_ventas)
-- =============================================================================
-- Descripción:
--   Crea el hecho dwh.fact_ventas (grano = 1 evento de venta).
--   Base de datos: dwh_comercial. Esquema: dwh.
--   Idempotente: CREATE TABLE IF NOT EXISTS.
--   Sin índices, CHECK, INSERT ni seeds.
-- =============================================================================

CREATE TABLE IF NOT EXISTS dwh.fact_ventas (
    sk_venta          BIGINT         NOT NULL,
    sk_tiempo         BIGINT         NOT NULL,
    sk_region         BIGINT         NOT NULL,
    sk_canal          BIGINT         NOT NULL,
    sk_categoria      BIGINT         NOT NULL,
    sk_jerarquia      BIGINT         NOT NULL,
    sk_aliado         BIGINT         NOT NULL,
    sk_marca          BIGINT         NOT NULL,
    sk_vendedor       BIGINT         NOT NULL,
    sk_validez        BIGINT         NOT NULL,
    codigo_factura    VARCHAR(40)    NULL,
    valor_antes_iva   NUMERIC(18,2)  NOT NULL,
    cuotas            NUMERIC(8,2)   NULL,
    fecha_carga_dw    TIMESTAMP      NOT NULL,

    CONSTRAINT pk_fact_ventas
        PRIMARY KEY (sk_venta),

    CONSTRAINT fk_fact_ventas_tiempo
        FOREIGN KEY (sk_tiempo) REFERENCES dwh.dim_tiempo (sk_tiempo),

    CONSTRAINT fk_fact_ventas_region
        FOREIGN KEY (sk_region) REFERENCES dwh.dim_region (sk_region),

    CONSTRAINT fk_fact_ventas_canal
        FOREIGN KEY (sk_canal) REFERENCES dwh.dim_canal (sk_canal),

    CONSTRAINT fk_fact_ventas_categoria
        FOREIGN KEY (sk_categoria) REFERENCES dwh.dim_categoria (sk_categoria),

    CONSTRAINT fk_fact_ventas_jerarquia
        FOREIGN KEY (sk_jerarquia) REFERENCES dwh.dim_jerarquia_comercial (sk_jerarquia),

    CONSTRAINT fk_fact_ventas_aliado
        FOREIGN KEY (sk_aliado) REFERENCES dwh.dim_aliado (sk_aliado),

    CONSTRAINT fk_fact_ventas_marca
        FOREIGN KEY (sk_marca) REFERENCES dwh.dim_marca (sk_marca),

    CONSTRAINT fk_fact_ventas_vendedor
        FOREIGN KEY (sk_vendedor) REFERENCES dwh.dim_vendedor (sk_vendedor),

    CONSTRAINT fk_fact_ventas_validez
        FOREIGN KEY (sk_validez) REFERENCES dwh.dim_validez_venta (sk_validez)
);

COMMENT ON TABLE dwh.fact_ventas IS
    'Hecho de ventas comerciales (cierre). Grano: 1 evento/registro transaccional. Fuente: 04_Modelo_Fisico.md.';

COMMENT ON COLUMN dwh.fact_ventas.sk_venta IS
    'SK del evento (no es Código Factura)';
COMMENT ON COLUMN dwh.fact_ventas.sk_tiempo IS
    'Fecha venta';
COMMENT ON COLUMN dwh.fact_ventas.sk_region IS
    'Región';
COMMENT ON COLUMN dwh.fact_ventas.sk_canal IS
    'Canal';
COMMENT ON COLUMN dwh.fact_ventas.sk_categoria IS
    'Categoría';
COMMENT ON COLUMN dwh.fact_ventas.sk_jerarquia IS
    'Jerarquía';
COMMENT ON COLUMN dwh.fact_ventas.sk_aliado IS
    'Aliado';
COMMENT ON COLUMN dwh.fact_ventas.sk_marca IS
    'Marca';
COMMENT ON COLUMN dwh.fact_ventas.sk_vendedor IS
    'Vendedor';
COMMENT ON COLUMN dwh.fact_ventas.sk_validez IS
    'Validez Reto 1';
COMMENT ON COLUMN dwh.fact_ventas.codigo_factura IS
    'Degenerado; puede ser NULL';
COMMENT ON COLUMN dwh.fact_ventas.valor_antes_iva IS
    'Medida';
COMMENT ON COLUMN dwh.fact_ventas.cuotas IS
    'Medida opcional';
COMMENT ON COLUMN dwh.fact_ventas.fecha_carga_dw IS
    'Auditoría ETL';
