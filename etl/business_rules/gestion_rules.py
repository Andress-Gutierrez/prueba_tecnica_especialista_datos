"""
Reglas de negocio del dataset Gestión TMK / Registros (prioridad Alta + Lista).

Códigos: RN-008, RN-010 (existencia KPIs, sin fórmulas %), RN-017, RN-019.
No implementa Media (RN-020) ni Pendientes (RN-P01, RN-P02, RN-P12).
"""

from __future__ import annotations

import pandas as pd

from etl.business_rules.common import (
    TIPO_CONTACTO_EFECTIVOS,
    TIPO_CONTACTO_NO_CONTACTOS,
    TIPO_CONTACTO_NO_EFECTIVOS,
)

_COL_TIPO_CONTACTO = "tipo_contacto"
_COL_CANTIDAD = "cantidad"
_COL_INTENTOS = "intentos"


def rn_008_marcar_alcance_tmk_outbound(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-008 — Reto 2 = canal TMK Outbound.

    La fuente Registros no trae columna CANAL homónima; el modelo declara el
    universo como Gestión TMK Outbound. Se anota el flag de alcance sin inventar
    un filtro sobre columna inexistente.
    """
    out = df.copy()
    out["es_alcance_tmk_outbound"] = True
    return out


def rn_017_sin_sk_canal(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-017 — ``fact_gestion_tmk`` no incluye ``sk_canal``.

    Elimina la columna si alguien la hubiera añadido; no la crea.
    """
    out = df.copy()
    if "sk_canal" in out.columns:
        out = out.drop(columns=["sk_canal"])
    return out


def rn_019_preservar_grano_agregado(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-019 — Grano = agregado tipificado (``cantidad`` / ``intentos``).

    No explota a contacto unitario.
    """
    return df.copy()


def rn_010_flags_tipificacion_kpi(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-010 — Prepara flags de tipificación para KPIs mínimos Reto 2.

    No calcula % Gestión / Contactabilidad / Efectivos / No efectivos
    (fórmulas = RN-P01 Pendiente) ni define “registros entregados” (RN-P02).
    Conserva ``cantidad`` e ``intentos`` como medidas observadas.
    """
    out = df.copy()
    if _COL_TIPO_CONTACTO not in out.columns:
        out["es_contacto_efectivo"] = False
        out["es_contacto_no_efectivo"] = False
        out["es_no_contacto"] = False
        return out

    tipo = out[_COL_TIPO_CONTACTO].astype("string").str.strip().str.upper()
    out["es_contacto_efectivo"] = tipo.eq(TIPO_CONTACTO_EFECTIVOS)
    out["es_contacto_no_efectivo"] = tipo.eq(TIPO_CONTACTO_NO_EFECTIVOS)
    out["es_no_contacto"] = tipo.eq(TIPO_CONTACTO_NO_CONTACTOS)
    return out


def apply_gestion_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Orquesta reglas Alta + Lista aplicables al DataFrame de Gestión TMK.

    Parameters
    ----------
    df:
        DataFrame técnico (salida de ``transform_gestion_tmk``).

    Returns
    -------
    pandas.DataFrame
        Gestión con flags TMK/tipificación y sin ``sk_canal``.
    """
    result = rn_019_preservar_grano_agregado(df)
    result = rn_017_sin_sk_canal(result)
    result = rn_008_marcar_alcance_tmk_outbound(result)
    result = rn_010_flags_tipificacion_kpi(result)
    # Conservar medidas agregadas si existen (sin reinterpretar RN-P02).
    _ = (_COL_CANTIDAD, _COL_INTENTOS)
    return result
