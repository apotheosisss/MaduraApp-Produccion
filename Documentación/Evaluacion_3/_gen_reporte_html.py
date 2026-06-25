# -*- coding: utf-8 -*-
"""Genera un reporte HTML auto-contenido (un solo archivo) con los resultados
reales de las 36 pruebas: backend (pytest) + Android (JUnit)."""
import os, glob, html
import xml.etree.ElementTree as ET
from datetime import date

BASE = os.path.dirname(__file__)
BACKEND_XML = r"C:\Users\molte\AppData\Local\Temp\backend_junit.xml"
if not os.path.exists(BACKEND_XML):
    BACKEND_XML = "/tmp/backend_junit.xml"
ANDROID_DIR = os.path.join(BASE, "..", "..", "Producto", "frontend", "app",
                           "build", "test-results", "testDebugUnitTest")

FRIENDLY = {
    "tests.test_predict": "Backend — Inferencia y health (/predict, /health)",
    "tests.test_history": "Backend — Historial, autenticación y feedback",
    "cl.duoc.maduraapp.data.repository.FruitRepositoryTest": "Android — Repositorio y caché offline",
    "cl.duoc.maduraapp.ui.ScanViewModelTest": "Android — ViewModel de escaneo (estados UI)",
    "cl.duoc.maduraapp.ui.history.HistoryViewModelTest": "Android — ViewModel de historial",
}
ORDER = list(FRIENDLY.keys())

def parse(path):
    """Devuelve lista de (classname, name, ok, time)."""
    out = []
    tree = ET.parse(path)
    root = tree.getroot()
    suites = root.iter("testsuite")
    for ts in suites:
        for tc in ts.findall("testcase"):
            cls = tc.get("classname") or ts.get("name")
            name = tc.get("name")
            t = float(tc.get("time") or 0)
            ok = tc.find("failure") is None and tc.find("error") is None and tc.find("skipped") is None
            out.append((cls, name, ok, t))
    return out

cases = []
if os.path.exists(BACKEND_XML):
    cases += parse(BACKEND_XML)
for f in sorted(glob.glob(os.path.join(ANDROID_DIR, "*.xml"))):
    cases += parse(f)

# Agrupar por classname
groups = {}
for cls, name, ok, t in cases:
    groups.setdefault(cls, []).append((name, ok, t))

total = len(cases)
passed = sum(1 for c in cases if c[2])
failed = total - passed
n_backend = sum(len(v) for k, v in groups.items() if k.startswith("tests."))
n_android = total - n_backend

def esc(s): return html.escape(str(s))

rows = ""
ordered = ORDER + [k for k in groups if k not in ORDER]
for cls in ordered:
    if cls not in groups:
        continue
    items = groups[cls]
    grp_ok = sum(1 for _, ok, _ in items if ok)
    rows += f'<tr class="grp"><td colspan="3">{esc(FRIENDLY.get(cls, cls))} <span class="cnt">{grp_ok}/{len(items)}</span></td></tr>\n'
    for name, ok, t in items:
        badge = '<span class="ok">PASS</span>' if ok else '<span class="fail">FAIL</span>'
        rows += f'<tr><td class="st">{badge}</td><td class="nm">{esc(name)}</td><td class="tm">{t:.3f}s</td></tr>\n'

pct = round(passed / total * 100) if total else 0
hoy = date.today().strftime("%d-%m-%Y")

doc = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reporte de Pruebas — MaduraApp</title>
<style>
 *{{box-sizing:border-box}}
 body{{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f4f7f2;color:#1a1c19}}
 .wrap{{max-width:900px;margin:0 auto;padding:24px}}
 header{{background:#2E7D32;color:#fff;border-radius:14px;padding:22px 24px}}
 header h1{{margin:0;font-size:24px}}
 header p{{margin:4px 0 0;opacity:.9;font-size:14px}}
 .cards{{display:flex;gap:14px;margin:18px 0;flex-wrap:wrap}}
 .card{{flex:1;min-width:130px;background:#fff;border:1px solid #dde5da;border-radius:12px;padding:16px;text-align:center}}
 .card .big{{font-size:30px;font-weight:700;color:#2E7D32}}
 .card.fail .big{{color:#b00020}}
 .card .lbl{{font-size:13px;color:#555b52;margin-top:2px}}
 .bar{{height:12px;background:#e2ece0;border-radius:6px;overflow:hidden;margin:6px 0 18px}}
 .bar>i{{display:block;height:100%;background:#43A047;width:{pct}%}}
 table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #dde5da}}
 td{{padding:9px 12px;font-size:14px;border-top:1px solid #eef2ec}}
 tr.grp td{{background:#eef4ec;font-weight:600;color:#1b5e20;font-size:14px}}
 tr.grp .cnt{{float:right;color:#2E7D32}}
 .st{{width:64px}} .tm{{width:80px;text-align:right;color:#777;font-variant-numeric:tabular-nums}}
 .nm{{font-family:Consolas,monospace;font-size:13px}}
 .ok{{background:#dff3e1;color:#1b5e20;padding:2px 8px;border-radius:6px;font-size:12px;font-weight:600}}
 .fail{{background:#fde7ea;color:#b00020;padding:2px 8px;border-radius:6px;font-size:12px;font-weight:600}}
 footer{{margin:18px 0;color:#777;font-size:12px;text-align:center}}
</style></head>
<body><div class="wrap">
 <header>
   <h1>Reporte de Pruebas — MaduraApp</h1>
   <p>Estado de Avance 3 · TPY1101 · Claudio Vicente Aro Kath · {hoy}</p>
 </header>
 <div class="cards">
   <div class="card"><div class="big">{total}</div><div class="lbl">Pruebas totales</div></div>
   <div class="card"><div class="big">{passed}</div><div class="lbl">Aprobadas</div></div>
   <div class="card {'fail' if failed else ''}"><div class="big">{failed}</div><div class="lbl">Fallidas</div></div>
   <div class="card"><div class="big">{pct}%</div><div class="lbl">Éxito</div></div>
 </div>
 <div class="bar"><i></i></div>
 <p style="font-size:14px;color:#555b52;margin:0 0 8px">
   <b>{n_backend}</b> backend (pytest) · <b>{n_android}</b> Android (JUnit + MockK). Generado el {hoy}.
 </p>
 <table>{rows}</table>
 <footer>Reporte auto-contenido — funciona en cualquier navegador sin dependencias.</footer>
</div></body></html>"""

out = os.path.join(BASE, "Reporte_Pruebas_MaduraApp.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(doc)
print(f"Guardado: {out}")
print(f"Total {total} · passed {passed} · failed {failed} · backend {n_backend} · android {n_android}")
