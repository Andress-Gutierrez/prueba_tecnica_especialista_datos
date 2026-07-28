"""
Validaciones finales del Data Warehouse (Subfase 4.6).

Solo SELECT. Usa la conexión existente de ``repository.postgres``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from psycopg.rows import tuple_row

from repository.postgres import PostgresSettings, postgres_connection

DIMENSION_TABLES: tuple[str, ...] = (
    "dim_tiempo",
    "dim_region",
    "dim_canal",
    "dim_categoria",
    "dim_jerarquia_comercial",
    "dim_aliado",
    "dim_unidad_gestion",
    "dim_marca",
    "dim_vendedor",
    "dim_validez_venta",
    "dim_campana",
    "dim_segmento",
    "dim_tipo_contacto",
)

FACT_TABLES: tuple[str, ...] = (
    "fact_ventas",
    "fact_presupuesto",
    "fact_gestion_tmk",
)

# Dimensiones con miembro sk=0 (validez usa dominio 1–4, no sk=0).
SK0_DIMENSIONS: dict[str, str] = {
    "dim_tiempo": "sk_tiempo",
    "dim_region": "sk_region",
    "dim_canal": "sk_canal",
    "dim_categoria": "sk_categoria",
    "dim_jerarquia_comercial": "sk_jerarquia",
    "dim_aliado": "sk_aliado",
    "dim_unidad_gestion": "sk_unidad_gestion",
    "dim_marca": "sk_marca",
    "dim_vendedor": "sk_vendedor",
    "dim_campana": "sk_campana",
    "dim_segmento": "sk_segmento",
    "dim_tipo_contacto": "sk_tipo_contacto",
}

# FK esperadas por hecho (columna → dimensión.sk).
FACT_FK_CHECKS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "fact_ventas": (
        ("sk_tiempo", "dim_tiempo", "sk_tiempo"),
        ("sk_region", "dim_region", "sk_region"),
        ("sk_canal", "dim_canal", "sk_canal"),
        ("sk_categoria", "dim_categoria", "sk_categoria"),
        ("sk_jerarquia", "dim_jerarquia_comercial", "sk_jerarquia"),
        ("sk_aliado", "dim_aliado", "sk_aliado"),
        ("sk_marca", "dim_marca", "sk_marca"),
        ("sk_vendedor", "dim_vendedor", "sk_vendedor"),
        ("sk_validez", "dim_validez_venta", "sk_validez"),
    ),
    "fact_presupuesto": (
        ("sk_tiempo", "dim_tiempo", "sk_tiempo"),
        ("sk_region", "dim_region", "sk_region"),
        ("sk_canal", "dim_canal", "sk_canal"),
        ("sk_categoria", "dim_categoria", "sk_categoria"),
        ("sk_unidad_gestion", "dim_unidad_gestion", "sk_unidad_gestion"),
        ("sk_jerarquia", "dim_jerarquia_comercial", "sk_jerarquia"),
        ("sk_aliado", "dim_aliado", "sk_aliado"),
    ),
    "fact_gestion_tmk": (
        ("sk_tiempo", "dim_tiempo", "sk_tiempo"),
        ("sk_region", "dim_region", "sk_region"),
        ("sk_jerarquia", "dim_jerarquia_comercial", "sk_jerarquia"),
        ("sk_aliado", "dim_aliado", "sk_aliado"),
        ("sk_campana", "dim_campana", "sk_campana"),
        ("sk_segmento", "dim_segmento", "sk_segmento"),
        ("sk_tipo_contacto", "dim_tipo_contacto", "sk_tipo_contacto"),
    ),
}


@dataclass(frozen=True)
class ValidationCheck:
    """Resultado de un chequeo individual."""

    name: str
    ok: bool
    detail: str = ""


@dataclass
class ValidationReport:
    """Resumen de validación del DW."""

    checks: list[ValidationCheck] = field(default_factory=list)
    row_counts: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """True si todos los chequeos pasaron."""
        return all(c.ok for c in self.checks)

    @property
    def failed_count(self) -> int:
        """Cantidad de chequeos fallidos."""
        return sum(1 for c in self.checks if not c.ok)

    def summary(self) -> str:
        """Texto de resumen final de ejecución."""
        status = "OK" if self.ok else f"FALLIDA ({self.failed_count} error(es))"
        lines = [
            f"Validación DW: {status}",
            f"Chequeos: {len(self.checks)} | Fallidos: {self.failed_count}",
            "Conteos:",
        ]
        for table, count in sorted(self.row_counts.items()):
            lines.append(f"  - {table}: {count}")
        return "\n".join(lines)


def validate_data_warehouse(settings: PostgresSettings) -> ValidationReport:
    """
    Ejecuta las validaciones finales del Data Warehouse.

    Comprueba: existencia dims/hechos, conteos, integridad referencial,
    miembro sk=0 y resume el resultado.
    """
    report = ValidationReport()

    with postgres_connection(settings) as connection:
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.schemata "
                "WHERE schema_name = 'dwh'"
            )
            schema_ok = int(cursor.fetchone()[0]) == 1
            report.checks.append(
                ValidationCheck("Esquema dwh", schema_ok, f"presente={schema_ok}")
            )

            for table in DIMENSION_TABLES:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'dwh' AND table_name = %s",
                    (table,),
                )
                exists = int(cursor.fetchone()[0]) == 1
                report.checks.append(
                    ValidationCheck(f"Existe dimensión {table}", exists)
                )
                if exists:
                    cursor.execute(f"SELECT COUNT(*) FROM dwh.{table}")
                    report.row_counts[table] = int(cursor.fetchone()[0])

            for table in FACT_TABLES:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'dwh' AND table_name = %s",
                    (table,),
                )
                exists = int(cursor.fetchone()[0]) == 1
                report.checks.append(
                    ValidationCheck(f"Existe hecho {table}", exists)
                )
                if exists:
                    cursor.execute(f"SELECT COUNT(*) FROM dwh.{table}")
                    report.row_counts[table] = int(cursor.fetchone()[0])
                    report.checks.append(
                        ValidationCheck(
                            f"Conteo {table}",
                            True,
                            f"rows={report.row_counts[table]}",
                        )
                    )

            for table, sk_col in SK0_DIMENSIONS.items():
                cursor.execute(
                    f"SELECT COUNT(*) FROM dwh.{table} WHERE {sk_col} = 0"
                )
                n = int(cursor.fetchone()[0])
                report.checks.append(
                    ValidationCheck(
                        f"Miembro sk=0 en {table}",
                        n >= 1,
                        f"count={n}",
                    )
                )

            cursor.execute("SELECT COUNT(*) FROM dwh.dim_validez_venta")
            validez_n = int(cursor.fetchone()[0])
            report.checks.append(
                ValidationCheck(
                    "Dominio dim_validez_venta",
                    validez_n >= 4,
                    f"rows={validez_n}",
                )
            )

            # Integridad referencial: anti-joins por cada FK.
            for fact, fks in FACT_FK_CHECKS.items():
                if report.row_counts.get(fact, 0) == 0:
                    report.checks.append(
                        ValidationCheck(
                            f"Integridad referencial {fact}",
                            True,
                            "sin filas (OK vacío)",
                        )
                    )
                    continue
                orphans_total = 0
                for fk_col, dim_table, dim_sk in fks:
                    cursor.execute(
                        f"""
                        SELECT COUNT(*)
                        FROM dwh.{fact} f
                        LEFT JOIN dwh.{dim_table} d
                          ON f.{fk_col} = d.{dim_sk}
                        WHERE d.{dim_sk} IS NULL
                        """
                    )
                    orphans_total += int(cursor.fetchone()[0])
                report.checks.append(
                    ValidationCheck(
                        f"Integridad referencial {fact}",
                        orphans_total == 0,
                        f"orphans={orphans_total}",
                    )
                )

            # Regresión de diseño: fact_gestion_tmk sin sk_canal.
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = 'dwh' AND table_name = 'fact_gestion_tmk' "
                "AND column_name = 'sk_canal'"
            )
            has_canal = int(cursor.fetchone()[0]) > 0
            report.checks.append(
                ValidationCheck(
                    "fact_gestion_tmk sin sk_canal",
                    not has_canal,
                    f"sk_canal_presente={has_canal}",
                )
            )

    report.checks.append(
        ValidationCheck(
            "Resumen final de ejecución",
            report.ok,
            report.summary().replace("\n", " | "),
        )
    )
    return report
