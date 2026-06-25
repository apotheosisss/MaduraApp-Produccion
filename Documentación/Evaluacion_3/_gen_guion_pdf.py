# -*- coding: utf-8 -*-
"""Genera el guion DETALLADO de la defensa en PDF (formato celular A5)."""
import os
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, CondPageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

_FD = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Arial", os.path.join(_FD, "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(_FD, "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", os.path.join(_FD, "ariali.ttf")))
registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

GREEN = colors.HexColor("#2E7D32")
AMBER = colors.HexColor("#8A5A00")
DARK = colors.HexColor("#1A1C19")
GRAY = colors.HexColor("#555B52")

out = os.path.join(os.path.dirname(__file__), "Guion_Celular_Defensa.pdf")
doc = SimpleDocTemplate(out, pagesize=A5, leftMargin=11*mm, rightMargin=11*mm,
                        topMargin=9*mm, bottomMargin=9*mm)
ss = getSampleStyleSheet()
TITLE = ParagraphStyle("TITLE", parent=ss["Normal"], fontName="Arial-Bold", fontSize=16, textColor=GREEN, spaceAfter=2, leading=18)
H = ParagraphStyle("H", parent=ss["Normal"], fontName="Arial-Bold", fontSize=12, textColor=GREEN, spaceBefore=7, spaceAfter=2, leading=14)
LBL = ParagraphStyle("LBL", parent=ss["Normal"], fontName="Arial-Bold", fontSize=8.5, textColor=AMBER, spaceBefore=3, spaceAfter=1, leading=10)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontName="Arial", fontSize=9.5, textColor=DARK, spaceAfter=2, leading=12.5, alignment=4)
B = ParagraphStyle("B", parent=ss["Normal"], fontName="Arial", fontSize=9.5, textColor=DARK, leftIndent=9, spaceAfter=1.5, leading=12)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Arial-Italic", fontSize=8.5, textColor=GRAY, spaceAfter=3, leading=11)

story = []
def h(t): story.append(Paragraph(t, H))
def lbl(t): story.append(Paragraph(t, LBL))
def body(t): story.append(Paragraph(t, BODY))
def b(t): story.append(Paragraph("&bull;&nbsp; " + t, B))
def sub(t): story.append(Paragraph(t, SUB))
def rule(): story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#C1C9BD"), spaceBefore=5, spaceAfter=4))

story.append(Paragraph("Gui&oacute;n detallado &mdash; Defensa MaduraApp", TITLE))
sub("~14 min. Lee &ldquo;Di&rdquo; si te bloqueas; usa &ldquo;Clave&rdquo; para dar vistazos; &ldquo;Si profundizan&rdquo; es para el jurado.")

h("Antes de empezar (en la sala)")
b("<b>Start Lab</b> &rarr; consola AWS &rarr; <b>EC2 &rarr; Iniciar instancia</b> &rarr; esperar 2-3 min.")
b("Verificar en el navegador del tel&eacute;fono: <font face='Courier'>http://3.215.43.61:8000/v1/health</font> &rarr; debe decir <b>model_loaded:true</b>.")
b("Tener la app abierta y con sesi&oacute;n iniciada.")
rule()

SLIDES = [
    {
        "t": "Slide 1 &middot; Portada (~25s)",
        "di": "Buenos d&iacute;as. Mi nombre es Claudio Aro, secci&oacute;n cero cero uno D. Voy a defender el "
              "Estado de Avance 3 de mi proyecto MaduraApp, un sistema que analiza la madurez de frutas "
              "mediante visi&oacute;n computacional. En los pr&oacute;ximos quince minutos les mostrar&eacute; tres cosas: "
              "el plan de pruebas que dise&ntilde;&eacute;, c&oacute;mo lo apliqu&eacute; a cada componente del sistema, y las "
              "mejoras que hice a partir de esos resultados.",
        "clave": ["Nombre + secci&oacute;n.", "El objetivo en una frase: plan de pruebas, aplicaci&oacute;n y mejoras."],
    },
    {
        "t": "Slide 2 &middot; Agenda (~20s)",
        "di": "Voy a seguir esta ruta: primero el contexto del problema para situarlos; luego el coraz&oacute;n de "
              "esta evaluaci&oacute;n, que es el plan de pruebas, su aplicaci&oacute;n y los resultados; despu&eacute;s las mejoras "
              "que apliqu&eacute; al producto; y cierro con la conclusi&oacute;n y el trabajo pendiente.",
        "clave": ["5 puntos: contexto, plan, aplicaci&oacute;n, mejoras, conclusi&oacute;n."],
    },
    {
        "t": "Slide 3 &middot; Contexto del proyecto (~1.5 min)",
        "di": "Partamos por el problema. En Chile se pierde entre el veinte y el cuarenta por ciento de la fruta "
              "despu&eacute;s de la cosecha, seg&uacute;n la FAO y ODEPA. Una causa ra&iacute;z es que no existe una forma objetiva "
              "y accesible de saber cu&aacute;ndo una fruta est&aacute; en su punto &oacute;ptimo de consumo: la gente se gu&iacute;a por "
              "el ojo o el tacto, y se equivoca. MaduraApp resuelve esto con una foto: el usuario elige la fruta, "
              "toma una foto, y la aplicaci&oacute;n le entrega el estado de madurez &mdash;inmaduro, &oacute;ptimo o sobremaduro&mdash; "
              "con un sem&aacute;foro de colores y una recomendaci&oacute;n. Funciona con cuatro frutas: aguacate, pl&aacute;tano, "
              "tomate y mango. Por debajo, la app es Android nativo en Kotlin, el servidor es una API en FastAPI, "
              "y el modelo de inteligencia artificial es YOLO veintis&eacute;is, que entren&eacute; y que alcanza una precisi&oacute;n, "
              "medida en mAP cincuenta, de cero coma noventa y dos, muy por encima del objetivo de cero coma setenta y cinco.",
        "clave": ["<b>20-40%</b> p&eacute;rdida post-cosecha (FAO/ODEPA).", "4 frutas &times; 3 estados.",
                  "Stack: Android Kotlin + FastAPI + <b>YOLO26n</b>.", "<b>mAP@50 = 0.92</b> (meta 0.75)."],
        "prof": "Si preguntan por qu&eacute; YOLO: es un modelo de detecci&oacute;n de objetos en tiempo real, liviano "
                "(5,2 MB), que corre en CPU sin necesidad de GPU. Lo entren&eacute; con un conjunto de im&aacute;genes "
                "etiquetadas por estado de madurez.",
    },
    {
        "t": "Slide 4 &middot; Plan de pruebas (~2.5 min)  [CLAVE]",
        "di": "Vamos al plan de pruebas, el primer criterio de esta evaluaci&oacute;n. Dise&ntilde;&eacute; treinta y seis casos "
              "de prueba automatizados: diecisiete para el backend y diecinueve para la app Android. Y los organic&eacute; "
              "en cuatro tipos, porque no todas las pruebas verifican lo mismo. Las de validaci&oacute;n responden a la "
              "pregunta: &iquest;estoy construyendo el sistema correcto?, es decir, si cumple los requisitos. Las de "
              "verificaci&oacute;n responden: &iquest;lo estoy construyendo correctamente?, y miran calidad, como el rendimiento "
              "o la precisi&oacute;n. Las de seguridad las bas&eacute; en OWASP, el est&aacute;ndar de la industria. Y las operacionales "
              "verifican que el sistema funcione en su entorno. Un punto importante es la base de datos de pruebas: "
              "no uso la base real, uso una base SQLite en memoria que se crea y se destruye en cada corrida; esto "
              "a&iacute;sla cada prueba, es r&aacute;pido, y no expone datos reales de usuarios.",
        "clave": ["<b>36 casos</b> = 17 backend + 19 Android.",
                  "Validaci&oacute;n=requisitos &middot; Verificaci&oacute;n=calidad &middot; Seguridad=OWASP &middot; Operacional=entorno.",
                  "BD de pruebas: <b>SQLite en memoria</b> (a&iacute;sla, r&aacute;pido, sin datos reales)."],
        "prof": "Cada caso documenta: funcionalidad, acci&oacute;n o dato de entrada, resultado esperado y obtenido. "
                "Ejemplos reales: pedir <font face='Courier'>/predict</font> sin token devuelve 401; un formato de "
                "imagen no soportado devuelve 400; una contrase&ntilde;a d&eacute;bil al registrarse devuelve 422.",
    },
    {
        "t": "Slide 5 &middot; Aplicaci&oacute;n y resultados (~2 min)",
        "di": "Estos son los resultados de aplicar el plan. Las treinta y seis pruebas pasan al cien por ciento; "
              "las ejecut&eacute; hoy. El backend con pytest: diecisiete de diecisiete. La app Android con MockK y JUnit: "
              "diecinueve de diecinueve. Adem&aacute;s agregu&eacute; integraci&oacute;n continua: configur&eacute; un flujo en GitHub Actions "
              "que ejecuta toda la suite cada vez que subo un cambio, as&iacute; me entero de inmediato si algo rompe una "
              "prueba y no integro c&oacute;digo defectuoso. En calidad: el modelo cumple su objetivo con cero coma noventa "
              "y dos, pesa solo cinco coma dos megabytes, y la app compila e instala sin errores.",
        "clave": ["<b>36/36 en verde</b> (hoy).", "backend 17/17 (pytest) &middot; Android 19/19 (MockK+JUnit).",
                  "<b>Integraci&oacute;n continua</b> en cada push.", "Modelo 0.92 &middot; 5,2 MB &middot; APK OK."],
        "prof": "El backend prueba con pytest sobre SQLite en memoria; Android usa MockK para simular la API y la "
                "base Room, y kotlinx-coroutines-test para controlar la concurrencia de forma determinista. El CI "
                "es un workflow llamado backend_ci.yml.",
    },
    {
        "t": "Slide 6 &middot; Mejoras al producto (~2.5 min)  [CLAVE]",
        "di": "Este es, para m&iacute;, el punto m&aacute;s importante. Quiero destacar algo: estas mejoras no son arbitrarias. "
              "Cada una nace de un resultado de las pruebas o de una auditor&iacute;a de seguridad que hice con OWASP. Las "
              "mape&eacute; a los cinco est&aacute;ndares de calidad que pide la r&uacute;brica. En seguridad, que fue el foco: descubr&iacute; "
              "que la clave secreta de los tokens estaba escrita en el c&oacute;digo, que la informaci&oacute;n viajaba sin cifrar, "
              "y que el token se guardaba sin cifrar en el tel&eacute;fono; corregí las tres cosas. En usabilidad, redise&ntilde;&eacute; "
              "toda la interfaz con Material Design tres, con modo oscuro e &iacute;conos vectoriales. En correcci&oacute;n, dej&eacute; la "
              "suite y la compilaci&oacute;n en verde tras integrar las funciones nuevas. En completitud, integr&eacute; y prob&eacute; de "
              "extremo a extremo la autenticaci&oacute;n y el sistema de calificaci&oacute;n. Y en pertinencia, las recomendaciones "
              "est&aacute;n ajustadas al dominio agr&iacute;cola. Cada mejora tiene un commit que la respalda, as&iacute; que son trazables.",
        "clave": ["<b>15 mejoras</b>, todas trazables a un commit.",
                  "5 est&aacute;ndares: <b>seguridad, usabilidad, correcci&oacute;n, completitud, pertinencia</b>."],
        "prof": "Ejemplos concretos de seguridad: el secreto JWT estaba fijo en el c&oacute;digo &rarr; ahora va por variable "
                "de entorno y la app se niega a arrancar con el valor por defecto en producci&oacute;n. El token se guardaba "
                "en texto plano &rarr; ahora se cifra en reposo con EncryptedSharedPreferences (AES-256). El tr&aacute;fico iba "
                "en claro &rarr; ahora se fuerza HTTPS.",
    },
    {
        "t": "Slide 7 &middot; Seguridad / OWASP (~1.5 min)",
        "di": "Quiero profundizar un momento en seguridad, porque se trata de proteger los datos personales del "
              "usuario. Apliqu&eacute; OWASP punto por punto: las contrase&ntilde;as se guardan con un hash de bcrypt, nunca en "
              "texto plano. Los endpoints est&aacute;n protegidos con tokens JWT. La comunicaci&oacute;n va cifrada por HTTPS, eso "
              "es el cifrado en tr&aacute;nsito. Y el token se guarda cifrado en el dispositivo, eso es el cifrado en reposo. "
              "Y aqu&iacute; hay un punto de &eacute;tica que quiero mencionar: estuve tentado de mostrarle al usuario un mensaje "
              "tipo cifrado de extremo a extremo, como WhatsApp. Pero decid&iacute; no hacerlo, porque ser&iacute;a falso: mi "
              "servidor necesita leer la imagen para procesarla. Ser&iacute;a enga&ntilde;ar al usuario. As&iacute; que uso un mensaje "
              "veraz: tus datos viajan cifrados. La honestidad con el usuario tambi&eacute;n es parte de la calidad.",
        "clave": ["bcrypt (hash) &middot; JWT &middot; HTTPS (tr&aacute;nsito) &middot; AES-256 (reposo).",
                  "Argumento &eacute;tico: no es &ldquo;extremo a extremo&rdquo; porque el servidor lee la imagen."],
        "prof": "Diferencia clave: el hashing (bcrypt) es irreversible y se usa para contrase&ntilde;as; el cifrado (AES) "
                "es reversible con una clave y se usa para el token. En OWASP: A01 es control de acceso roto, A02 "
                "fallos criptogr&aacute;ficos, A07 fallos de autenticaci&oacute;n.",
    },
    {
        "t": "Slide 8 &middot; Conclusi&oacute;n (~1.5 min)  [CLAVE]",
        "di": "Para concluir. MaduraApp es hoy un producto funcional, probado y seguro. Treinta y seis de treinta y "
              "seis pruebas en verde, quince mejoras trazables a los est&aacute;ndares de calidad, y los datos personales "
              "protegidos con cifrado y hashing. De hecho, lo prob&eacute; en producci&oacute;n: desplegu&eacute; el backend en una "
              "instancia de AWS con Docker, y escane&eacute; un pl&aacute;tano real que diagnostic&oacute; como &oacute;ptimo correctamente. "
              "Y soy honesto con lo que queda pendiente: el despliegue, por ser un laboratorio acad&eacute;mico, es temporal; "
              "falta automatizar las pruebas de extremo a extremo, y obtener su aprobaci&oacute;n formal del plan de pruebas "
              "en esta misma defensa.",
        "clave": ["<b>36/36</b> &middot; <b>15 mejoras</b> &middot; datos protegidos.",
                  "Evidencia fuerte: <b>demo real en AWS</b> (pl&aacute;tano &rarr; &Oacute;ptimo).",
                  "Pendiente honesto: E2E + aprobaci&oacute;n del plan."],
    },
    {
        "t": "Slide 9 &middot; Cierre (~10s)",
        "di": "Eso es todo de mi parte. Muchas gracias por su atenci&oacute;n. Quedo atento a sus preguntas.",
        "clave": [],
    },
]

for s in SLIDES:
    story.append(CondPageBreak(28*mm))
    h(s["t"])
    lbl("DI:")
    body(s["di"])
    if s["clave"]:
        lbl("CLAVE (vistazo):")
        for c in s["clave"]:
            b(c)
    if s.get("prof"):
        lbl("SI PROFUNDIZAN:")
        body(s["prof"])

rule()
h("Glosario t&eacute;cnico (para no trabarte)")
GLO = [
    "<b>Validaci&oacute;n</b>: &iquest;el sistema correcto? (cumple requisitos). <b>Verificaci&oacute;n</b>: &iquest;correctamente? (calidad).",
    "<b>Prueba unitaria</b>: prueba una unidad aislada. <b>Integraci&oacute;n</b>: varios componentes juntos.",
    "<b>Fixture</b>: prepara datos antes de un test. <b>Mock</b>: objeto que simula una dependencia.",
    "<b>JWT</b>: token firmado que prueba la identidad en cada petici&oacute;n.",
    "<b>bcrypt / hash</b>: transformaci&oacute;n irreversible; la contrase&ntilde;a nunca se guarda en claro.",
    "<b>AES-256</b>: cifrado reversible con clave; protege el token en el dispositivo.",
    "<b>HTTPS / TLS</b>: cifra la comunicaci&oacute;n entre app y servidor (cifrado en tr&aacute;nsito).",
    "<b>OWASP</b>: lista est&aacute;ndar de los 10 riesgos de seguridad m&aacute;s cr&iacute;ticos en apps.",
    "<b>mAP@50</b>: m&eacute;trica de precisi&oacute;n del modelo (0.92 = muy alta).",
    "<b>CI</b>: integraci&oacute;n continua; corre las pruebas autom&aacute;ticamente en cada cambio.",
    "<b>Endpoint</b>: una ruta de la API (por ej. /predict, /history).",
]
for g in GLO:
    b(g)

rule()
h("Banco de preguntas (Q&amp;A)")
QA = [
    ("&iquest;Por qu&eacute; SQLite en memoria para las pruebas?",
     "Para aislar cada prueba (que una no contamine a otra), por velocidad y para no exponer datos reales. El esquema es el mismo de producci&oacute;n, as&iacute; que la prueba es representativa."),
    ("&iquest;Por qu&eacute; simulan (mockean) el modelo YOLO en los tests?",
     "Porque el test del endpoint valida la l&oacute;gica de la API &mdash;validaci&oacute;n de entrada, persistencia, respuesta&mdash;, no la red neuronal. As&iacute; es r&aacute;pido y determinista. La precisi&oacute;n del modelo se mide aparte con la m&eacute;trica mAP."),
    ("&iquest;Cu&aacute;l es la diferencia entre validaci&oacute;n y verificaci&oacute;n?",
     "Validaci&oacute;n responde si construyo el sistema correcto (cumple los requisitos del usuario). Verificaci&oacute;n, si lo construyo correctamente (atributos de calidad como rendimiento o precisi&oacute;n)."),
    ("&iquest;Por qu&eacute; no es cifrado de extremo a extremo como WhatsApp?",
     "Porque en extremo a extremo ni el servidor puede leer el contenido, y mi servidor necesita leer la imagen para procesarla y guardar el historial. Llamarlo as&iacute; ser&iacute;a falso. Uso el t&eacute;rmino correcto: cifrado en tr&aacute;nsito m&aacute;s cifrado en reposo."),
    ("&iquest;C&oacute;mo aseguran que las pruebas se ejecutan siempre?",
     "Con integraci&oacute;n continua: un workflow de GitHub Actions corre toda la suite en cada push. Si algo rompe una prueba, se detecta antes de integrar."),
    ("&iquest;De d&oacute;nde salieron las mejoras?",
     "De los resultados de las pruebas y de una auditor&iacute;a OWASP. Por ejemplo, al integrar la autenticaci&oacute;n, las pruebas quedaron en rojo y las corregí; y la auditor&iacute;a revel&oacute; el secreto JWT en el c&oacute;digo, que mov&iacute; a variable de entorno. Cada mejora tiene su commit."),
    ("&iquest;Qu&eacute; pasa si alguien intercepta la red?",
     "No ve nada &uacute;til: el tr&aacute;fico va cifrado por HTTPS, y la contrase&ntilde;a nunca viaja ni se guarda en claro porque se hashea con bcrypt."),
    ("&iquest;C&oacute;mo guardan la sesi&oacute;n en el tel&eacute;fono de forma segura?",
     "El token JWT se cifra en reposo con EncryptedSharedPreferences (AES-256) y la clave vive en el Android Keystore. Si extraen el archivo del dispositivo, no pueden leer el token."),
    ("&iquest;Qu&eacute; es mAP@50?",
     "Mean Average Precision con un umbral de solapamiento de 0,5; mide qu&eacute; tan bien el modelo detecta y clasifica. 0,92 es muy alta, sobre el objetivo de 0,75."),
    ("&iquest;Qu&eacute; cobertura tienen las pruebas?",
     "Los 36 casos cubren autenticaci&oacute;n, inferencia, historial, feedback, cach&eacute; offline y la capa de presentaci&oacute;n. Hay una matriz que relaciona cada requisito con las pruebas que lo cubren."),
    ("&iquest;Qu&eacute; falta o qu&eacute; mejorar&iacute;a?",
     "Desplegar el backend de forma permanente (el lab AWS es temporal), automatizar las pruebas de extremo a extremo &mdash;hoy la c&aacute;mara se prueba manualmente&mdash; y subir la cobertura."),
    ("&iquest;Por qu&eacute; Android nativo y no multiplataforma?",
     "Para aprovechar CameraX y el control fino de c&aacute;mara y rendimiento; el alcance del proyecto es Android."),
]
for q, a in QA:
    story.append(Paragraph("<b>P: " + q + "</b>", B))
    story.append(Paragraph("R: " + a, BODY))

rule()
sub("Tips: respira en los puntos &middot; mira al jurado en las secciones [CLAVE] &middot; si no sabes algo, recon&oacute;celo y explica c&oacute;mo lo averiguar&iacute;as &middot; habla de decisiones y porqu&eacute;s, no solo de lo que hiciste.")

doc.build(story)
print("Guardado:", out)

# Exportar tambien a Markdown (mismo contenido) para lectura web/repo
import html, re
def clean(t):
    t = (t.replace("&mdash;", "—").replace("&rarr;", "→").replace("&middot;", "·")
          .replace("&times;", "×").replace("&ldquo;", "“").replace("&rdquo;", "”")
          .replace("&iquest;", "¿").replace("&amp;", "&").replace("&nbsp;", " ")
          .replace("&bull;", "•"))
    t = html.unescape(t)
    t = re.sub(r"</?b>", "**", t)
    t = re.sub(r"<font[^>]*>", "`", t).replace("</font>", "`")
    return t
mdp = os.path.join(os.path.dirname(__file__), "Guion_Celular_Defensa.md")
with open(mdp, "w", encoding="utf-8") as f:
    f.write("# Guión detallado — Defensa MaduraApp\n\n")
    f.write("> ~14 min. **Di** = texto completo (si te bloqueas) · **Clave** = vistazo rápido · "
            "**Si profundizan** = para el jurado.\n\n")
    f.write("## Antes de empezar\n- Start Lab → EC2 → Iniciar instancia → esperar 2-3 min.\n"
            "- Verificar: `http://3.215.43.61:8000/v1/health` → `model_loaded:true`.\n"
            "- App abierta con sesión iniciada.\n\n")
    for s in SLIDES:
        f.write(f"## {clean(s['t'])}\n\n**Di:** {clean(s['di'])}\n\n")
        if s["clave"]:
            f.write("**Clave:**\n")
            for c in s["clave"]:
                f.write(f"- {clean(c)}\n")
            f.write("\n")
        if s.get("prof"):
            f.write(f"**Si profundizan:** {clean(s['prof'])}\n\n")
    f.write("## Glosario técnico\n")
    for g in GLO:
        f.write(f"- {clean(g)}\n")
    f.write("\n## Banco de preguntas\n")
    for q, a in QA:
        f.write(f"- **P: {clean(q)}** R: {clean(a)}\n")
print("Markdown guardado:", mdp)
