"""
Reglas de negocio ETL (Subfase 4.3B).

Fuente oficial: ``docs/arquitectura/02_Catalogo_Reglas_Negocio.md``.
Solo se implementan reglas con estado Lista según el alcance de cada subfase.
"""

from etl.business_rules.gestion_rules import apply_gestion_rules
from etl.business_rules.presupuesto_rules import apply_presupuesto_rules
from etl.business_rules.ventas_rules import apply_ventas_rules

__all__ = [
    "apply_ventas_rules",
    "apply_presupuesto_rules",
    "apply_gestion_rules",
]
