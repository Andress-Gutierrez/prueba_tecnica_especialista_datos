CREATE INDEX IF NOT EXISTS ix_fact_gestion_tiempo ON dwh.fact_gestion_tmk (sk_tiempo);
CREATE INDEX IF NOT EXISTS ix_fact_gestion_campana_aliado ON dwh.fact_gestion_tmk (sk_campana, sk_aliado);
CREATE INDEX IF NOT EXISTS ix_fact_gestion_tipo ON dwh.fact_gestion_tmk (sk_tipo_contacto);
