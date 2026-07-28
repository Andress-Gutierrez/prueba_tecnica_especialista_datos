"""Transformaciones técnicas específicas por dataset (Subfase 4.2B)."""

from etl.transform.datasets.gestion_tmk import transform_gestion_tmk
from etl.transform.datasets.presupuesto import transform_presupuesto
from etl.transform.datasets.ventas import transform_ventas

__all__ = [
    "transform_ventas",
    "transform_presupuesto",
    "transform_gestion_tmk",
]
