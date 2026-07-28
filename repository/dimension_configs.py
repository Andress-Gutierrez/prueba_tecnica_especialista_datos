"""
Configuraciones ``DimensionTableConfig`` de dimensiones (excepto dim_tiempo).

Subfase 4.4B.3: solo declaración de metadatos. Sin SQL ni lógica de persistencia.
``DIM_TIEMPO_CONFIG`` permanece en ``dimension_repository.py``.
"""

from __future__ import annotations

from repository.dimension_repository import DimensionTableConfig

DIM_REGION_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_region",
    schema="dwh",
    table="dim_region",
    sk_column="sk_region",
    natural_key_columns=("region_nk",),
    attribute_columns=("region_nk", "nombre_region", "es_sin_region"),
    update_columns=("nombre_region", "es_sin_region"),
    required_columns=("region_nk", "nombre_region", "es_sin_region"),
    bool_columns=("es_sin_region",),
)

DIM_CANAL_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_canal",
    schema="dwh",
    table="dim_canal",
    sk_column="sk_canal",
    natural_key_columns=("canal", "canal2", "sub_canal"),
    attribute_columns=("canal", "canal2", "sub_canal"),
    update_columns=("canal", "canal2", "sub_canal"),
    required_columns=("canal",),
    optional_str_columns=("canal2", "sub_canal"),
)

DIM_CATEGORIA_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_categoria",
    schema="dwh",
    table="dim_categoria",
    sk_column="sk_categoria",
    natural_key_columns=("categoria_nk",),
    attribute_columns=("categoria_nk", "nombre_categoria"),
    update_columns=("nombre_categoria",),
    required_columns=("categoria_nk", "nombre_categoria"),
)

DIM_JERARQUIA_COMERCIAL_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_jerarquia_comercial",
    schema="dwh",
    table="dim_jerarquia_comercial",
    sk_column="sk_jerarquia",
    natural_key_columns=("gerente", "jefe", "especialista"),
    attribute_columns=("gerente", "jefe", "especialista"),
    update_columns=("gerente", "jefe", "especialista"),
    required_columns=("gerente", "jefe", "especialista"),
    optional_str_columns=("gerente", "jefe", "especialista"),
)

DIM_ALIADO_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_aliado",
    schema="dwh",
    table="dim_aliado",
    sk_column="sk_aliado",
    natural_key_columns=("aliado_nk",),
    attribute_columns=("aliado_nk", "nombre_aliado"),
    update_columns=("nombre_aliado",),
    required_columns=("aliado_nk", "nombre_aliado"),
)

DIM_UNIDAD_GESTION_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_unidad_gestion",
    schema="dwh",
    table="dim_unidad_gestion",
    sk_column="sk_unidad_gestion",
    natural_key_columns=("unidad_gestion_nk",),
    attribute_columns=("unidad_gestion_nk", "nombre_unidad_gestion"),
    update_columns=("nombre_unidad_gestion",),
    required_columns=("unidad_gestion_nk", "nombre_unidad_gestion"),
)

DIM_MARCA_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_marca",
    schema="dwh",
    table="dim_marca",
    sk_column="sk_marca",
    natural_key_columns=("marca_nk",),
    attribute_columns=("marca_nk", "nombre_marca"),
    update_columns=("nombre_marca",),
    required_columns=("marca_nk", "nombre_marca"),
)

DIM_VENDEDOR_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_vendedor",
    schema="dwh",
    table="dim_vendedor",
    sk_column="sk_vendedor",
    natural_key_columns=("cedula_vendedor_nk",),
    attribute_columns=("cedula_vendedor_nk", "nombre_vendedor"),
    update_columns=("nombre_vendedor",),
    required_columns=("cedula_vendedor_nk",),
    optional_str_columns=("nombre_vendedor",),
)

DIM_VALIDEZ_VENTA_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_validez_venta",
    schema="dwh",
    table="dim_validez_venta",
    sk_column="sk_validez",
    natural_key_columns=("tiene_factura", "tiene_nota_credito"),
    attribute_columns=(
        "tiene_factura",
        "tiene_nota_credito",
        "es_venta_valida",
        "descripcion",
    ),
    update_columns=("es_venta_valida", "descripcion"),
    required_columns=(
        "tiene_factura",
        "tiene_nota_credito",
        "es_venta_valida",
        "descripcion",
    ),
    bool_columns=("tiene_factura", "tiene_nota_credito", "es_venta_valida"),
)

DIM_CAMPANA_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_campana",
    schema="dwh",
    table="dim_campana",
    sk_column="sk_campana",
    natural_key_columns=("campana_nk",),
    attribute_columns=("campana_nk", "nombre_campana"),
    update_columns=("nombre_campana",),
    required_columns=("campana_nk", "nombre_campana"),
)

DIM_SEGMENTO_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_segmento",
    schema="dwh",
    table="dim_segmento",
    sk_column="sk_segmento",
    natural_key_columns=("segmento_nk",),
    attribute_columns=("segmento_nk", "segmento_normalizado", "nombre_segmento"),
    update_columns=("segmento_normalizado", "nombre_segmento"),
    required_columns=("segmento_nk", "segmento_normalizado", "nombre_segmento"),
)

DIM_TIPO_CONTACTO_CONFIG: DimensionTableConfig = DimensionTableConfig(
    logical_name="dim_tipo_contacto",
    schema="dwh",
    table="dim_tipo_contacto",
    sk_column="sk_tipo_contacto",
    natural_key_columns=("tipo_contacto", "detalle_contacto"),
    attribute_columns=("tipo_contacto", "detalle_contacto", "nombre_tipo_contacto"),
    update_columns=("nombre_tipo_contacto",),
    required_columns=("tipo_contacto", "nombre_tipo_contacto"),
    optional_str_columns=("detalle_contacto",),
)

# Registro de configs 4.4B.3 (sin dim_tiempo).
DIMENSION_CONFIGS_4_4B3: dict[str, DimensionTableConfig] = {
    cfg.logical_name: cfg
    for cfg in (
        DIM_REGION_CONFIG,
        DIM_CANAL_CONFIG,
        DIM_CATEGORIA_CONFIG,
        DIM_JERARQUIA_COMERCIAL_CONFIG,
        DIM_ALIADO_CONFIG,
        DIM_UNIDAD_GESTION_CONFIG,
        DIM_MARCA_CONFIG,
        DIM_VENDEDOR_CONFIG,
        DIM_VALIDEZ_VENTA_CONFIG,
        DIM_CAMPANA_CONFIG,
        DIM_SEGMENTO_CONFIG,
        DIM_TIPO_CONTACTO_CONFIG,
    )
}
