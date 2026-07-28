"""Extrae resumen legible de la auditoría de claves."""
import json
from pathlib import Path

p = Path(
    r"c:\Users\stone\OneDrive\Escritorio\hoja de vida\Hv\Claro\Prueba_tecnica"
    r"\prueba_tecnica_especialista_datos\docs\modelo\_audit_claves_tmp.json"
)
r = json.loads(p.read_text(encoding="utf-8"))
v = r["ventas"]
print("=== VENTAS other candidates ===")
print(json.dumps(v["other_candidates"], indent=2, ensure_ascii=False))
print("=== col vary freq ===")
print(v["col_vary_freq"])
print("=== multi_* ===", v["multi_date"], v["multi_client"], v["multi_value"], v["multi_brand"])
print("=== weird ===", v["weird_short_codes"][:10])
print("=== samples count ===", len(v["samples"]))
for s in v["samples"][:3]:
    print("CODE", s["codigo"], "n", s["ocurrencias"], "vary", s["columnas_que_cambian"])
    for row in s["preview"][:3]:
        print(" ", row)
print("=== dup occurrence distribution ===")
from collections import Counter
c = Counter(x["ocurrencias"] for x in v["dup_list"])
print(dict(sorted(c.items())))
print("=== PRESUPUESTO ===")
print(json.dumps(r["presupuesto"], indent=2, ensure_ascii=False)[:3000])
print("=== REGISTROS ===")
print(json.dumps(r["registros"], indent=2, ensure_ascii=False))

# Write full dup list as csv for annex
out_csv = p.parent / "anexo_ventas_codigos_factura_duplicados.csv"
lines = ["codigo_factura,ocurrencias"]
for x in v["dup_list"]:
    lines.append(f"{x['codigo']},{x['ocurrencias']}")
out_csv.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", out_csv, "rows", len(v["dup_list"]))
