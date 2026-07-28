"""Análisis de solapamiento de claves entre fuentes (Fase 1)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\data\raw"
)


def load(name: str) -> pd.DataFrame:
    print(f"Loading {name}...", flush=True)
    return pd.read_excel(RAW / name, engine="pyxlsb")


def norm(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.upper()


def overlap(a: pd.Series, b: pd.Series, label: str) -> None:
    sa = set(norm(a.dropna()).unique())
    sb = set(norm(b.dropna()).unique())
    inter = sa & sb
    only_a = sa - sb
    only_b = sb - sa
    print(
        f"{label}: A={len(sa)} B={len(sb)} inter={len(inter)} "
        f"onlyA={len(only_a)} onlyB={len(only_b)}",
        flush=True,
    )
    if only_a and len(only_a) <= 15:
        print(f"  onlyA sample: {sorted(only_a)[:15]}")
    if only_b and len(only_b) <= 15:
        print(f"  onlyB sample: {sorted(only_b)[:15]}")


def main() -> None:
    p = load("Presupuesto.xlsb")
    v = load("Ventas.xlsb")
    r = load("Registros.xlsb")

    print("\n--- Date / period ranges ---", flush=True)
    print("Presupuesto MES unique:", sorted(p["MES"].unique().tolist()))
    print("Ventas Fecha Venta min/max:", v["Fecha Venta"].min(), v["Fecha Venta"].max())
    print("Ventas AÑO unique:", sorted(v["AÑO"].unique().tolist()))
    print("Ventas MES unique:", sorted(v["MES"].unique().tolist()))
    print("Registros PERIODO unique:", sorted(r["PERIODO"].unique().tolist()))
    print("Registros FECHA_GESTION sample dtype:", r["FECHA_GESTION"].dtype)
    print("Registros FECHA_GESTION min/max:", r["FECHA_GESTION"].dropna().min(), r["FECHA_GESTION"].dropna().max())

    print("\n--- Grain checks ---", flush=True)
    grain_p = [
        "MES",
        "REGION",
        "CANAL",
        "CANAL2",
        "SUB CANAL",
        "CATEGORIA",
        "UNIDAD DE GESTION",
        "ESPECIALISTA",
        "JEFE",
        "GERENTE",
        "DESCRIP2",
    ]
    print("Presupuesto dup on grain dims:", int(p.duplicated(subset=grain_p).sum()))
    print("Ventas Código Factura nulls:", int(v["Código Factura"].isna().sum()))
    print("Ventas Código Factura dups (non-null):", int(v["Código Factura"].dropna().duplicated().sum()))
    print("Ventas Identificación nunique:", v["Identificación"].nunique(dropna=True))

    print("\n--- Key overlaps ---", flush=True)
    overlap(p["REGION"], v["Región Comercial"], "Presupuesto.REGION vs Ventas.Región Comercial")
    overlap(p["REGION"], v["GV-Division"], "Presupuesto.REGION vs Ventas.GV-Division")
    overlap(p["REGION"], r["DIVISION_COMERCIAL"], "Presupuesto.REGION vs Registros.DIVISION_COMERCIAL")
    overlap(p["ESPECIALISTA"], v["GV-Especialista"], "Presupuesto.ESPECIALISTA vs Ventas.GV-Especialista")
    overlap(p["ESPECIALISTA"], r["Especialista"], "Presupuesto.ESPECIALISTA vs Registros.Especialista")
    overlap(p["JEFE"], v["GV-JEFE 1 CANAL REGIONAL"], "Presupuesto.JEFE vs Ventas.GV-JEFE")
    overlap(p["JEFE"], r["jefe"], "Presupuesto.JEFE vs Registros.jefe")
    overlap(p["GERENTE"], v["GV-Gerente Area"], "Presupuesto.GERENTE vs Ventas.GV-Gerente")
    overlap(p["GERENTE"], r["gerente"], "Presupuesto.GERENTE vs Registros.gerente")
    overlap(p["DESCRIP2"], v["GV_Desc2"], "Presupuesto.DESCRIP2 vs Ventas.GV_Desc2")
    overlap(p["DESCRIP2"], r["ALIADO"], "Presupuesto.DESCRIP2 vs Registros.ALIADO")
    overlap(p["CANAL"], v["CANAL"], "Presupuesto.CANAL vs Ventas.CANAL")
    overlap(p["CANAL2"], v["CANAL2"], "Presupuesto.CANAL2 vs Ventas.CANAL2")
    overlap(p["CATEGORIA"], v["CATEGORIA"], "Presupuesto.CATEGORIA vs Ventas.CATEGORIA")

    print("\n--- Measure stats Presupuesto ---", flush=True)
    for c in ["TERMINALES", "TECNOLOGIA", "T&T"]:
        print(c, "sum=", float(p[c].sum()), "min=", float(p[c].min()), "max=", float(p[c].max()))

    print("\n--- Measure stats Ventas ---", flush=True)
    print("Valor Antes de iva sum=", int(v["Valor Antes de iva"].sum()))
    print("Nota_credito value counts:\n", v["Nota_credito"].value_counts(dropna=False).head())
    print("Descripción Estado Reserva:\n", v["Descripción Estado Reserva"].value_counts())

    print("\n--- Registros measures ---", flush=True)
    print("CANTIDAD sum=", int(r["CANTIDAD"].sum()))
    print("INTENTOS sum=", float(r["INTENTOS"].sum()))
    print("TIPO_CONTACTO:\n", r["TIPO_CONTACTO"].value_counts(dropna=False))
    print("SEGMENTO:\n", r["SEGMENTO"].value_counts(dropna=False))

    # Period alignment Ventas YYYYMM vs Presupuesto MES
    v_period = (2000 + v["AÑO"]) * 100 + v["MES"]
    print("\nVentas derived YYYYMM unique:", sorted(v_period.unique().tolist()))
    print(
        "Presupuesto MES in Ventas periods?",
        set(p["MES"].unique()).issubset(set(v_period.unique())),
    )
    print(
        "Presupuesto MES vs Registros PERIODO inter:",
        set(p["MES"].unique()) & set(r["PERIODO"].unique()),
    )


if __name__ == "__main__":
    main()
