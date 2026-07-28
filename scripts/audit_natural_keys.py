"""Auditoría de claves naturales — evidencia para Tech Lead."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RAW = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\data\raw"
)
OUT = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\docs\modelo"
)


def ventas_audit() -> dict:
    print("Loading Ventas...", flush=True)
    v = pd.read_excel(RAW / "Ventas.xlsb", engine="pyxlsb")
    n = len(v)
    cf = v["Código Factura"]
    nulls = int(cf.isna().sum())
    non_null = int(cf.notna().sum())
    nunique = int(cf.dropna().nunique())
    # duplicate non-null values: values that appear >1
    vc = cf.dropna().astype(str).value_counts()
    dup_values = vc[vc > 1]
    n_dup_values = int(len(dup_values))
    n_rows_in_dup_groups = int(dup_values.sum())
    n_extra_rows = int((vc - 1).clip(lower=0).sum())  # duplicated() count style

    # list ALL duplicate codes with counts
    dup_list = [{"codigo": k, "ocurrencias": int(c)} for k, c in dup_values.items()]

    # for each dup code, which columns vary
    vary_summary = []
    col_vary_freq = {c: 0 for c in v.columns}
    samples = []
    for code, cnt in dup_values.items():
        g = v[cf.astype(str) == code] if cf.notna().any() else v.iloc[0:0]
        # better: match original
        g = v[cf.notna() & (cf.astype(str) == str(code))]
        varying = []
        for c in v.columns:
            if g[c].nunique(dropna=False) > 1:
                varying.append(c)
                col_vary_freq[c] += 1
        vary_summary.append({"codigo": str(code), "ocurrencias": int(cnt), "columnas_que_cambian": varying})
        if len(samples) < 5:
            samples.append(
                {
                    "codigo": str(code),
                    "ocurrencias": int(cnt),
                    "preview": g[
                        [
                            "Código Factura",
                            "Fecha Venta",
                            "Identificación",
                            "Cédula Vendedor",
                            "Marca",
                            "Valor Antes de iva",
                            "GV_Desc2",
                            "GV-Especialista",
                            "Región Comercial",
                        ]
                    ]
                    .astype(object)
                    .where(pd.notnull(g[
                        [
                            "Código Factura",
                            "Fecha Venta",
                            "Identificación",
                            "Cédula Vendedor",
                            "Marca",
                            "Valor Antes de iva",
                            "GV_Desc2",
                            "GV-Especialista",
                            "Región Comercial",
                        ]
                    ]), None)
                    .to_dict(orient="records"),
                    "columnas_que_cambian": varying,
                }
            )

    # stability: same code over time with different business meaning
    multi_date = 0
    multi_client = 0
    multi_value = 0
    multi_brand = 0
    for code in dup_values.index:
        g = v[cf.notna() & (cf.astype(str) == str(code))]
        if g["Fecha Venta"].nunique(dropna=False) > 1:
            multi_date += 1
        if g["Identificación"].nunique(dropna=False) > 1:
            multi_client += 1
        if g["Valor Antes de iva"].nunique(dropna=False) > 1:
            multi_value += 1
        if g["Marca"].nunique(dropna=False) > 1:
            multi_brand += 1

    # empty / weird codes
    cf_str = cf.dropna().astype(str).str.strip()
    weird = cf_str[cf_str.str.len() < 5]
    weird_vc = weird.value_counts()

    result = {
        "total_filas": n,
        "nulls": nulls,
        "non_null": non_null,
        "nunique": nunique,
        "valores_duplicados_distintos": n_dup_values,
        "filas_en_grupos_duplicados": n_rows_in_dup_groups,
        "filas_extra_por_duplicacion": n_extra_rows,
        "es_unica": n_dup_values == 0 and nulls == 0,
        "dup_list": dup_list,  # ALL
        "dup_list_top20": dup_list[:20],
        "col_vary_freq": sorted(col_vary_freq.items(), key=lambda x: -x[1])[:20],
        "multi_date": multi_date,
        "multi_client": multi_client,
        "multi_value": multi_value,
        "multi_brand": multi_brand,
        "samples": samples,
        "weird_short_codes": [{"codigo": k, "n": int(c)} for k, c in weird_vc.head(20).items()],
        "exact_row_dups": int(v.duplicated().sum()),
    }
    # other candidate keys uniqueness
    candidates = {
        "Identificación": ["Identificación"],
        "Código Factura + Identificación": ["Código Factura", "Identificación"],
        "Código Factura + Fecha Venta + Identificación": [
            "Código Factura",
            "Fecha Venta",
            "Identificación",
        ],
        "Código Factura + Cédula Vendedor + Fecha Venta + Valor + Marca": [
            "Código Factura",
            "Cédula Vendedor",
            "Fecha Venta",
            "Valor Antes de iva",
            "Marca",
        ],
    }
    cand_stats = {}
    for name, cols in candidates.items():
        d = v.copy()
        # for uniqueness of natural key, nulls in key break uniqueness
        null_key = d[cols].isna().any(axis=1).sum()
        d2 = d.dropna(subset=cols)
        dups = int(d2.duplicated(subset=cols).sum())
        nunq = int(d2.drop_duplicates(subset=cols).shape[0])
        cand_stats[name] = {
            "null_rows": int(null_key),
            "rows_non_null_key": len(d2),
            "unique_keys": nunq,
            "duplicate_rows": dups,
            "is_unique_when_non_null": dups == 0,
        }
    result["other_candidates"] = cand_stats
    print("Ventas done", flush=True)
    return result


def presupuesto_audit() -> dict:
    print("Loading Presupuesto...", flush=True)
    p = pd.read_excel(RAW / "Presupuesto.xlsb", engine="pyxlsb")
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
    n = len(p)
    nulls_per = {c: int(p[c].isna().sum()) for c in dims}
    dups = int(p.duplicated(subset=dims).sum())
    groups = p.groupby(dims, dropna=False).size()
    multi = groups[groups > 1]
    multi_list = []
    for idx, cnt in multi.items():
        key = idx if isinstance(idx, tuple) else (idx,)
        key_dict = dict(zip(dims, key))
        g = p.copy()
        for c, val in key_dict.items():
            if pd.isna(val):
                g = g[g[c].isna()]
            else:
                g = g[g[c] == val]
        multi_list.append(
            {
                "clave": {k: (None if pd.isna(v) else (int(v) if hasattr(v, "item") else v)) for k, v in key_dict.items()},
                "ocurrencias": int(cnt),
                "TERMINALES": [float(x) for x in g["TERMINALES"].tolist()],
                "TECNOLOGIA": [float(x) for x in g["TECNOLOGIA"].tolist()],
                "T&T": [float(x) for x in g["T&T"].tolist()],
            }
        )
    return {
        "total_filas": n,
        "dims": dims,
        "nulls_per_dim": nulls_per,
        "unique_dim_keys": int(groups.shape[0]),
        "duplicate_rows_on_dims": dups,
        "claves_con_mas_de_una_fila": int(len(multi)),
        "detalle_claves_duplicadas": multi_list,
        "exact_dups": int(p.duplicated().sum()),
        "es_unica": dups == 0 and all(v == 0 for v in nulls_per.values()),
    }


def registros_audit() -> dict:
    print("Loading Registros...", flush=True)
    r = pd.read_excel(RAW / "Registros.xlsb", engine="pyxlsb")
    n = len(r)
    # no single ID column - test combinations
    combos = {
        "all_columns": list(r.columns),
        "campaña+periodo+fecha+aliado+tipo+detalle+división+segmento+fecha_cargue": [
            "NOMBRE_CAMPAÑA",
            "PERIODO",
            "FECHA_GESTION",
            "ALIADO",
            "TIPO_CONTACTO",
            "DETALLE1",
            "DIVISION_COMERCIAL",
            "SEGMENTO",
            "FECHA_CARGUE",
        ],
        "same_without_fecha_cargue": [
            "NOMBRE_CAMPAÑA",
            "PERIODO",
            "FECHA_GESTION",
            "ALIADO",
            "TIPO_CONTACTO",
            "DETALLE1",
            "DIVISION_COMERCIAL",
            "SEGMENTO",
        ],
    }
    stats = {}
    for name, cols in combos.items():
        cols = [c for c in cols if c in r.columns]
        null_any = int(r[cols].isna().any(axis=1).sum())
        d2 = r.dropna(subset=cols) if name != "all_columns" else r
        # for all_columns use full row
        if name == "all_columns":
            dups = int(r.duplicated().sum())
            nunq = int(r.drop_duplicates().shape[0])
            null_any = 0
            rows_nn = n
        else:
            dups = int(d2.duplicated(subset=cols).sum())
            nunq = int(d2.drop_duplicates(subset=cols).shape[0])
            rows_nn = len(d2)
        stats[name] = {
            "null_rows_any_key_col": null_any,
            "rows_evaluated": rows_nn,
            "unique_keys": nunq,
            "duplicate_rows": dups,
        }
    return {
        "total_filas": n,
        "tiene_columna_id": False,
        "cantidad_gt_1_pct": round(100 * float((r["CANTIDAD"] > 1).mean()), 2),
        "candidates": stats,
        "exact_dups": int(r.duplicated().sum()),
    }


def main() -> None:
    report = {
        "ventas": ventas_audit(),
        "presupuesto": presupuesto_audit(),
        "registros": registros_audit(),
    }
    out = OUT / "_audit_claves_tmp.json"
    # dup_list can be large - keep all for ventas as required
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out}", flush=True)
    # print summary
    v = report["ventas"]
    print("VENTAS summary:")
    print(" total", v["total_filas"], "nunique", v["nunique"], "nulls", v["nulls"])
    print(" dup values", v["valores_duplicados_distintos"], "rows in dup groups", v["filas_en_grupos_duplicados"])
    print(" multi_client", v["multi_client"], "multi_value", v["multi_value"], "multi_brand", v["multi_brand"])
    print("PRESUPUESTO:", report["presupuesto"]["claves_con_mas_de_una_fila"], "dup keys")
    print("REGISTROS exact dups", report["registros"]["exact_dups"])


if __name__ == "__main__":
    main()
