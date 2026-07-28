"""
Fachadas de persistencia de hechos (Subfase 4.5A).

Cada fachada fija metadatos de tabla y delega en ``PostgresFactRepository``.
"""

from __future__ import annotations

import pandas as pd

from repository.fact_repository import FactRepository, PersistResult, PostgresFactRepository
from repository.postgres import PostgresSettings

_FACT_VENTAS_COLUMNS: tuple[str, ...] = (
    "sk_venta",
    "sk_tiempo",
    "sk_region",
    "sk_canal",
    "sk_categoria",
    "sk_jerarquia",
    "sk_aliado",
    "sk_marca",
    "sk_vendedor",
    "sk_validez",
    "codigo_factura",
    "valor_antes_iva",
    "cuotas",
    "fecha_carga_dw",
)

_FACT_PRESUPUESTO_COLUMNS: tuple[str, ...] = (
    "sk_presupuesto",
    "sk_tiempo",
    "sk_region",
    "sk_canal",
    "sk_categoria",
    "sk_unidad_gestion",
    "sk_jerarquia",
    "sk_aliado",
    "terminales",
    "tecnologia",
    "tyt",
    "fecha_carga_dw",
)

_FACT_GESTION_TMK_COLUMNS: tuple[str, ...] = (
    "sk_gestion",
    "sk_tiempo",
    "sk_region",
    "sk_jerarquia",
    "sk_aliado",
    "sk_campana",
    "sk_segmento",
    "sk_tipo_contacto",
    "cantidad",
    "intentos",
    "fecha_carga_dw",
)


class FactVentasRepository(FactRepository):
    """Persistencia de ``dwh.fact_ventas``."""

    def __init__(self, settings: PostgresSettings) -> None:
        self._inner = PostgresFactRepository(
            settings,
            logical_name="fact_ventas",
            table="fact_ventas",
            sk_column="sk_venta",
            columns=_FACT_VENTAS_COLUMNS,
            required_columns=(
                "sk_tiempo",
                "sk_region",
                "sk_canal",
                "sk_categoria",
                "sk_jerarquia",
                "sk_aliado",
                "sk_marca",
                "sk_vendedor",
                "sk_validez",
                "valor_antes_iva",
            ),
        )

    def persist_fact(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """Persiste únicamente ``fact_ventas``."""
        return self._inner.persist_fact(table_name, frame)


class FactPresupuestoRepository(FactRepository):
    """Persistencia de ``dwh.fact_presupuesto``."""

    def __init__(self, settings: PostgresSettings) -> None:
        self._inner = PostgresFactRepository(
            settings,
            logical_name="fact_presupuesto",
            table="fact_presupuesto",
            sk_column="sk_presupuesto",
            columns=_FACT_PRESUPUESTO_COLUMNS,
            required_columns=(
                "sk_tiempo",
                "sk_region",
                "sk_canal",
                "sk_categoria",
                "sk_unidad_gestion",
                "sk_jerarquia",
                "sk_aliado",
                "terminales",
                "tecnologia",
                "tyt",
            ),
        )

    def persist_fact(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """Persiste únicamente ``fact_presupuesto``."""
        return self._inner.persist_fact(table_name, frame)


class FactGestionTmkRepository(FactRepository):
    """Persistencia de ``dwh.fact_gestion_tmk``."""

    def __init__(self, settings: PostgresSettings) -> None:
        self._inner = PostgresFactRepository(
            settings,
            logical_name="fact_gestion_tmk",
            table="fact_gestion_tmk",
            sk_column="sk_gestion",
            columns=_FACT_GESTION_TMK_COLUMNS,
            required_columns=(
                "sk_tiempo",
                "sk_region",
                "sk_jerarquia",
                "sk_aliado",
                "sk_campana",
                "sk_segmento",
                "sk_tipo_contacto",
                "cantidad",
            ),
        )

    def persist_fact(
        self,
        table_name: str,
        frame: pd.DataFrame,
    ) -> PersistResult:
        """Persiste únicamente ``fact_gestion_tmk``."""
        return self._inner.persist_fact(table_name, frame)


FACT_FACADE_TYPES: dict[str, type[FactRepository]] = {
    "fact_ventas": FactVentasRepository,
    "fact_presupuesto": FactPresupuestoRepository,
    "fact_gestion_tmk": FactGestionTmkRepository,
}


def build_fact_repositories(
    settings: PostgresSettings,
) -> dict[str, FactRepository]:
    """Construye el mapa de repositorios de hechos (orden oficial)."""
    return {
        name: facade_cls(settings)
        for name, facade_cls in FACT_FACADE_TYPES.items()
    }
