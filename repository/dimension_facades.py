"""
Fachadas de persistencia dimensional (Subfase 4.4B.3).

Cada fachada delega en ``GenericDimensionRepository`` + su ``DimensionTableConfig``.
No duplica SQL ni altera ``DimTiempoRepository`` / motor genérico.
"""

from __future__ import annotations

import pandas as pd

from repository.dimension_configs import (
    DIM_ALIADO_CONFIG,
    DIM_CAMPANA_CONFIG,
    DIM_CANAL_CONFIG,
    DIM_CATEGORIA_CONFIG,
    DIM_JERARQUIA_COMERCIAL_CONFIG,
    DIM_MARCA_CONFIG,
    DIM_REGION_CONFIG,
    DIM_SEGMENTO_CONFIG,
    DIM_TIPO_CONTACTO_CONFIG,
    DIM_UNIDAD_GESTION_CONFIG,
    DIM_VALIDEZ_VENTA_CONFIG,
    DIM_VENDEDOR_CONFIG,
)
from repository.dimension_repository import (
    DimensionRepository,
    DimensionTableConfig,
    GenericDimensionRepository,
    PersistResult,
)
from repository.postgres import PostgresSettings


class ConfiguredDimensionRepository(DimensionRepository):
    """
    Fachada genérica: fija una config y delega en el motor aprobado.

    Parameters
    ----------
    settings:
        Credenciales PostgreSQL.
    config:
        Metadatos de la dimensión.
    """

    def __init__(
        self,
        settings: PostgresSettings,
        config: DimensionTableConfig,
    ) -> None:
        self._config = config
        self._inner = GenericDimensionRepository(settings, config)

    def persist_dimension(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """
        Persiste solo la dimensión de ``config``.

        Raises
        ------
        ValueError
            Si ``table_name`` no coincide con la configuración.
        """
        if table_name != self._config.logical_name:
            raise ValueError(
                f"{type(self).__name__} solo persiste "
                f"{self._config.logical_name!r}; recibido {table_name!r}."
            )
        return self._inner.persist_dimension(table_name, frame)


class DimRegionRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_region``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_REGION_CONFIG)


class DimCanalRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_canal``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_CANAL_CONFIG)


class DimCategoriaRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_categoria``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_CATEGORIA_CONFIG)


class DimJerarquiaComercialRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_jerarquia_comercial``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_JERARQUIA_COMERCIAL_CONFIG)


class DimAliadoRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_aliado``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_ALIADO_CONFIG)


class DimUnidadGestionRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_unidad_gestion``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_UNIDAD_GESTION_CONFIG)


class DimMarcaRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_marca``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_MARCA_CONFIG)


class DimVendedorRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_vendedor``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_VENDEDOR_CONFIG)


class DimValidezVentaRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_validez_venta``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_VALIDEZ_VENTA_CONFIG)


class DimCampanaRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_campana``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_CAMPANA_CONFIG)


class DimSegmentoRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_segmento``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_SEGMENTO_CONFIG)


class DimTipoContactoRepository(ConfiguredDimensionRepository):
    """Persistencia de ``dwh.dim_tipo_contacto``."""

    def __init__(self, settings: PostgresSettings) -> None:
        super().__init__(settings, DIM_TIPO_CONTACTO_CONFIG)


DIMENSION_FACADE_TYPES: dict[str, type[ConfiguredDimensionRepository]] = {
    "dim_region": DimRegionRepository,
    "dim_canal": DimCanalRepository,
    "dim_categoria": DimCategoriaRepository,
    "dim_jerarquia_comercial": DimJerarquiaComercialRepository,
    "dim_aliado": DimAliadoRepository,
    "dim_unidad_gestion": DimUnidadGestionRepository,
    "dim_marca": DimMarcaRepository,
    "dim_vendedor": DimVendedorRepository,
    "dim_validez_venta": DimValidezVentaRepository,
    "dim_campana": DimCampanaRepository,
    "dim_segmento": DimSegmentoRepository,
    "dim_tipo_contacto": DimTipoContactoRepository,
}


def build_dimension_repositories(
    settings: PostgresSettings,
) -> dict[str, DimensionRepository]:
    """
    Construye el mapa completo de repositorios dimensionales.

    Incluye ``DimTiempoRepository`` y las 12 fachadas 4.4B.3.
    """
    from repository.dimension_repository import DimTiempoRepository

    repositories: dict[str, DimensionRepository] = {
        "dim_tiempo": DimTiempoRepository(settings),
    }
    for logical_name, facade_cls in DIMENSION_FACADE_TYPES.items():
        repositories[logical_name] = facade_cls(settings)
    return repositories
