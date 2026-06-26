# -*- coding: utf-8 -*-
"""Genera la Carta Gantt v3 de MaduraApp (3 iteraciones / evaluaciones)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import datetime as dt

G = "#2E7D32"; A = "#9A6700"; B = "#1565C0"; GR = "#555B52"
FASES = [
    # (tarea, inicio, fin, color, iteracion)
    ("EP1 · Definición del problema y ERS",        "2026-03-18", "2026-04-08", G,  "EP1"),
    ("EP1 · Diseño inicial y requisitos",          "2026-03-25", "2026-04-08", G,  "EP1"),
    ("EP2 · Arquitectura 4+1",                      "2026-04-09", "2026-04-30", A,  "EP2"),
    ("EP2 · Backend + modelo YOLO26n",              "2026-04-16", "2026-05-20", A,  "EP2"),
    ("EP2 · App Android (CameraX, Room, MVVM)",     "2026-04-23", "2026-05-25", A,  "EP2"),
    ("EP2 · Primera suite de pruebas + demo",       "2026-05-18", "2026-05-28", A,  "EP2"),
    ("EP3 · Auth JWT + feedback",                   "2026-05-29", "2026-06-10", B,  "EP3"),
    ("EP3 · Seguridad OWASP + rediseño UI",         "2026-06-08", "2026-06-18", B,  "EP3"),
    ("EP3 · Plan de pruebas (57) + cobertura",      "2026-06-12", "2026-06-21", B,  "EP3"),
    ("EP3 · Rendimiento + despliegue AWS",          "2026-06-18", "2026-06-24", B,  "EP3"),
    ("EP3 · Informe final y defensa",               "2026-06-21", "2026-06-25", B,  "EP3"),
]

def d(s): return dt.datetime.strptime(s, "%Y-%m-%d")
base = d(FASES[0][1])

fig, ax = plt.subplots(figsize=(12, 6.2))
for i, (tarea, ini, fin, color, _) in enumerate(FASES):
    y = len(FASES) - i - 1
    start = (d(ini) - base).days
    dur = (d(fin) - d(ini)).days
    ax.barh(y, dur, left=start, height=0.55, color=color, edgecolor="white")
    ax.text(start + dur + 1.5, y, tarea, va="center", ha="left", fontsize=9, color="#1A1C19")

# Hitos (evaluaciones)
for fecha, etiqueta in [("2026-04-08","EP1"), ("2026-05-28","EP2"), ("2026-06-25","EP3")]:
    x = (d(fecha) - base).days
    ax.axvline(x, color="#B00020", ls="--", lw=1, alpha=0.7)
    ax.text(x, len(FASES)-0.2, f"▲ {etiqueta} {fecha[8:]}/{fecha[5:7]}", color="#B00020",
            fontsize=8, ha="center", va="bottom", rotation=0)

ax.set_yticks([]); ax.set_xlim(0, 130)
ax.set_xlabel("Días desde el inicio del proyecto (18/03/2026)", fontsize=10)
ax.set_title("Carta Gantt — MaduraApp (v3)", fontsize=15, fontweight="bold", color=G, loc="left")
ax.grid(axis="x", color="#E2ECE0", lw=0.8)
ax.set_axisbelow(True)
for s in ["top","right","left"]: ax.spines[s].set_visible(False)
ax.legend(handles=[Patch(color=G, label="EP1 — Definición"),
                   Patch(color=A, label="EP2 — Producto"),
                   Patch(color=B, label="EP3 — Calidad")],
          loc="lower right", fontsize=9, frameon=False)
plt.tight_layout()

out_dir = os.path.join(os.path.dirname(__file__), "..", "diagramas")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "Gantt_MaduraApp_v3.png")
plt.savefig(out, dpi=140, bbox_inches="tight")
print("Guardado:", os.path.abspath(out))
