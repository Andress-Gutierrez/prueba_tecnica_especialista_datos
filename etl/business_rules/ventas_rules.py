"""
Reglas de negocio del dataset Ventas (prioridad Alta + Lista).

Códigos: RN-001, RN-007, RN-011, RN-012, RN-015, RN-022.
No implementa Media (RN-020) ni Pendientes (RN-P*).
"""

from __future__ import annotations

import pandas as pd

from etl.business_rules.common import (
    rn_007_verificar_columnas_monitoreo,
    rn_015_mapear_sk_validez,
)

# Columnas técnicas post-transform (normalize_column_names).
_COL_CODIGO_FACTURA = "codigo_factura"
_COL_NOTA_CREDITO = "nota_credito"

# RN-007 — dimensiones de monitoreo (sin elegir columna oficial de región: RN-P09).
_COLS_MONITOREO_VENTAS: tuple[str, ...] = (
    "gv_desc2",  # aliado
    "gv_gerente_area",
    "gv_jefe_1_canal_regional",
    "gv_especialista",
)


def rn_022_flag_nota_credito(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-022 — ``Nota_credito = SI`` → nota crédito; nulo/ausencia → sin nota crédito.

    Añade ``tiene_nota_credito`` (bool).
    """
    out = df.copy()
    if _COL_NOTA_CREDITO not in out.columns:
        out["tiene_nota_credito"] = False
        return out

    serie = out[_COL_NOTA_CREDITO]
    # Solo el valor documentado "SI" marca nota crédito (V2 / O1).
    out["tiene_nota_credito"] = serie.astype("string").str.upper().eq("SI").fillna(False)
    return out


def rn_001_ventas_validas(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-001 — Venta válida = factura presente ∧ ¬nota crédito.

    Requiere ``tiene_nota_credito`` (RN-022). Añade ``tiene_factura`` y
    ``es_venta_valida``.
    """
    out = df.copy()
    if "tiene_nota_credito" not in out.columns:
        out = rn_022_flag_nota_credito(out)

    if _COL_CODIGO_FACTURA not in out.columns:
        out["tiene_factura"] = False
    else:
        factura = out[_COL_CODIGO_FACTURA].astype("string")
        out["tiene_factura"] = factura.notna() & factura.str.strip().ne("") & factura.ne("<NA>")

    out["es_venta_valida"] = out["tiene_factura"] & ~out["tiene_nota_credito"].astype(bool)
    return out


def rn_015_asignar_sk_validez(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-015 — Materializa validez como ``sk_validez`` (dominio seed DML).

    Depende de RN-001 / RN-022.
    """
    out = df.copy()
    if "tiene_factura" not in out.columns or "tiene_nota_credito" not in out.columns:
        out = rn_001_ventas_validas(out)

    out["sk_validez"] = [
        rn_015_mapear_sk_validez(bool(tf), bool(tn))
        for tf, tn in zip(out["tiene_factura"], out["tiene_nota_credito"], strict=True)
    ]
    return out


def rn_007_verificar_dims_monitoreo(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-007 — Verifica presencia de columnas de Aliado/Gerente/Jefe/Especialista.

    No selecciona la columna oficial de región (RN-P09 Pendiente).
    No elimina filas; solo valida estructura.
    """
    return rn_007_verificar_columnas_monitoreo(
        df,
        _COLS_MONITOREO_VENTAS,
        "Ventas",
    )


def rn_011_preservar_grano_fila(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-011 — Grano = 1 evento/fila fuente. No colapsa por ``codigo_factura``.
    """
    # Explícitamente no agrega ni deduplica por factura.
    return df.copy()


def rn_012_codigo_factura_no_pk(df: pd.DataFrame) -> pd.DataFrame:
    """
    RN-012 — ``codigo_factura`` no es PK; se conserva como atributo degenerado.

    Si el índice se llama ``codigo_factura``, se resetea para no usarlo como identidad.
    La generación de ``sk_venta`` corresponde a la capa de carga (4.4/4.5).
    """
    out = df.copy()
    if out.index.name == _COL_CODIGO_FACTURA:
        out = out.reset_index()
    return out


def apply_ventas_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Orquesta reglas Alta + Lista aplicables al DataFrame de Ventas.

    Parameters
    ----------
    df:
        DataFrame técnico (salida de ``transform_ventas``).

    Returns
    -------
    pandas.DataFrame
        DataFrame con flags de validez y ``sk_validez``.
    """
    pasos = [
        rn_011_preservar_grano_fila,
        rn_012_codigo_factura_no_pk,
        rn_007_verificar_dims_monitoreo,
        rn_022_flag_nota_credito,
        rn_001_ventas_validas,
        rn_015_asignar_sk_validez,
    ]
    result = df
    for paso in pasos:
        result = paso(result)
    return result
