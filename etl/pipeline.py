"""
Orquestación del pipeline ETL completo (Subfase 4.6).

Flujo: Extract → Transform → Business Rules → Load → Validación.
No modifica capas congeladas; solo las invoca.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import pandas as pd
from psycopg.rows import tuple_row

from etl.business_rules import (
    apply_gestion_rules,
    apply_presupuesto_rules,
    apply_ventas_rules,
)
from etl.extract.extractor import extract_all_sources
from etl.load.loader import LoadReport, run_load
from etl.transform.datasets.gestion_tmk import transform_gestion_tmk
from etl.transform.datasets.presupuesto import transform_presupuesto
from etl.transform.datasets.ventas import transform_ventas
from etl.utils.logger import get_logger
from etl.validation import ValidationReport, validate_data_warehouse
from repository.dimension_facades import build_dimension_repositories
from repository.fact_facades import build_fact_repositories
from repository.postgres import PostgresSettings, postgres_connection

logger = get_logger("pipeline")

_SEED_STATEMENTS: tuple[str, ...] = (
    """
    INSERT INTO dwh.dim_tiempo (
        sk_tiempo, fecha, anio, mes, dia, periodo_yyyymm,
        nombre_mes, dia_semana, es_dia_habil, es_festivo_co, es_fin_semana
    ) VALUES (0, NULL, 0, 1, NULL, 0, 'No informado', NULL, FALSE, FALSE, NULL)
    ON CONFLICT (sk_tiempo) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_region (sk_region, region_nk, nombre_region, es_sin_region)
    VALUES (0, 'NO_INFORMADO', 'No informado', TRUE)
    ON CONFLICT (sk_region) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_canal (sk_canal, canal, canal2, sub_canal)
    VALUES (0, 'NO_INFORMADO', NULL, NULL)
    ON CONFLICT (sk_canal) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_categoria (sk_categoria, categoria_nk, nombre_categoria)
    VALUES (0, 'NO_INFORMADO', 'No informado')
    ON CONFLICT (sk_categoria) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_jerarquia_comercial (sk_jerarquia, gerente, jefe, especialista)
    VALUES (0, 'No informado', 'No informado', 'No informado')
    ON CONFLICT (sk_jerarquia) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_aliado (sk_aliado, aliado_nk, nombre_aliado)
    VALUES (0, 'NO_INFORMADO', 'No informado')
    ON CONFLICT (sk_aliado) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_unidad_gestion (
        sk_unidad_gestion, unidad_gestion_nk, nombre_unidad_gestion
    ) VALUES (0, 'NO_INFORMADO', 'No informado')
    ON CONFLICT (sk_unidad_gestion) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_marca (sk_marca, marca_nk, nombre_marca)
    VALUES (0, 'NO_INFORMADO', 'No informado')
    ON CONFLICT (sk_marca) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_vendedor (sk_vendedor, cedula_vendedor_nk, nombre_vendedor)
    VALUES (0, 'NO_INFORMADO', 'No informado')
    ON CONFLICT (sk_vendedor) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_campana (sk_campana, campana_nk, nombre_campana)
    VALUES (0, 'NO_INFORMADO', 'No informado')
    ON CONFLICT (sk_campana) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_segmento (
        sk_segmento, segmento_nk, segmento_normalizado, nombre_segmento
    ) VALUES (0, 'NO_INFORMADO', 'No informado', 'No informado')
    ON CONFLICT (sk_segmento) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_tipo_contacto (
        sk_tipo_contacto, tipo_contacto, detalle_contacto, nombre_tipo_contacto
    ) VALUES (0, 'NO_INFORMADO', NULL, 'No informado')
    ON CONFLICT (sk_tipo_contacto) DO NOTHING
    """,
    """
    INSERT INTO dwh.dim_validez_venta (
        sk_validez, tiene_factura, tiene_nota_credito, es_venta_valida, descripcion
    ) VALUES
        (1, TRUE, FALSE, TRUE, 'Venta valida'),
        (2, FALSE, FALSE, FALSE, 'Sin factura'),
        (3, TRUE, TRUE, FALSE, 'Con nota credito'),
        (4, FALSE, TRUE, FALSE, 'Sin factura con nota credito')
    ON CONFLICT (sk_validez) DO NOTHING
    """,
)


@dataclass
class StageCounts:
    """Conteos por etapa del pipeline."""

    extract: dict[str, int] = field(default_factory=dict)
    transform: dict[str, int] = field(default_factory=dict)
    business_rules: dict[str, int] = field(default_factory=dict)
    load_dimensions: dict[str, str] = field(default_factory=dict)
    load_facts: dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Resultado de una corrida ETL + validación."""

    stage_counts: StageCounts
    load_report: LoadReport | None
    validation: ValidationReport

    def summary(self) -> str:
        """Resumen final de ejecución del pipeline."""
        lines = [
            "=== Resumen pipeline ETL (4.6) ===",
            f"Extract: {self.stage_counts.extract}",
            f"Transform: {self.stage_counts.transform}",
            f"Business Rules: {self.stage_counts.business_rules}",
            f"Load dims: {self.stage_counts.load_dimensions}",
            f"Load facts: {self.stage_counts.load_facts}",
            "",
            self.validation.summary(),
        ]
        return "\n".join(lines)


def ensure_seeds(settings: PostgresSettings) -> None:
    """Garantiza seeds sk=0 y dominio de validez (idempotente)."""
    with postgres_connection(settings) as connection:
        with connection.cursor() as cursor:
            for statement in _SEED_STATEMENTS:
                cursor.execute(statement)


def run_etl_pipeline(
    settings: PostgresSettings,
    *,
    max_rows: int | None = None,
) -> PipelineResult:
    """
    Ejecuta Extract → Transform → Business Rules → Load → Validación.

    Parameters
    ----------
    settings:
        Conexión PostgreSQL.
    max_rows:
        Límite opcional por fuente tras extract (integración). ``None`` = completo.
    """
    counts = StageCounts()
    started = perf_counter()
    logger.info("Inicio del ETL | max_rows=%s", max_rows)

    try:
        _assert_official_calendar_loaded(settings)

        # 1) Extract
        logger.info("Inicio etapa Extract")
        raw = extract_all_sources()
        if max_rows is not None:
            raw = {k: v.head(max_rows).copy() for k, v in raw.items()}
        counts.extract = {k: int(len(v)) for k, v in raw.items()}
        logger.info("Fin etapa Extract | registros=%s", counts.extract)

        # 2) Transform
        logger.info("Inicio etapa Transform")
        transformed = {
            "ventas": transform_ventas(raw["ventas"]),
            "presupuesto": transform_presupuesto(raw["presupuesto"]),
            "registros": transform_gestion_tmk(raw["registros"]),
        }
        counts.transform = {k: int(len(v)) for k, v in transformed.items()}
        logger.info("Fin etapa Transform | registros=%s", counts.transform)

        # 3) Business Rules
        logger.info("Inicio etapa Business Rules")
        dias_habiles_por_periodo = _load_dias_habiles_por_periodo(settings)
        ruled = {
            "ventas": apply_ventas_rules(transformed["ventas"]),
            "presupuesto": apply_presupuesto_rules(
                transformed["presupuesto"],
                dias_habiles_por_periodo=dias_habiles_por_periodo,
            ),
            "registros": apply_gestion_rules(transformed["registros"]),
        }
        counts.business_rules = {k: int(len(v)) for k, v in ruled.items()}
        logger.info(
            "Fin etapa Business Rules | registros=%s",
            counts.business_rules,
        )

        # 4) Load
        logger.info("Inicio etapa Load")
        ensure_seeds(settings)
        dim_frames = _build_dimension_frames(ruled)
        dim_repos = build_dimension_repositories(settings)
        fact_repos = build_fact_repositories(settings)

        # Carga dims primero (hechos vacíos en esta pasada intermedia).
        load_dims_only = run_load(
            dimension_repositories=dim_repos,
            fact_repositories=fact_repos,
            dimension_frames=dim_frames,
            fact_frames={},
        )
        counts.load_dimensions = {
            k: v.detail for k, v in load_dims_only.dimensions.items()
        }

        fact_frames = _build_fact_frames(settings, ruled)
        load_report = run_load(
            dimension_repositories=dim_repos,
            fact_repositories=fact_repos,
            dimension_frames={},
            fact_frames=fact_frames,
        )
        counts.load_facts = {k: v.detail for k, v in load_report.facts.items()}
        logger.info(
            "Fin etapa Load | dims=%s | facts=%s",
            counts.load_dimensions,
            counts.load_facts,
        )

        # 5) Validación
        logger.info("Inicio etapa Validation")
        validation = validate_data_warehouse(settings)
        logger.info(
            "Fin etapa Validation | ok=%s | chequeos=%s | fallidos=%s",
            validation.ok,
            len(validation.checks),
            sum(1 for c in validation.checks if not c.ok),
        )

        result = PipelineResult(
            stage_counts=counts,
            load_report=load_report,
            validation=validation,
        )
        elapsed = perf_counter() - started
        logger.info("Resumen final | %s", result.summary().replace("\n", " | "))
        logger.info("Duración total de la ejecución: %.2f s", elapsed)
        logger.info("Fin del ETL | ok=%s", validation.ok)
        return result
    except Exception:
        elapsed = perf_counter() - started
        logger.exception(
            "Error en pipeline ETL tras %.2f s",
            elapsed,
        )
        raise


def _assert_official_calendar_loaded(settings: PostgresSettings) -> None:
    """
    Verifica existencia de calendario oficial previo al ETL comercial.

    Requisito operativo: el calendario debe poblarse antes del extract.
    """
    with postgres_connection(settings) as connection:
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dwh.dim_tiempo
                WHERE fecha IS NOT NULL
                """
            )
            total = int(cursor.fetchone()[0])

    if total <= 0:
        message = (
            "No existe un calendario oficial cargado. "
            "Ejecute primero calendar_seed_dag."
        )
        logger.error(message)
        raise RuntimeError(message)


def _load_dias_habiles_por_periodo(
    settings: PostgresSettings,
) -> dict[int, int]:
    """
    Lee conteo de días hábiles por periodo desde ``dwh.dim_tiempo``.

    Única fuente oficial del calendario corporativo (``es_habil``).
    """
    query = """
        SELECT periodo_yyyymm, COUNT(*)::int AS dias_habiles
        FROM dwh.dim_tiempo
        WHERE fecha IS NOT NULL
          AND es_habil IS TRUE
        GROUP BY periodo_yyyymm
    """
    mapping: dict[int, int] = {}
    with postgres_connection(settings) as connection:
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(query)
            for periodo, dias in cursor.fetchall():
                mapping[int(periodo)] = int(dias)
    return mapping


def run_pipeline() -> PipelineResult:
    """
    Punto de entrada público del pipeline para orquestación (p. ej. Airflow).

    Carga la configuración desde variables de entorno y ejecuta el ETL
    completo sin parámetros adicionales. Propaga excepciones y convierte
    una validación DW fallida en error explícito.
    """
    settings = PostgresSettings.from_env()
    result = run_etl_pipeline(settings)
    if not result.validation.ok:
        raise RuntimeError(result.validation.summary())
    return result


def _norm_text(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def _build_dimension_frames(
    ruled: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Construye DataFrames de dimensiones a partir de fuentes gobernadas."""
    ventas = ruled["ventas"]
    presupuesto = ruled["presupuesto"]
    registros = ruled["registros"]

    dim_frames: dict[str, pd.DataFrame] = {}

    # dim_tiempo NO se construye aquí: la única fuente oficial es calendar_seed_dag.

    regions = set()
    for col, df in (
        ("region_comercial", ventas),
        ("region", presupuesto),
        ("division_comercial", registros),
    ):
        if col in df.columns:
            regions.update(_norm_text(v) for v in df[col].unique())
    regions.discard(None)
    if regions:
        dim_frames["dim_region"] = pd.DataFrame(
            [
                {
                    "region_nk": r,
                    "nombre_region": r,
                    "es_sin_region": "SIN" in r.upper(),
                }
                for r in sorted(regions)
            ]
        )

    canal_rows = []
    seen_canal: set[tuple[str | None, str | None, str | None]] = set()
    for df, c1, c2, c3 in (
        (ventas, "canal", "canal2", None),
        (presupuesto, "canal", "canal2", "sub_canal"),
    ):
        cols = [c for c in (c1, c2, c3) if c and c in df.columns]
        if not cols:
            continue
        for _, row in df[cols].drop_duplicates().iterrows():
            key = (
                _norm_text(row.get(c1)) if c1 else None,
                _norm_text(row.get(c2)) if c2 else None,
                _norm_text(row.get(c3)) if c3 else None,
            )
            if key[0] is None or key in seen_canal:
                continue
            seen_canal.add(key)
            canal_rows.append(
                {"canal": key[0], "canal2": key[1], "sub_canal": key[2]}
            )
    if canal_rows:
        dim_frames["dim_canal"] = pd.DataFrame(canal_rows)

    categorias = set()
    for df in (ventas, presupuesto):
        if "categoria" in df.columns:
            categorias.update(_norm_text(v) for v in df["categoria"].unique())
    categorias.discard(None)
    if categorias:
        dim_frames["dim_categoria"] = pd.DataFrame(
            [
                {"categoria_nk": c, "nombre_categoria": c}
                for c in sorted(categorias)
            ]
        )

    jer_rows = []
    seen_jer: set[tuple[str | None, str | None, str | None]] = set()
    for df, g, j, e in (
        (ventas, "gv_gerente_area", "gv_jefe_1_canal_regional", "gv_especialista"),
        (presupuesto, "gerente", "jefe", "especialista"),
        (registros, "gerente", "jefe", "especialista"),
    ):
        cols = [c for c in (g, j, e) if c in df.columns]
        if len(cols) < 1:
            continue
        subset = df.reindex(columns=[g, j, e])
        for _, row in subset.drop_duplicates().iterrows():
            key = (_norm_text(row.get(g)), _norm_text(row.get(j)), _norm_text(row.get(e)))
            if key in seen_jer:
                continue
            seen_jer.add(key)
            jer_rows.append(
                {"gerente": key[0], "jefe": key[1], "especialista": key[2]}
            )
    if jer_rows:
        dim_frames["dim_jerarquia_comercial"] = pd.DataFrame(jer_rows)

    aliados = set()
    for col, df in (
        ("gv_desc2", ventas),
        ("descrip2", presupuesto),
        ("aliado", registros),
    ):
        if col in df.columns:
            aliados.update(_norm_text(v) for v in df[col].unique())
    aliados.discard(None)
    if aliados:
        dim_frames["dim_aliado"] = pd.DataFrame(
            [{"aliado_nk": a, "nombre_aliado": a} for a in sorted(aliados)]
        )

    if "unidad_de_gestion" in presupuesto.columns:
        ugs = {
            _norm_text(v) for v in presupuesto["unidad_de_gestion"].unique()
        }
        ugs.discard(None)
        if ugs:
            dim_frames["dim_unidad_gestion"] = pd.DataFrame(
                [
                    {
                        "unidad_gestion_nk": u,
                        "nombre_unidad_gestion": u,
                    }
                    for u in sorted(ugs)
                ]
            )

    if "marca" in ventas.columns:
        marcas = {_norm_text(v) for v in ventas["marca"].unique()}
        marcas.discard(None)
        if marcas:
            dim_frames["dim_marca"] = pd.DataFrame(
                [{"marca_nk": m, "nombre_marca": m} for m in sorted(marcas)]
            )

    if "cedula_vendedor" in ventas.columns:
        vends = {_norm_text(v) for v in ventas["cedula_vendedor"].unique()}
        vends.discard(None)
        if vends:
            dim_frames["dim_vendedor"] = pd.DataFrame(
                [
                    {"cedula_vendedor_nk": v, "nombre_vendedor": None}
                    for v in sorted(vends)
                ]
            )

    if "nombre_campana" in registros.columns:
        camps = {_norm_text(v) for v in registros["nombre_campana"].unique()}
        camps.discard(None)
        if camps:
            dim_frames["dim_campana"] = pd.DataFrame(
                [{"campana_nk": c, "nombre_campana": c} for c in sorted(camps)]
            )

    if "segmento" in registros.columns:
        segs = {_norm_text(v) for v in registros["segmento"].unique()}
        segs.discard(None)
        if segs:
            dim_frames["dim_segmento"] = pd.DataFrame(
                [
                    {
                        "segmento_nk": s,
                        "segmento_normalizado": s,
                        "nombre_segmento": s,
                    }
                    for s in sorted(segs)
                ]
            )

    if "tipo_contacto" in registros.columns:
        tip_rows = []
        seen_tip: set[tuple[str | None, str | None]] = set()
        cols = ["tipo_contacto"]
        if "detalle1" in registros.columns:
            cols.append("detalle1")
        for _, row in registros[cols].drop_duplicates().iterrows():
            tipo = _norm_text(row.get("tipo_contacto"))
            det = _norm_text(row.get("detalle1")) if "detalle1" in row else None
            key = (tipo, det)
            if tipo is None or key in seen_tip:
                continue
            seen_tip.add(key)
            tip_rows.append(
                {
                    "tipo_contacto": tipo,
                    "detalle_contacto": det,
                    "nombre_tipo_contacto": tipo,
                }
            )
        if tip_rows:
            dim_frames["dim_tipo_contacto"] = pd.DataFrame(tip_rows)

    # validez: dominio seed; opcionalmente sincroniza flags observados
    if "sk_validez" in ventas.columns:
        validez_rows = []
        for sk in sorted({int(v) for v in ventas["sk_validez"].dropna().unique()}):
            mapping = {
                1: (True, False, True, "Venta valida"),
                2: (False, False, False, "Sin factura"),
                3: (True, True, False, "Con nota credito"),
                4: (False, True, False, "Sin factura con nota credito"),
            }
            if sk not in mapping:
                continue
            tf, tn, ev, desc = mapping[sk]
            validez_rows.append(
                {
                    "sk_validez": sk,
                    "tiene_factura": tf,
                    "tiene_nota_credito": tn,
                    "es_venta_valida": ev,
                    "descripcion": desc,
                }
            )
        if validez_rows:
            dim_frames["dim_validez_venta"] = pd.DataFrame(validez_rows)

    return dim_frames


def _lookup_sk_map(
    settings: PostgresSettings,
    table: str,
    sk_col: str,
    nk_cols: tuple[str, ...],
) -> dict[tuple[Any, ...], int]:
    """Carga mapa NK → SK desde PostgreSQL."""
    cols_sql = ", ".join([sk_col, *nk_cols])
    query = f"SELECT {cols_sql} FROM dwh.{table}"
    mapping: dict[tuple[Any, ...], int] = {}
    with postgres_connection(settings) as connection:
        with connection.cursor(row_factory=tuple_row) as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                sk = int(row[0])
                nk = tuple(row[1:])
                mapping[nk] = sk
    return mapping


def _resolve_sk(
    mapping: dict[tuple[Any, ...], int],
    key: tuple[Any, ...],
    default: int = 0,
) -> int:
    return mapping.get(key, default)


def _build_fact_frames(
    settings: PostgresSettings,
    ruled: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Construye hechos resolviendo SK contra dimensiones ya cargadas."""
    ventas = ruled["ventas"]
    presupuesto = ruled["presupuesto"]
    registros = ruled["registros"]

    map_tiempo_fecha = _lookup_sk_map(
        settings, "dim_tiempo", "sk_tiempo", ("fecha",)
    )
    map_region = _lookup_sk_map(
        settings, "dim_region", "sk_region", ("region_nk",)
    )
    map_canal = _lookup_sk_map(
        settings, "dim_canal", "sk_canal", ("canal", "canal2", "sub_canal")
    )
    map_categoria = _lookup_sk_map(
        settings, "dim_categoria", "sk_categoria", ("categoria_nk",)
    )
    map_jer = _lookup_sk_map(
        settings,
        "dim_jerarquia_comercial",
        "sk_jerarquia",
        ("gerente", "jefe", "especialista"),
    )
    map_aliado = _lookup_sk_map(
        settings, "dim_aliado", "sk_aliado", ("aliado_nk",)
    )
    map_marca = _lookup_sk_map(
        settings, "dim_marca", "sk_marca", ("marca_nk",)
    )
    map_vendedor = _lookup_sk_map(
        settings, "dim_vendedor", "sk_vendedor", ("cedula_vendedor_nk",)
    )
    map_ug = _lookup_sk_map(
        settings,
        "dim_unidad_gestion",
        "sk_unidad_gestion",
        ("unidad_gestion_nk",),
    )
    map_campana = _lookup_sk_map(
        settings, "dim_campana", "sk_campana", ("campana_nk",)
    )
    map_segmento = _lookup_sk_map(
        settings, "dim_segmento", "sk_segmento", ("segmento_nk",)
    )
    map_tipo = _lookup_sk_map(
        settings,
        "dim_tipo_contacto",
        "sk_tipo_contacto",
        ("tipo_contacto", "detalle_contacto"),
    )

    fact_ventas_rows: list[dict[str, Any]] = []
    for _, row in ventas.iterrows():
        fecha = row.get("fecha_venta")
        ts = pd.to_datetime(fecha, errors="coerce")
        fecha_key = (None if pd.isna(ts) else ts.date(),)
        region = _norm_text(row.get("region_comercial"))
        canal = _norm_text(row.get("canal"))
        canal2 = _norm_text(row.get("canal2"))
        categoria = _norm_text(row.get("categoria"))
        gerente = _norm_text(row.get("gv_gerente_area"))
        jefe = _norm_text(row.get("gv_jefe_1_canal_regional"))
        esp = _norm_text(row.get("gv_especialista"))
        aliado = _norm_text(row.get("gv_desc2"))
        marca = _norm_text(row.get("marca"))
        vend = _norm_text(row.get("cedula_vendedor"))
        sk_validez = int(row["sk_validez"]) if "sk_validez" in row and not pd.isna(row["sk_validez"]) else 2
        valor = row.get("valor_antes_de_iva", 0)
        if pd.isna(valor):
            valor = 0
        fact_ventas_rows.append(
            {
                "sk_tiempo": _resolve_sk(map_tiempo_fecha, fecha_key),
                "sk_region": _resolve_sk(map_region, (region,)),
                "sk_canal": _resolve_sk(map_canal, (canal, canal2, None)),
                "sk_categoria": _resolve_sk(map_categoria, (categoria,)),
                "sk_jerarquia": _resolve_sk(map_jer, (gerente, jefe, esp)),
                "sk_aliado": _resolve_sk(map_aliado, (aliado,)),
                "sk_marca": _resolve_sk(map_marca, (marca,)),
                "sk_vendedor": _resolve_sk(map_vendedor, (vend,)),
                "sk_validez": sk_validez,
                "codigo_factura": _norm_text(row.get("codigo_factura")),
                "valor_antes_iva": float(valor),
                "cuotas": None if pd.isna(row.get("cuotas")) else float(row.get("cuotas")),
            }
        )

    fact_pres_rows: list[dict[str, Any]] = []
    for _, row in presupuesto.iterrows():
        mes = row.get("mes")
        ts = pd.to_datetime(mes, errors="coerce")
        fecha_key = (None if pd.isna(ts) else ts.date(),)
        term = float(row["terminales"]) if not pd.isna(row.get("terminales")) else 0.0
        tec = float(row["tecnologia"]) if not pd.isna(row.get("tecnologia")) else 0.0
        tyt = float(row["t_t"]) if "t_t" in row and not pd.isna(row.get("t_t")) else term + tec
        fact_pres_rows.append(
            {
                "sk_tiempo": _resolve_sk(map_tiempo_fecha, fecha_key),
                "sk_region": _resolve_sk(
                    map_region, (_norm_text(row.get("region")),)
                ),
                "sk_canal": _resolve_sk(
                    map_canal,
                    (
                        _norm_text(row.get("canal")),
                        _norm_text(row.get("canal2")),
                        _norm_text(row.get("sub_canal")),
                    ),
                ),
                "sk_categoria": _resolve_sk(
                    map_categoria, (_norm_text(row.get("categoria")),)
                ),
                "sk_unidad_gestion": _resolve_sk(
                    map_ug, (_norm_text(row.get("unidad_de_gestion")),)
                ),
                "sk_jerarquia": _resolve_sk(
                    map_jer,
                    (
                        _norm_text(row.get("gerente")),
                        _norm_text(row.get("jefe")),
                        _norm_text(row.get("especialista")),
                    ),
                ),
                "sk_aliado": _resolve_sk(
                    map_aliado, (_norm_text(row.get("descrip2")),)
                ),
                "terminales": term,
                "tecnologia": tec,
                "tyt": tyt,
            }
        )

    fact_gest_rows: list[dict[str, Any]] = []
    for _, row in registros.iterrows():
        fecha = row.get("fecha_gestion")
        if pd.isna(fecha):
            fecha = row.get("periodo")
        ts = pd.to_datetime(fecha, errors="coerce")
        fecha_key = (None if pd.isna(ts) else ts.date(),)
        cant = int(row["cantidad"]) if not pd.isna(row.get("cantidad")) else 0
        intentos = (
            None
            if pd.isna(row.get("intentos"))
            else float(row.get("intentos"))
        )
        fact_gest_rows.append(
            {
                "sk_tiempo": _resolve_sk(map_tiempo_fecha, fecha_key),
                "sk_region": _resolve_sk(
                    map_region, (_norm_text(row.get("division_comercial")),)
                ),
                "sk_jerarquia": _resolve_sk(
                    map_jer,
                    (
                        _norm_text(row.get("gerente")),
                        _norm_text(row.get("jefe")),
                        _norm_text(row.get("especialista")),
                    ),
                ),
                "sk_aliado": _resolve_sk(
                    map_aliado, (_norm_text(row.get("aliado")),)
                ),
                "sk_campana": _resolve_sk(
                    map_campana, (_norm_text(row.get("nombre_campana")),)
                ),
                "sk_segmento": _resolve_sk(
                    map_segmento, (_norm_text(row.get("segmento")),)
                ),
                "sk_tipo_contacto": _resolve_sk(
                    map_tipo,
                    (
                        _norm_text(row.get("tipo_contacto")),
                        _norm_text(row.get("detalle1")),
                    ),
                ),
                "cantidad": cant,
                "intentos": intentos,
            }
        )

    frames: dict[str, pd.DataFrame] = {
        "fact_ventas": pd.DataFrame(
            fact_ventas_rows,
            columns=[
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
            ],
        ),
        "fact_presupuesto": pd.DataFrame(
            fact_pres_rows,
            columns=[
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
            ],
        ),
        "fact_gestion_tmk": pd.DataFrame(
            fact_gest_rows,
            columns=[
                "sk_tiempo",
                "sk_region",
                "sk_jerarquia",
                "sk_aliado",
                "sk_campana",
                "sk_segmento",
                "sk_tipo_contacto",
                "cantidad",
                "intentos",
            ],
        ),
    }
    return frames
