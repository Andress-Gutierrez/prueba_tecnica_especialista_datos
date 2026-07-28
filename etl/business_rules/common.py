"""
Utilidades reutilizables de reglas de negocio (RN transversales Alta + Lista).

Códigos: RN-003, RN-004, RN-005, RN-006 (principio diferido),
RN-007, RN-013, RN-014.
No implementa RN-P* ni reglas de prioridad Media (RN-020, RN-021).
Días hábiles: única fuente oficial ``dim_tiempo`` (calendar_seed_dag).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Set

import pandas as pd

# Alias compatible con entornos donde collections.abc.AbstractSet no está expuesto.
AbstractSet = Set

# RN-014 — Miembro "No informado"
SK_NO_INFORMADO: int = 0

# RN-015 / seed dim_validez_venta
SK_VALIDEZ_VALIDA: int = 1
SK_VALIDEZ_SIN_FACTURA: int = 2
SK_VALIDEZ_CON_NOTA_CREDITO: int = 3
SK_VALIDEZ_SIN_FACTURA_CON_NOTA: int = 4

# Tipificación observada (R1) — soporte RN-010 existencia de KPIs, sin fórmulas %
TIPO_CONTACTO_EFECTIVOS: str = "CONTACTOS EFECTIVOS"
TIPO_CONTACTO_NO_EFECTIVOS: str = "CONTACTOS NO EFECTIVOS"
TIPO_CONTACTO_NO_CONTACTOS: str = "NO CONTACTOS"


def rn_007_verificar_columnas_monitoreo(
    df: pd.DataFrame,
    columnas_requeridas: Sequence[str],
    nombre_dataset: str,
) -> pd.DataFrame:
    """
    RN-007 — Verifica presencia de columnas de monitoreo dimensional.

    No elimina filas; solo valida estructura. Parametrizable por dataset.

    Parameters
    ----------
    df:
        DataFrame de entrada.
    columnas_requeridas:
        Columnas de monitoreo exigidas por el dataset.
    nombre_dataset:
        Etiqueta del dataset para el mensaje de error.

    Returns
    -------
    pandas.DataFrame
        Copia del DataFrame si todas las columnas están presentes.

    Raises
    ------
    ValueError
        Si falta alguna columna requerida.
    """
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"RN-007: faltan columnas de monitoreo en {nombre_dataset}: "
            + ", ".join(faltantes)
        )
    return df.copy()


def rn_014_sk_no_informado(valor_sk: Any) -> int:
    """
    RN-014 — Ante nulo / no homologable → ``sk = 0`` ("No informado").

    Parameters
    ----------
    valor_sk:
        Surrogate key resuelta o nulo.

    Returns
    -------
    int
        SK original si es válida; ``0`` si falta o no es convertible.
    """
    if valor_sk is None or (isinstance(valor_sk, float) and pd.isna(valor_sk)):
        return SK_NO_INFORMADO
    if pd.isna(valor_sk):
        return SK_NO_INFORMADO
    try:
        sk = int(valor_sk)
    except (TypeError, ValueError):
        return SK_NO_INFORMADO
    if sk < 0:
        return SK_NO_INFORMADO
    return sk


def rn_013_resolver_sk(
    clave_natural: Any,
    mapa_nk_a_sk: Mapping[Any, int],
) -> int:
    """
    RN-013 — Lookup de SK por NK; si no hay match → RN-014 (``sk = 0``).

    Parameters
    ----------
    clave_natural:
        Natural key a resolver.
    mapa_nk_a_sk:
        Diccionario NK → SK (sin el miembro 0).

    Returns
    -------
    int
        Surrogate key resuelta o ``SK_NO_INFORMADO``.
    """
    if clave_natural is None or (isinstance(clave_natural, float) and pd.isna(clave_natural)):
        return SK_NO_INFORMADO
    if pd.isna(clave_natural):
        return SK_NO_INFORMADO
    sk = mapa_nk_a_sk.get(clave_natural)
    if sk is None:
        # Intento con str normalizado mínimo (sin homologación de negocio Media)
        sk = mapa_nk_a_sk.get(str(clave_natural).strip())
    return rn_014_sk_no_informado(sk)


def rn_003_meta_diaria(
    meta_mensual: float,
    dias_habiles_mes: int,
) -> float | None:
    """
    RN-003 — Meta diaria = meta mensual ÷ días hábiles del mes.

    No elige la medida fuente (TERMINALES / TECNOLOGIA / T&T → RN-P03 Pendiente).
    El llamador pasa el valor de meta mensual ya seleccionado.
    Los días hábiles provienen de ``dim_tiempo`` (calendario oficial).

    Parameters
    ----------
    meta_mensual:
        Meta del periodo mensual.
    dias_habiles_mes:
        Días hábiles del mes (fuente: dim_tiempo.es_habil).

    Returns
    -------
    float | None
        Meta diaria, o ``None`` si no hay días hábiles.
    """
    if dias_habiles_mes <= 0:
        return None
    return float(meta_mensual) / float(dias_habiles_mes)


def rn_004_rn_005_acumular_deficit(
    metas_diarias: Iterable[float],
    ventas_validas_diarias: Iterable[float],
) -> list[float]:
    """
    RN-004 + RN-005 — Déficit acumula al siguiente día hábil; excedente no descuenta.

    Secuencia alineada día hábil a día hábil. No aplica recalculo dinámico O6
    (RN-006 / RN-P04 Pendiente).

    Parameters
    ----------
    metas_diarias:
        Meta base de cada día hábil (p. ej. resultado de RN-003).
    ventas_validas_diarias:
        Ventas válidas del mismo día hábil.

    Returns
    -------
    list[float]
        Déficit acumulado al cierre de cada día (0 si hubo excedente o cumplimiento).
    """
    deficit_carry = 0.0
    resultado: list[float] = []
    for meta, ventas in zip(metas_diarias, ventas_validas_diarias, strict=True):
        meta_efectiva = float(meta) + deficit_carry
        ventas_f = float(ventas)
        if ventas_f < meta_efectiva:
            deficit_carry = meta_efectiva - ventas_f
        else:
            # RN-005: excedente no reduce la meta del día siguiente
            deficit_carry = 0.0
        resultado.append(deficit_carry)
    return resultado


def rn_006_recalculo_dinamico_meta(
    *_args: Any,
    **_kwargs: Any,
) -> None:
    """
    RN-006 — Principio Lista; detalle de fórmula **Pendiente (RN-P04)**.

    No se inventa comportamiento. No debe invocarse en orquestadores hasta
    resolución documentada del vacío V4 / RN-P04.

    Raises
    ------
    NotImplementedError
        Siempre: fórmula exacta no catalogada como Lista.
    """
    raise NotImplementedError(
        "RN-006: principio documentado; fórmula exacta pendiente (RN-P04). "
        "No implementar comportamiento inventado."
    )


def rn_015_mapear_sk_validez(
    tiene_factura: bool,
    tiene_nota_credito: bool,
) -> int:
    """
    RN-015 — Mapeo a ``sk_validez`` según seed ``02_seed_dim_validez_venta.sql``.

    Parameters
    ----------
    tiene_factura:
        Factura presente.
    tiene_nota_credito:
        Nota crédito = SI (RN-022).

    Returns
    -------
    int
        ``sk_validez`` ∈ {1, 2, 3, 4}.
    """
    if tiene_factura and not tiene_nota_credito:
        return SK_VALIDEZ_VALIDA
    if (not tiene_factura) and (not tiene_nota_credito):
        return SK_VALIDEZ_SIN_FACTURA
    if tiene_factura and tiene_nota_credito:
        return SK_VALIDEZ_CON_NOTA_CREDITO
    return SK_VALIDEZ_SIN_FACTURA_CON_NOTA
