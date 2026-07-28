CREATE INDEX IF NOT EXISTS ix_fact_presupuesto_tiempo ON dwh.fact_presupuesto (sk_tiempo);
CREATE INDEX IF NOT EXISTS ix_fact_presupuesto_cruce ON dwh.fact_presupuesto (sk_region, sk_aliado, sk_jerarquia);
