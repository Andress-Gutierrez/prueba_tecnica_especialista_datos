CREATE INDEX IF NOT EXISTS ix_fact_ventas_tiempo ON dwh.fact_ventas (sk_tiempo);
CREATE INDEX IF NOT EXISTS ix_fact_ventas_validez ON dwh.fact_ventas (sk_validez);
CREATE INDEX IF NOT EXISTS ix_fact_ventas_region_aliado ON dwh.fact_ventas (sk_region, sk_aliado);
CREATE INDEX IF NOT EXISTS ix_fact_ventas_jerarquia ON dwh.fact_ventas (sk_jerarquia);
