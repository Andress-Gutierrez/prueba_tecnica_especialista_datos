"""
Reglas de negocio del dataset Presupuesto (prioridad Alta + Lista).

Códigos: RN-003 (prep), RN-007, RN-016, RN-018.
Días hábiles: lectura exclusiva desde ``dim_tiempo`` (calendario oficial).
No implementa Media (RN-020) ni Pendientes (RN-P03, RN-P07).
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from etl.business_rules.common import (
    rn_003_meta_diaria,
    rn_007_verificar_columnas_monitoreo,
)

_COL_MES = "mes"

# RN-007 — dimensiones de monitoreo (sin región oficial Ventas: RN-P09).
_COLS_MONITOREO_PRESUPUESTO: tuple[str, ...] = (
    "region",
    "descrip2",  # aliado
    "gerente",
    "jefe",
    "especialista",
)


def rn_016_preservar_grano_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-016 — Grano = mes × jerarquía. No explota a día hábil en esta capa.

    La proyección diaria (si aplica) queda en capas posteriores / Power BI.
    """
    return df.copy()


def rn_018_preservar_medidas_observadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-018 — Conserva TERMINALES, TECNOLOGIA y T&T tal como vienen.

    No elige una medida “oficial” única (RN-P03 Pendiente).
    No redefine T&T (RN-P07 Pendiente).
    """
    return df.copy()


def anotar_dias_habiles_mes_desde_dim_tiempo(
    df: pd.DataFrame,
    dias_habiles_por_periodo: Mapping[int, int],
) -> pd.DataFrame:
    """
    Anota ``dias_habiles_mes`` desde el calendario oficial ``dim_tiempo``.

    Parameters
    ----------
    df:
        Presupuesto mensual.
    dias_habiles_por_periodo:
        Mapa ``periodo_yyyymm`` → conteo de días con ``es_habil = TRUE``
        en ``dwh.dim_tiempo`` (única fuente oficial del calendario corporativo).
    """
    out = df.copy()
    if _COL_MES not in out.columns:
        out["dias_habiles_mes"] = pd.NA
        return out

    def _lookup(valor: object) -> int | None:
        ts = pd.to_datetime(valor, errors="coerce")
        if pd.isna(ts):
            return None
        periodo = int(ts.year) * 100 + int(ts.month)
        return int(dias_habiles_por_periodo.get(periodo, 0))

    out["dias_habiles_mes"] = out[_COL_MES].map(_lookup)
    return out


def rn_003_anotar_meta_diaria_por_medida(
    df: pd.DataFrame,
    columna_meta_mensual: str,
    columna_salida: str,
) -> pd.DataFrame:
    """
    RN-003 — Anota meta diaria para una medida mensual concreta.

    Requiere ``dias_habiles_mes`` (calendario oficial ``dim_tiempo``).
    """
    out = df.copy()
    if columna_meta_mensual not in out.columns or "dias_habiles_mes" not in out.columns:
        out[columna_salida] = pd.NA
        return out

    metas: list[float | None] = []
    for meta, dias in zip(out[columna_meta_mensual], out["dias_habiles_mes"], strict=True):
        if pd.isna(meta) or pd.isna(dias):
            metas.append(None)
        else:
            metas.append(rn_003_meta_diaria(float(meta), int(dias)))
    out[columna_salida] = metas
    return out


def rn_007_verificar_dims_monitoreo(df: pd.DataFrame) -> pd.DataFrame:
    """RN-007 — Verifica columnas de monitoreo en Presupuesto."""
    return rn_007_verificar_columnas_monitoreo(
        df,
        _COLS_MONITOREO_PRESUPUESTO,
        "Presupuesto",
    )


def apply_presupuesto_rules(
    df: pd.DataFrame,
    *,
    dias_habiles_por_periodo: Mapping[int, int],
) -> pd.DataFrame:
    """
    Orquesta reglas Alta + Lista aplicables al DataFrame de Presupuesto.

    Parameters
    ----------
    df:
        DataFrame técnico (salida de ``transform_presupuesto``).
    dias_habiles_por_periodo:
        Conteo de días hábiles por ``periodo_yyyymm`` leído de ``dim_tiempo``.

    Returns
    -------
    pandas.DataFrame
        Presupuesto mensual con ``dias_habiles_mes`` desde el calendario oficial.
    """
    result = rn_016_preservar_grano_mensual(df)
    result = rn_018_preservar_medidas_observadas(result)
    result = rn_007_verificar_dims_monitoreo(result)
    result = anotar_dias_habiles_mes_desde_dim_tiempo(
        result, dias_habiles_por_periodo
    )
    return result
