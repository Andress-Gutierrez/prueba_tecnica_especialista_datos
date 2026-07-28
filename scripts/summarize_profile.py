import json
from pathlib import Path

p = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\docs\analisis\_perfil_raw_tmp.json"
)
r = json.loads(p.read_text(encoding="utf-8"))
for fname, finfo in r["files"].items():
    print("=" * 60)
    print(fname, "size", finfo["size_bytes"])
    for sheet, s in finfo["sheets"].items():
        print(f"  SHEET {sheet}: {s['rows']}x{s['cols']} dups={s['duplicate_rows']}")
        for c in s["columns"]:
            top = ""
            if c.get("top_values"):
                items = list(c["top_values"].items())[:5]
                top = " | top=" + str(items)
            print(
                f"    - {c['name']}: dtype={c['dtype']} null%={c['null_pct']} "
                f"nunique={c['nunique']} sample={c['sample'][:5]}{top}"
            )
