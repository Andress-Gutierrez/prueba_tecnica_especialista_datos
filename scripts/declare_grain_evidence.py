"""Declaración de grano — evidencia sobre Ventas, Presupuesto y Registros."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\data\raw"
)


def load(name: str) -> pd.DataFrame:
    print(f"\n=== Loading {name} ===", flush=True)
    df = pd.read_excel(RAW / name, engine="pyxlsb")
    print(f"shape={df.shape}", flush=True)
    return df


def analyze_ventas(v: pd.DataFrame) -> None:
    print("\n--- VENTAS ---")
    print("columns:", list(v.columns))
    print("exact dups:", int(v.duplicated().sum()))
    print("Código Factura nulls:", int(v["Código Factura"].isna().sum()))
    cf = v["Código Factura"]
    print("Código Factura nunique (dropna):", cf.dropna().nunique())
    print("Código Factura rows non-null:", int(cf.notna().sum()))
    print("dup non-null Código Factura rows:", int(cf.dropna().duplicated(keep=False).sum()))
    # groups with same invoice code
    dup_mask = cf.notna() & cf.duplicated(keep=False)
    vd = v.loc[dup_mask].copy()
    print("rows in duplicate-invoice groups:", len(vd))
    if len(vd):
        # how many distinct invoice codes are duplicated
        print("distinct duplicated invoice codes:", vd["Código Factura"].nunique())
        # sample one code with >1 row
        counts = vd["Código Factura"].value_counts()
        sample_code = counts.index[0]
        sample = v[v["Código Factura"] == sample_code]
        print(f"sample invoice {sample_code} rows={len(sample)}")
        # which columns vary within duplicate groups
        varying = []
        for col in v.columns:
            n = sample[col].nunique(dropna=False)
            if n > 1:
                varying.append((col, n, sample[col].head(5).tolist()))
        print("columns that vary in sample invoice:", varying)
        # aggregate: for each dup invoice, count varying cols
        vary_counts = {c: 0 for c in v.columns}
        for code, g in vd.groupby("Código Factura"):
            if len(g) < 2:
                continue
            for c in v.columns:
                if g[c].nunique(dropna=False) > 1:
                    vary_counts[c] += 1
        ranked = sorted(vary_counts.items(), key=lambda x: -x[1])
        print("invoices where column varies (top):", ranked[:15])
        # same invoice + same all commercial dims?
        key_candidates = [
            ["Código Factura"],
            ["Código Factura", "Marca"],
            ["Código Factura", "Valor Antes de iva"],
            ["Código Factura", "Marca", "Valor Antes de iva"],
            ["Código Factura", "Fecha Venta"],
            ["Código Factura", "Identificación"],
            ["Código Factura", "Cédula Vendedor"],
            ["Código Factura", "Marca", "Valor Antes de iva", "Fecha Venta"],
        ]
        for cols in key_candidates:
            dups = int(v.dropna(subset=["Código Factura"]).duplicated(subset=cols).sum())
            print(f"dups on {cols}: {dups}")

    # full-row uniqueness without invoice
    print("Identificación nunique:", v["Identificación"].nunique(dropna=True))
    # valid sales filter
    valid = v["Código Factura"].notna() & (v["Nota_credito"].isna() | (v["Nota_credito"].astype(str).str.upper() != "SI"))
    # Nota_credito is SI or null - valid = has invoice AND not SI
    valid2 = v["Código Factura"].notna() & ~(v["Nota_credito"].fillna("").astype(str).str.upper().eq("SI"))
    print("valid sales rows (factura + not SI):", int(valid2.sum()))
    print("invalid no factura:", int(v["Código Factura"].isna().sum()))
    print("invalid nota credito SI:", int((v["Nota_credito"].fillna("").astype(str).str.upper() == "SI").sum()))

    # Are there identical commercial rows differing only by something?
    print("\nExact duplicate examples count:", int(v.duplicated(keep=False).sum()))
    if v.duplicated().any():
        ex = v[v.duplicated(keep=False)].head(6)
        print(ex[["Código Factura", "Fecha Venta", "Valor Antes de iva", "Marca", "Identificación"]].to_string())


def analyze_presupuesto(p: pd.DataFrame) -> None:
    print("\n--- PRESUPUESTO ---")
    print("columns:", list(p.columns))
    print("exact dups:", int(p.duplicated().sum()))
    dims = [
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
    print("dups on all dims:", int(p.duplicated(subset=dims).sum()))
    print("unique on all dims:", p.duplicated(subset=dims).eq(False).sum())
    # show duplicate groups
    dmask = p.duplicated(subset=dims, keep=False)
    pdup = p.loc[dmask].sort_values(dims)
    print("rows in dim-dup groups:", len(pdup))
    if len(pdup):
        print(pdup.to_string())
        # do measures differ?
        for code, g in pdup.groupby(dims, dropna=False):
            if len(g) > 1:
                print("group size", len(g))
                print("TERMINALES values", g["TERMINALES"].tolist())
                print("TECNOLOGIA values", g["TECNOLOGIA"].tolist())
                print("T&T values", g["T&T"].tolist())
                # only first few
                break
    # check if measures are additive across dim key uniqueness
    print("nunique all dims key:", p.groupby(dims, dropna=False).ngroups)
    # T&T == TERMINALES+TECNOLOGIA?
    delta = (p["T&T"] - (p["TERMINALES"] + p["TECNOLOGIA"])).abs()
    print("rows where T&T != TERMINALES+TECNOLOGIA (tol 0.01):", int((delta > 0.01).sum()))
    print("max abs delta:", float(delta.max()))


def analyze_registros(r: pd.DataFrame) -> None:
    print("\n--- REGISTROS ---")
    print("columns:", list(r.columns))
    print("exact dups:", int(r.duplicated().sum()))
    candidates = [
        ["NOMBRE_CAMPAÑA", "PERIODO", "FECHA_GESTION", "ALIADO", "TIPO_CONTACTO", "DETALLE1"],
        ["NOMBRE_CAMPAÑA", "PERIODO", "FECHA_GESTION", "ALIADO", "TIPO_CONTACTO", "DETALLE1", "DIVISION_COMERCIAL"],
        ["NOMBRE_CAMPAÑA", "PERIODO", "FECHA_GESTION", "ALIADO", "TIPO_CONTACTO", "DETALLE1", "DIVISION_COMERCIAL", "SEGMENTO"],
        ["NOMBRE_CAMPAÑA", "PERIODO", "FECHA_CARGUE", "ALIADO", "TIPO_CONTACTO", "DETALLE1"],
        list(r.columns),
    ]
    for cols in candidates[:-1]:
        # only existing cols
        cols = [c for c in cols if c in r.columns]
        dups = int(r.duplicated(subset=cols).sum())
        print(f"dups on {cols}: {dups}")
    # sample duplicate on campaign+date+ally+tipo+detalle
    key = ["NOMBRE_CAMPAÑA", "PERIODO", "FECHA_GESTION", "ALIADO", "TIPO_CONTACTO", "DETALLE1", "DIVISION_COMERCIAL"]
    key = [c for c in key if c in r.columns]
    dmask = r.duplicated(subset=key, keep=False)
    rd = r.loc[dmask]
    print("rows in key-dup groups:", len(rd))
    if len(rd):
        # pick a group
        gsize = rd.groupby(key, dropna=False).size().sort_values(ascending=False)
        print("largest group size:", int(gsize.iloc[0]))
        # find that key
        top_key = gsize.index[0]
        if not isinstance(top_key, tuple):
            top_key = (top_key,)
        q = rd.copy()
        for col, val in zip(key, top_key):
            if pd.isna(val):
                q = q[q[col].isna()]
            else:
                q = q[q[col] == val]
        sample = q.head(8)
        print("sample group:")
        print(sample.to_string())
        varying = []
        for c in r.columns:
            if sample[c].nunique(dropna=False) > 1:
                varying.append(c)
        print("varying cols in sample:", varying)
        # CANTIDAD and INTENTOS - are rows aggregates?
        print("CANTIDAD describe:", r["CANTIDAD"].describe().to_dict())
        print("INTENTOS describe:", r["INTENTOS"].describe().to_dict())
        # if we sum CANTIDAD for same key, meaning
        sums = r.groupby(key, dropna=False).agg(rows=("CANTIDAD", "size"), cant=("CANTIDAD", "sum"), intent=("INTENTOS", "sum"))
        print("groups with >1 row:", int((sums["rows"] > 1).sum()))
        print("max rows per key:", int(sums["rows"].max()))


def main() -> None:
    v = load("Ventas.xlsb")
    analyze_ventas(v)
    del v
    p = load("Presupuesto.xlsb")
    analyze_presupuesto(p)
    del p
    r = load("Registros.xlsb")
    analyze_registros(r)


if __name__ == "__main__":
    main()
