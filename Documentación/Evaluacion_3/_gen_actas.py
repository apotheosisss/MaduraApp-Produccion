# -*- coding: utf-8 -*-
"""Genera las 3 actas de avance (EP1, EP2, EP3) en PDF, con diseño propio."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

_FD = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Arial", os.path.join(_FD, "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(_FD, "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", os.path.join(_FD, "ariali.ttf")))
registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

GREEN = colors.HexColor("#2E7D32")
GREEN_D = colors.HexColor("#1B5E20")
LIGHT = colors.HexColor("#EAF3E9")
DARK = colors.HexColor("#1A1C19")
GRAY = colors.HexColor("#555B52")
LINE = colors.HexColor("#C1C9BD")
BASE = os.path.dirname(__file__)

ss = getSampleStyleSheet()
TITLE = ParagraphStyle("T", parent=ss["Normal"], fontName="Arial-Bold", fontSize=15, textColor=GREEN_D, leading=18, alignment=1)
SUBT = ParagraphStyle("ST", parent=ss["Normal"], fontName="Arial-Italic", fontSize=10, textColor=GRAY, leading=13, alignment=1)
H = ParagraphStyle("H", parent=ss["Normal"], fontName="Arial-Bold", fontSize=11, textColor=GREEN_D, spaceBefore=10, spaceAfter=4, leading=14)
BODY = ParagraphStyle("B", parent=ss["Normal"], fontName="Arial", fontSize=10, textColor=DARK, leading=14, alignment=4)
ITEM = ParagraphStyle("I", parent=ss["Normal"], fontName="Arial", fontSize=10, textColor=DARK, leading=14, leftIndent=6)
LBLV = ParagraphStyle("LV", parent=ss["Normal"], fontName="Arial", fontSize=10, textColor=DARK, leading=13)
LBLK = ParagraphStyle("LK", parent=ss["Normal"], fontName="Arial-Bold", fontSize=10, textColor=GREEN_D, leading=13)

ESTUDIANTE = "Claudio Vicente Aro Kath"
RUT = "22.022.498-8"
DOCENTE = "José Ignacio Campos Arévalo"


def build_acta(filename, num, subtitulo, fecha, entregables, resumen):
    doc = SimpleDocTemplate(os.path.join(BASE, filename), pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm, topMargin=16*mm, bottomMargin=16*mm)
    s = []

    # Banda superior
    banda = Table([[Paragraph('<font color="#FFFFFF"><b>MaduraApp</b></font>',
                              ParagraphStyle("x", fontName="Arial-Bold", fontSize=16)),
                    Paragraph('<font color="#D7EBD7">Análisis de madurez agrícola · TPY1101</font>',
                              ParagraphStyle("y", fontName="Arial", fontSize=9, alignment=2))]],
                   colWidths=[80*mm, 90*mm])
    banda.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (0, 0), 12), ("RIGHTPADDING", (1, 0), (1, 0), 12),
    ]))
    s.append(banda)
    s.append(Spacer(1, 10))
    s.append(Paragraph(f"ACTA DE AVANCE — EVALUACIÓN PARCIAL N&deg; {num}", TITLE))
    s.append(Paragraph(subtitulo, SUBT))
    s.append(Spacer(1, 10))

    # Tabla de datos
    def kv(k, v): return [Paragraph(k, LBLK), Paragraph(v, LBLV)]
    datos = Table([
        kv("Estudiante", ESTUDIANTE) + kv("RUT", RUT),
        kv("Asignatura", "Taller Aplicado de Programación (TPY1101)") + kv("Sección", "001D"),
        kv("Docente guía", DOCENTE) + kv("Fecha", fecha),
        kv("Proyecto", "MaduraApp — Visión computacional") + kv("Evaluación", f"Parcial N&deg; {num}"),
    ], colWidths=[28*mm, 57*mm, 22*mm, 63*mm])
    datos.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]))
    s.append(datos)

    # Entregables
    s.append(Paragraph("Entregables de esta evaluación", H))
    for e in entregables:
        s.append(Paragraph(f'<font color="#2E7D32"><b>&bull;</b></font>&nbsp;&nbsp;{e}', ITEM))

    # Resumen
    s.append(Paragraph("Resumen del avance", H))
    s.append(Paragraph(resumen, BODY))

    # Constancia
    s.append(Paragraph("Constancia", H))
    s.append(Paragraph("La presente acta deja constancia de los entregables desarrollados por el "
                       "estudiante en la evaluación indicada. La revisión, validación y calificación "
                       "final quedan sujetas al criterio del docente guía.", BODY))
    s.append(Spacer(1, 22))

    # Firmas (dos columnas)
    def firma(rol, nombre, extra):
        return [Paragraph('<font color="#999999">________________________________</font>',
                          ParagraphStyle("ln", fontName="Arial", fontSize=11, alignment=1)),
                Paragraph(f"<b>{rol}</b>", ParagraphStyle("r", fontName="Arial-Bold", fontSize=9.5, alignment=1, textColor=GREEN_D)),
                Paragraph(nombre, ParagraphStyle("n", fontName="Arial", fontSize=9.5, alignment=1, textColor=DARK)),
                Paragraph(extra, ParagraphStyle("e", fontName="Arial", fontSize=8.5, alignment=1, textColor=GRAY)),
                Paragraph("Fecha: ____ / ____ / ______", ParagraphStyle("f", fontName="Arial", fontSize=8.5, alignment=1, textColor=GRAY))]
    fcol1 = firma("FIRMA DEL ESTUDIANTE", ESTUDIANTE, f"RUT {RUT}")
    fcol2 = firma("FIRMA DEL DOCENTE GUÍA", DOCENTE, "Docente — TPY1101")
    firmas = Table([[fcol1[0], fcol2[0]], [fcol1[1], fcol2[1]], [fcol1[2], fcol2[2]],
                    [fcol1[3], fcol2[3]], [fcol1[4], fcol2[4]]], colWidths=[85*mm, 85*mm])
    firmas.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, 0), 2),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    s.append(firmas)

    doc.build(s)
    print("Acta:", filename)


build_acta(
    "Acta_Avance_EP1_MaduraApp.pdf", 1,
    "Definición del problema, requisitos y diseño inicial",
    "08 / 04 / 2026",
    ["Informe de Evaluación 1: definición del problema (pérdidas post-cosecha) y objetivos.",
     "Especificación de Requisitos de Software (ERS) con requisitos funcionales y no funcionales.",
     "Diagramas: casos de uso, Ishikawa (causa raíz) y carta Gantt del proyecto.",
     "Definición del alcance: 4 frutas climatéricas y 3 estados de madurez."],
    "En esta primera evaluación se delimitó la problemática de las pérdidas post-cosecha en frutas "
    "climatéricas y se propuso MaduraApp como solución basada en visión computacional. Se elaboró la "
    "ERS, se identificaron los requisitos y se definieron los objetivos y el alcance del proyecto, "
    "sentando la base para el diseño y desarrollo posteriores.",
)

build_acta(
    "Acta_Avance_EP2_MaduraApp.pdf", 2,
    "Arquitectura, desarrollo del producto y modelo de IA",
    "28 / 05 / 2026",
    ["Backend FastAPI con endpoints /predict, /history y /health (SQLAlchemy async + Alembic).",
     "Modelo YOLO26n entrenado: mAP@50 = 0,92 (supera el KPI de 0,75), 5,2 MB.",
     "App Android nativa (Kotlin + CameraX + Room + MVVM) con historial offline.",
     "Documentación de arquitectura 4+1 (Kruchten), informe técnico (Word) y presentación.",
     "Plan de pruebas inicial y suite automatizada (pytest + JUnit)."],
    "En la segunda evaluación se construyó el producto funcional: el backend con el modelo de IA "
    "desplegable y la aplicación Android completa, incluyendo captura por cámara, selección de fruta, "
    "semáforo de madurez e historial con cache offline. Se documentó la arquitectura bajo el modelo "
    "4+1 y se entregó el informe y la presentación correspondientes.",
)

build_acta(
    "Acta_Avance_EP3_MaduraApp.pdf", 3,
    "Plan de pruebas, validación, rendimiento y mejoras",
    "25 / 06 / 2026",
    ["Plan de pruebas con 57 casos automatizados (38 backend + 19 Android), 100% en verde.",
     "Pruebas de verificación del estado de madurez de la fruta (clase → estado/color/recomendación).",
     "Pruebas de validación, seguridad (OWASP) y base de datos de pruebas documentada.",
     "Pruebas de rendimiento y tiempos de respuesta bajo concurrencia (ambiente controlado).",
     "15 mejoras al producto (seguridad, usabilidad, corrección, completitud, pertinencia).",
     "Despliegue del backend en AWS (EC2 + Docker) e integración continua (GitHub Actions).",
     "Informe técnico, presentación de defensa y evidencias de pruebas."],
    "En la tercera evaluación se formalizó el aseguramiento de calidad: se diseñó y aplicó el plan de "
    "pruebas a todos los componentes (57 casos en verde), se midió el rendimiento bajo concurrencia y "
    "se aplicaron 15 mejoras derivadas de los resultados y de una auditoría de seguridad OWASP. "
    "Además se desplegó el backend en AWS y se incorporó integración continua, dejando el producto "
    "probado, seguro y funcional de extremo a extremo.",
)
print("Listo: 3 actas generadas.")
