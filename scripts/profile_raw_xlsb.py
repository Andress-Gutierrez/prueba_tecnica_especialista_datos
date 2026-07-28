"""Perfilado temporal Fase 1 — fuentes .xlsb en data/raw."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from pyxlsb import open_workbook

RAW = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\data\raw"
)
OUT = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\docs\analisis"
)
OUT.mkdir(parents=True, exist_ok=True)

FILES = ["Presupuesto.xlsb", "Ventas.xlsb", "Registros.xlsb"]
SAMPLE_UNIQUE = 15


def serialize(v):
    if pd.isna(v):
        return None
    if hasattr(v, "item"):
        try:
            return v.item()
        except Exception:
            pass
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    return str(v)


def profile_sheet(path: Path, sheet: str) -> dict:
    print(f"  Reading sheet: {sheet} ...", flush=True)
    df = pd.read_excel(path, sheet_name=sheet, engine="pyxlsb")
    n_rows, n_cols = df.shape
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    dup_rows = int(df.duplicated().sum())
    cols = []
    for col in df.columns:
        s = df[col]
        non_null = int(s.notna().sum())
        nulls = int(s.isna().sum())
        nunique = int(s.nunique(dropna=True))
        sample = [serialize(x) for x in s.dropna().head(SAMPLE_UNIQUE).tolist()]
        top = None
        if 0 < nunique <= 30:
            vc = s.value_counts(dropna=True).head(10)
            top = {str(k): int(v) for k, v in vc.items()}
        cols.append(
            {
                "name": str(col),
                "dtype": str(s.dtype),
                "non_null": non_null,
                "nulls": nulls,
                "null_pct": round(100 * nulls / n_rows, 2) if n_rows else None,
                "nunique": nunique,
                "sample": sample,
                "top_values": top,
            }
        )
    print(
        f"    -> {n_rows} rows x {n_cols} cols; dups={dup_rows}; empty_cols={len(empty_cols)}",
        flush=True,
    )
    result = {
        "rows": n_rows,
        "cols": n_cols,
        "columns": cols,
        "empty_columns": [str(c) for c in empty_cols],
        "duplicate_rows": dup_rows,
        "column_names": [str(c) for c in df.columns],
    }
    del df
    return result


def main() -> None:
    report: dict = {"files": {}}
    for fname in FILES:
        path = RAW / fname
        print(f"\n=== {fname} ({path.stat().st_size} bytes) ===", flush=True)
        with open_workbook(path) as wb:
            sheet_names = list(wb.sheets)
        print(f"Sheets: {sheet_names}", flush=True)
        sheets = {}
        for sheet in sheet_names:
            sheets[sheet] = profile_sheet(path, sheet)
        report["files"][fname] = {
            "size_bytes": path.stat().st_size,
            "sheets": sheets,
        }

    out_json = OUT / "_perfil_raw_tmp.json"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_json}", flush=True)


if __name__ == "__main__":
    main()
