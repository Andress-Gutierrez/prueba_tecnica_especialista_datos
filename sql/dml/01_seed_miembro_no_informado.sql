INSERT INTO dwh.dim_tiempo (
    sk_tiempo, fecha, anio, mes, dia, periodo_yyyymm,
    nombre_mes, dia_semana, es_dia_habil, es_festivo_co, es_fin_semana
) VALUES (
    0, NULL, 0, 1, NULL, 0,
    'No informado', NULL, FALSE, FALSE, NULL
)
ON CONFLICT (sk_tiempo) DO NOTHING;

INSERT INTO dwh.dim_region (
    sk_region, region_nk, nombre_region, es_sin_region
) VALUES (
    0, 'NO_INFORMADO', 'No informado', TRUE
)
ON CONFLICT (sk_region) DO NOTHING;

INSERT INTO dwh.dim_canal (
    sk_canal, canal, canal2, sub_canal
) VALUES (
    0, 'NO_INFORMADO', NULL, NULL
)
ON CONFLICT (sk_canal) DO NOTHING;

INSERT INTO dwh.dim_categoria (
    sk_categoria, categoria_nk, nombre_categoria
) VALUES (
    0, 'NO_INFORMADO', 'No informado'
)
ON CONFLICT (sk_categoria) DO NOTHING;

INSERT INTO dwh.dim_jerarquia_comercial (
    sk_jerarquia, gerente, jefe, especialista
) VALUES (
    0, 'No informado', 'No informado', 'No informado'
)
ON CONFLICT (sk_jerarquia) DO NOTHING;

INSERT INTO dwh.dim_aliado (
    sk_aliado, aliado_nk, nombre_aliado
) VALUES (
    0, 'NO_INFORMADO', 'No informado'
)
ON CONFLICT (sk_aliado) DO NOTHING;

INSERT INTO dwh.dim_unidad_gestion (
    sk_unidad_gestion, unidad_gestion_nk, nombre_unidad_gestion
) VALUES (
    0, 'NO_INFORMADO', 'No informado'
)
ON CONFLICT (sk_unidad_gestion) DO NOTHING;

INSERT INTO dwh.dim_marca (
    sk_marca, marca_nk, nombre_marca
) VALUES (
    0, 'NO_INFORMADO', 'No informado'
)
ON CONFLICT (sk_marca) DO NOTHING;

INSERT INTO dwh.dim_vendedor (
    sk_vendedor, cedula_vendedor_nk, nombre_vendedor
) VALUES (
    0, 'NO_INFORMADO', 'No informado'
)
ON CONFLICT (sk_vendedor) DO NOTHING;

INSERT INTO dwh.dim_campana (
    sk_campana, campana_nk, nombre_campana
) VALUES (
    0, 'NO_INFORMADO', 'No informado'
)
ON CONFLICT (sk_campana) DO NOTHING;

INSERT INTO dwh.dim_segmento (
    sk_segmento, segmento_nk, segmento_normalizado, nombre_segmento
) VALUES (
    0, 'NO_INFORMADO', 'No informado', 'No informado'
)
ON CONFLICT (sk_segmento) DO NOTHING;

INSERT INTO dwh.dim_tipo_contacto (
    sk_tipo_contacto, tipo_contacto, detalle_contacto, nombre_tipo_contacto
) VALUES (
    0, 'NO_INFORMADO', NULL, 'No informado'
)
ON CONFLICT (sk_tipo_contacto) DO NOTHING;
