# -*- coding: utf-8 -*-
"""Genera el guion de bolsillo de la defensa en PDF (formato celular)."""
import os
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Registrar Arial (Windows) — trae flechas, viñetas y acentos correctamente
_FD = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Arial", os.path.join(_FD, "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(_FD, "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", os.path.join(_FD, "ariali.ttf")))
registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

GREEN = colors.HexColor("#2E7D32")
AMBER = colors.HexColor("#9A6700")
DARK = colors.HexColor("#1A1C19")
GRAY = colors.HexColor("#555B52")

out = os.path.join(os.path.dirname(__file__), "Guion_Celular_Defensa.pdf")
doc = SimpleDocTemplate(out, pagesize=A5,
                        leftMargin=12*mm, rightMargin=12*mm,
                        topMargin=10*mm, bottomMargin=10*mm)

ss = getSampleStyleSheet()
H = ParagraphStyle("H", parent=ss["Normal"], fontName="Arial-Bold",
                   fontSize=13, textColor=GREEN, spaceBefore=8, spaceAfter=3, leading=15)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Arial-Italic",
                     fontSize=8.5, textColor=GRAY, spaceAfter=4, leading=11)
B = ParagraphStyle("B", parent=ss["Normal"], fontName="Arial",
                   fontSize=10, textColor=DARK, leftIndent=8, bulletIndent=0,
                   spaceAfter=2.5, leading=13)
TITLE = ParagraphStyle("TITLE", parent=ss["Normal"], fontName="Arial-Bold",
                       fontSize=17, textColor=GREEN, spaceAfter=2, leading=19)

story = []

def h(t): story.append(Paragraph(t, H))
def sub(t): story.append(Paragraph(t, SUB))
def b(t): story.append(Paragraph("•&nbsp; " + t, B))
def rule(): story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#C1C9BD"), spaceBefore=5, spaceAfter=5))

story.append(Paragraph("Guión de bolsillo — Defensa MaduraApp", TITLE))
sub("~14 min &middot; Habla con TUS palabras, no leas todo. Mira al jurado en las (CLAVE).")

h("Antes de empezar (en la sala)")
b("<b>Start Lab</b> &rarr; EC2 &rarr; <b>Iniciar instancia</b> &rarr; esperar 2-3 min")
b("Probar en el navegador del tel&eacute;fono: <font face='Courier'>http://3.215.43.61:8000/v1/health</font> &rarr; <b>model_loaded:true</b>")
b("App lista en el tel&eacute;fono")
rule()

slides = [
    ("1 &middot; Portada (~20s)", [
        "Saludo + tu nombre",
        "&ldquo;Defensa del Estado de Avance 3 de MaduraApp&rdquo;",
        "&ldquo;Hoy ver&aacute;n: el plan de pruebas, c&oacute;mo lo apliqu&eacute; y las mejoras&rdquo;",
    ]),
    ("2 &middot; Agenda (~20s)", [
        "Contexto &rarr; plan de pruebas &rarr; aplicaci&oacute;n y resultados &rarr; mejoras &rarr; conclusi&oacute;n",
    ]),
    ("3 &middot; Contexto (~1.5 min)", [
        "Problema: <b>20-40%</b> de p&eacute;rdida post-cosecha (FAO/ODEPA)",
        "Causa ra&iacute;z: no hay criterio <b>objetivo</b> de madurez",
        "Soluci&oacute;n: una foto &rarr; estado (inmaduro / &oacute;ptimo / sobremaduro) + recomendaci&oacute;n",
        "4 frutas: aguacate, pl&aacute;tano, tomate, mango",
        "Stack: Android (Kotlin) + API FastAPI + modelo <b>YOLO26n</b>",
        "Precisi&oacute;n <b>mAP@50 = 0.92</b> (meta era 0.75)",
    ]),
    ("4 &middot; Plan de pruebas (~2.5 min) (CLAVE)", [
        "<b>36 casos</b> automatizados &rarr; 17 backend + 19 Android",
        "4 tipos:",
        "&nbsp;&nbsp;&ndash; <b>Validaci&oacute;n</b> = &iquest;el sistema correcto? (requisitos)",
        "&nbsp;&nbsp;&ndash; <b>Verificaci&oacute;n</b> = &iquest;correctamente? (calidad)",
        "&nbsp;&nbsp;&ndash; <b>Seguridad</b> = OWASP",
        "&nbsp;&nbsp;&ndash; <b>Operacional</b> = funciona en su entorno",
        "BD de pruebas: <b>SQLite en memoria</b> &rarr; a&iacute;sla, r&aacute;pido, sin datos reales",
    ]),
    ("5 &middot; Aplicaci&oacute;n y resultados (~2 min)", [
        "<b>36/36 en verde</b> (ejecutadas hoy)",
        "backend 17/17 (pytest) &middot; Android 19/19 (MockK + JUnit)",
        "<b>Integraci&oacute;n continua</b>: la suite corre sola en cada cambio",
        "Calidad: modelo 0.92 &middot; 5.2 MB &middot; APK compila",
    ]),
    ("6 &middot; Mejoras (~2.5 min) (CLAVE)", [
        "&ldquo;Las mejoras <b>no son arbitrarias</b>: salen de las pruebas + auditor&iacute;a OWASP&rdquo;",
        "<b>Seguridad</b>: secreto JWT fuera del c&oacute;digo &middot; HTTPS &middot; token cifrado <b>AES-256</b>",
        "<b>Usabilidad</b>: rediseño Material 3 &middot; modo oscuro &middot; &iacute;conos vectoriales",
        "<b>Correcci&oacute;n</b>: suite y compilaci&oacute;n en verde",
        "<b>Completitud</b>: autenticaci&oacute;n + feedback end-to-end",
        "<b>Pertinencia</b>: recomendaciones del dominio agr&iacute;cola",
        "&ldquo;Cada mejora tiene un <b>commit</b> &rarr; trazable&rdquo;",
    ]),
    ("7 &middot; Seguridad (~1.5 min)", [
        "bcrypt (hash de contraseñas) &middot; JWT &middot; HTTPS (tr&aacute;nsito) &middot; AES-256 (reposo)",
        "(CLAVE) <b>&Eacute;tica</b>: &ldquo;No le pongo 'extremo a extremo' como WhatsApp porque <b>ser&iacute;a falso</b> &mdash; mi servidor necesita leer la imagen. Uso 'cifrado en tr&aacute;nsito'. La honestidad tambi&eacute;n es calidad.&rdquo;",
    ]),
    ("8 &middot; Conclusi&oacute;n (~1.5 min) (CLAVE)", [
        "Producto <b>funcional, probado y seguro</b>",
        "<b>36/36</b> pruebas &middot; <b>15 mejoras</b> &middot; datos protegidos",
        "Probado en producci&oacute;n: backend en <b>AWS (EC2 + Docker)</b>, escane&eacute; un <b>pl&aacute;tano real &rarr; &Oacute;ptimo</b>",
        "Pendiente honesto: pruebas E2E + su <b>aprobaci&oacute;n del plan</b> hoy",
    ]),
    ("9 &middot; Cierre (~10s)", [
        "&ldquo;Eso es todo. Gracias por su atenci&oacute;n. Quedo atento a sus preguntas.&rdquo;",
    ]),
]

for title, bullets in slides:
    h(title)
    for item in bullets:
        b(item)

rule()
h("Si me preguntan (respuestas r&aacute;pidas)")
qa = [
    "<b>&iquest;SQLite en memoria?</b> A&iacute;sla cada test, r&aacute;pido, sin datos reales.",
    "<b>&iquest;Por qu&eacute; mockean el modelo?</b> El test valida la l&oacute;gica de la API, no la red neuronal. La precisi&oacute;n se mide aparte (mAP).",
    "<b>&iquest;Validaci&oacute;n vs verificaci&oacute;n?</b> Validaci&oacute;n = sistema correcto. Verificaci&oacute;n = correctamente (calidad).",
    "<b>&iquest;Por qu&eacute; no E2E como WhatsApp?</b> El servidor necesita leer la imagen; ser&iacute;a falso. Es cifrado en tr&aacute;nsito + reposo.",
    "<b>&iquest;Qu&eacute; es OWASP?</b> El est&aacute;ndar de los 10 riesgos de seguridad m&aacute;s cr&iacute;ticos en apps.",
    "<b>&iquest;Qu&eacute; es mAP@50?</b> M&eacute;trica de precisi&oacute;n del modelo; 0.92 es muy alta (meta 0.75).",
    "<b>&iquest;Qu&eacute; falta?</b> Automatizar pruebas E2E y un despliegue permanente; el lab AWS es temporal.",
]
for item in qa:
    b(item)

rule()
story.append(Paragraph("<b>Tips:</b> respira en los puntos &middot; mira al jurado en las (CLAVE) &middot; si no sabes algo, recon&oacute;celo y explica c&oacute;mo lo averiguar&iacute;as.", SUB))

doc.build(story)
print("Guardado:", out)
