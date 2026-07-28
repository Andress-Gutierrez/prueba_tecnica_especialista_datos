"""Análisis adicional de grano — Registros y Ventas."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\data\raw"
)


def main() -> None:
    v = pd.read_excel(RAW / "Ventas.xlsb", engine="pyxlsb")
    # invoice code length / pattern for duplicated codes
    cf = v["Código Factura"].dropna().astype(str)
    dup_codes = cf[cf.duplicated(keep=False)]
    print("dup codes sample value_counts head:")
    print(dup_codes.value_counts().head(20))
    print("len of top dup codes:")
    for code, n in dup_codes.value_counts().head(10).items():
        print(repr(code), "count", n, "strlen", len(str(code)))

    # rows where Código Factura + Cédula Vendedor still duplicate
    subset = ["Código Factura", "Cédula Vendedor"]
    d = v.dropna(subset=["Código Factura"])
    still = d[d.duplicated(subset=subset, keep=False)]
    print("\nrows with dup (factura+vendedor):", len(still))
    if len(still):
        code = still["Código Factura"].value_counts().index[0]
        s = still[still["Código Factura"] == code]
        print("sample:", code, "rows", len(s))
        print(s[["Fecha Venta", "Identificación", "Cédula Vendedor", "Marca", "Valor Antes de iva", "GV_Desc2"]].head(10).to_string())

    # Can full row except measures be unique?
    print("\nall-column uniqueness excluding nothing: dups", int(v.duplicated().sum()))

    del v
    r = pd.read_excel(RAW / "Registros.xlsb", engine="pyxlsb")
    print("\n=== REGISTROS deeper ===")
    print("FECHA_GESTION null pct", round(100 * r["FECHA_GESTION"].isna().mean(), 2))
    print("TIPO_CONTACTO null pct", round(100 * r["TIPO_CONTACTO"].isna().mean(), 2))
    print("ALIADO null pct", round(100 * r["ALIADO"].isna().mean(), 2))

    filled = r[r["FECHA_GESTION"].notna() & r["TIPO_CONTACTO"].notna() & r["DETALLE1"].notna()]
    print("rows with fecha+tipo+detalle:", len(filled))
    key = [
        "NOMBRE_CAMPAÑA",
        "PERIODO",
        "FECHA_GESTION",
        "ALIADO",
        "TIPO_CONTACTO",
        "DETALLE1",
        "DIVISION_COMERCIAL",
        "SEGMENTO",
        "gerente",
        "jefe",
        "Especialista",
        "FECHA_CARGUE",
        "AREA_COMERCIAL",
        "dia",
    ]
    key = [c for c in key if c in filled.columns]
    print("dups on full attr key (filled):", int(filled.duplicated(subset=key).sum()))
    # without hierarchy
    key2 = [
        "CANTIDAD",
        "INTENTOS",
        "NOMBRE_CAMPAÑA",
        "PERIODO",
        "FECHA_GESTION",
        "ALIADO",
        "TIPO_CONTACTO",
        "DETALLE1",
        "DIVISION_COMERCIAL",
        "SEGMENTO",
        "FECHA_CARGUE",
    ]
    print("dups on key2+measures:", int(filled.duplicated(subset=key2).sum()))
    key3 = [c for c in key2 if c not in ("CANTIDAD", "INTENTOS")]
    print("dups on key3 attrs only:", int(filled.duplicated(subset=key3).sum()))
    # when key3 duplicates, do measures differ?
    dmask = filled.duplicated(subset=key3, keep=False)
    g = filled.loc[dmask]
    print("rows in key3 dup groups:", len(g))
    if len(g):
        sizes = g.groupby(key3, dropna=False).size().sort_values(ascending=False)
        print("max group", int(sizes.iloc[0]))
        # inspect first group
        tk = sizes.index[0]
        q = g
        for col, val in zip(key3, tk if isinstance(tk, tuple) else (tk,)):
            if pd.isna(val):
                q = q[q[col].isna()]
            else:
                q = q[q[col] == val]
        print(q.head(6).to_string())
        vary = [c for c in filled.columns if q[c].nunique(dropna=False) > 1]
        print("varying:", vary)

    # Is CANTIDAD typically >1? => aggregated grain
    print("\nCANTIDAD == 1 pct:", round(100 * (r["CANTIDAD"] == 1).mean(), 2))
    print("CANTIDAD > 1 pct:", round(100 * (r["CANTIDAD"] > 1).mean(), 2))
    print("INTENTOS == CANTIDAD pct (non-null):", round(100 * ((r["INTENTOS"] == r["CANTIDAD"]) & r["INTENTOS"].notna()).mean(), 2))

    # null tipification rows
    null_tip = r[r["TIPO_CONTACTO"].isna()]
    print("null tipificacion rows:", len(null_tip))
    print("null tip CANTIDAD sum:", int(null_tip["CANTIDAD"].sum()))


if __name__ == "__main__":
    main()
