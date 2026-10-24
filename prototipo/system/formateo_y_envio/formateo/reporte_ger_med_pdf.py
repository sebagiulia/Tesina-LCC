import io
import json
import re
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from system.deteccion.elementos_blackboard.resultado_regla import Estado
from system.formateo_y_envio.formateo.estrategia_formato import EstrategiaFormato
from system.formateo_y_envio.formateo.reporte import Reporte

FUENTES = "/usr/share/fonts/truetype/dejavu/"
for _nombre in ("DejaVuSans", "DejaVuSans-Bold", "DejaVuSerif", "DejaVuSerif-Bold"):
    pdfmetrics.registerFont(TTFont(_nombre, FUENTES + _nombre + ".ttf"))
pdfmetrics.registerFontFamily("DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold",
                              italic="DejaVuSans", boldItalic="DejaVuSans-Bold")  # <b> en los párrafos

AZUL, CELESTE, ROJO = colors.HexColor("#13294b"), colors.HexColor("#2b6f8f"), colors.HexColor("#b3261e")
GRIS, FONDO, LINEA, ROSA = colors.HexColor("#5f6b7a"), colors.HexColor("#eef1f6"), colors.HexColor("#c5cfdb"), colors.HexColor("#fbf1f0")
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
NUMEROS = ["ningún", "un", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"]
ANCHO = A4[0] - 4 * cm


def estilo(fuente="DejaVuSans", tam=9, color=colors.black, **kw):
    return ParagraphStyle("e", fontName=fuente, fontSize=tam, leading=tam * 1.4, textColor=color, **kw)


def larga(fecha):
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def cantidad(n, singular, plural):
    return f"{NUMEROS[n] if n < len(NUMEROS) else n} {singular if n == 1 else plural}"


def secciones(bb):
    """Secciones del dictamen del Blackboard, indexadas por nombre."""
    return {h.nombre(): h for h in bb.dictamen().getChildren()}


class PaginadoCanvas(canvas.Canvas):
    """Canvas que escribe "Página x de N" al final, cuando ya se conoce N."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginas = []

    def showPage(self):
        self.paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for pagina in self.paginas:
            self.__dict__.update(pagina)
            self.setFont("DejaVuSans", 7)
            self.setFillColor(GRIS)
            self.drawRightString(A4[0] - 2 * cm, 1.3 * cm, f"Página {self._pageNumber} de {len(self.paginas)}")
            super().showPage()
        super().save()


class ReporteGerMedPDF(EstrategiaFormato):
    """Informe diario en PDF para la Gerencia Médica: portada con totales y una página por dictamen
    con errores, con sus fundamentos (Analisis del ResumenAnalizador)."""

    def __init__(self, logger):
        self.logger = logger

    def formatear(self, blackboards):
        emisiones = sorted({secciones(bb)["Seccion Datos Principales"].fechaEmision() for bb in blackboards})
        if len(emisiones) > 1:
            self.logger.warning(f"ReporteGerMedPDF: dictámenes con distintas fechas de emisión {emisiones}")
        emision = emisiones[0]
        con_errores = [bb for bb in blackboards if bb.analisis()]
        alertas = sum(r.estado() == Estado.DETECTADO for bb in blackboards for r in bb.resultados())

        historia = self.portada(emision, len(blackboards), alertas, con_errores)
        for bb in con_errores:
            historia += [PageBreak()] + self.pagina_dictamen(bb)

        buffer = io.BytesIO()
        titulo = f"Informe Diario - Detección de errores en dictámenes médicos ({emision:%d/%m/%Y})"
        doc = SimpleDocTemplate(buffer, pagesize=A4, title=titulo, author="Analytics",
                                leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2.2 * cm, bottomMargin=2.2 * cm)
        doc.build(historia, onFirstPage=lambda c, d: self.fondo_portada(c, emision),
                  onLaterPages=lambda c, d: self.fondo_interior(c, emision), canvasmaker=PaginadoCanvas)
        self.logger.info(f"ReporteGerMedPDF: {len(blackboards)} dictámenes, {alertas} alertas")
        return Reporte(buffer.getvalue(), [f"Informe_Diario_Dictamenes_{emision:%d-%m-%Y}.pdf", titulo])

    def portada(self, emision, analizados, alertas, con_errores):
        datos = Table([[Paragraph(etiqueta, estilo("DejaVuSans-Bold", 7.5, GRIS)), Paragraph(valor, estilo(tam=8.5))]
                       for etiqueta, valor in (("Fecha de emisión de los dictámenes", larga(emision)),
                                               ("Fecha de elaboración del informe", larga(date.today())),
                                               ("Destinatario", "Gerencia Médica"), ("Elaborado por", "Analytics"))],
                      colWidths=[6 * cm, ANCHO - 6 * cm])
        datos.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -2), 0.5, LINEA), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        centro = {"alignment": 1}
        kpis = Table([[[Paragraph(str(n), estilo("DejaVuSerif-Bold", 20, color, **centro)), Spacer(1, 6),
                        Paragraph(texto, estilo(tam=7, color=GRIS, **centro))]
                       for n, texto, color in ((analizados, "Dictámenes<br/>analizados", AZUL),
                                               (alertas, "Alertas<br/>detectadas", ROJO))]],
                     colWidths=[ANCHO / 2] * 2)
        kpis.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FONDO), ("LINEAFTER", (0, 0), (0, 0), 1.5, colors.white),
                                  ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))

        objeto = ("El presente informe reúne los resultados del control automático aplicado a la totalidad de los "
                  f"dictámenes médicos emitidos el {emision:%d/%m/%Y}. ")
        if con_errores:
            titulos = {}
            for bb in con_errores:
                for a in bb.analisis():
                    titulo = json.loads(a.analisis())["titulo"].lower()
                    titulos[titulo] = titulos.get(titulo, 0) + 1
            errores = [cantidad(n, *(t, t.replace("error", "errores", 1))) for t, n in titulos.items()]
            objeto += ("A los fines de su elevación a la Gerencia Médica, se detallan en las páginas siguientes "
                       + ("el dictamen en el que" if len(con_errores) == 1
                          else f"los {cantidad(len(con_errores), '', 'dictámenes en los que')}")
                       + " se identificaron "
                       f"inconsistencias: {', '.join(errores[:-1]) + ' y ' + errores[-1] if len(errores) > 1 else errores[0]}.")
        else:
            objeto += "No se identificaron inconsistencias en los dictámenes analizados."

        return [Spacer(1, 7.2 * cm), datos, Spacer(1, 1.2 * cm), kpis, Spacer(1, 0.9 * cm),
                Paragraph("Objeto del informe", estilo("DejaVuSans-Bold", 9.5, AZUL, spaceAfter=3)),
                Paragraph(objeto, estilo(tam=8.5))]

    def pagina_dictamen(self, bb):
        dictamen = bb.dictamen()
        datos = secciones(bb)["Seccion Datos Principales"]
        fundamentos = secciones(bb).get("Seccion Fundamentos")
        incapacidad = secciones(bb).get("Seccion Incapacidad")
        nro_reporte = datos.nroReporte()
        apellido, *nombres = (datos.damnificado() or "").split()
        dictaminada = (f"{incapacidad.incapacidadTotal():.2f}".replace(".", ",") + " % · " +
                       " · ".join(v.capitalize() for v in (incapacidad.tipo(), incapacidad.grado(), incapacidad.caracter()))
                       if incapacidad else "No fija porcentaje")
        filas = [("Nombre del trabajador", " ".join(nombres + [apellido]).title()),
                 ("Expediente", f"SRT {datos.expediente()}"),
                 ("Tipo de contingencia", fundamentos.tipoContingencia() if fundamentos else "—"),
                 ("Motivo de presentación", datos.motivo()),
                 ("Diagnóstico", re.sub(r"^([A-Z]\d\d)(\d) - ", r"\1.\2 – ", datos.diagnostico() or "")),
                 ("Incapacidad dictaminada", dictaminada)]
        tabla = Table([[Paragraph(e, estilo("DejaVuSans-Bold", 7.5, GRIS)),
                        Paragraph(v, estilo("DejaVuSans-Bold" if i == 0 else "DejaVuSans", 8.5))]
                       for i, (e, v) in enumerate(filas)], colWidths=[4.3 * cm, ANCHO - 4.3 * cm])
        tabla.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, LINEA), ("BACKGROUND", (0, 0), (0, -1), FONDO),
                                   ("BACKGROUND", (1, 0), (1, 0), FONDO), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))

        analisis = [json.loads(a.analisis()) for a in bb.analisis()]
        historia = [Paragraph("Dictamen Médico", estilo(tam=8.5, color=GRIS)),
                    Paragraph(f"Nro. Reporte: {nro_reporte}", estilo("DejaVuSerif-Bold", 15, AZUL, spaceAfter=8)),
                    tabla, Spacer(1, 0.7 * cm),
                    Paragraph(f"Errores detectados ({len(analisis)})", estilo("DejaVuSans-Bold", 9.5, AZUL, spaceAfter=6))]
        for i, error in enumerate(analisis, start=1):
            historia += [self.caja_error(i, error), Spacer(1, 0.4 * cm)]
        self.logger.info(f"ReporteGerMedPDF: página {nro_reporte} para {dictamen.nombre()}")
        return historia

    def caja_error(self, i, error):
        detalle = Table([[Paragraph(c, estilo("DejaVuSans-Bold", 7.5, AZUL)) for c in ("Concepto", "Informado", "Esperado")]]
                        + [[Paragraph(f"<b>{c}</b>" if j == 0 else c, estilo(tam=7.5)) for j, c in enumerate(fila)]
                           for fila in error["filas"]],
                        colWidths=[(ANCHO - 1.2 * cm) * p for p in (0.52, 0.24, 0.24)])
        detalle.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, LINEA), ("TOPPADDING", (0, 0), (-1, -1), 2),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        caja = Table([[Paragraph(f"Error {i}: {error['titulo']}", estilo("DejaVuSans-Bold", 9, ROJO))],
                      [Paragraph(f"<b>Justificación:</b> {error['justificacion']}", estilo(tam=8.5))],
                      [detalle]], colWidths=[ANCHO])
        caja.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ROSA), ("LINEBEFORE", (0, 0), (0, -1), 2.5, ROJO),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                                  ("BOTTOMPADDING", (0, -1), (-1, -1), 12)]))
        return caja

    def fondo_portada(self, c, emision):
        alto, ancho = A4[1], A4[0]
        c.setFillColor(AZUL)
        c.rect(0, alto - 9 * cm, ancho, 9 * cm, stroke=0, fill=1)
        c.setFillColor(CELESTE)
        c.rect(0, alto - 9.2 * cm, ancho, 0.2 * cm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("DejaVuSans", 7.5)
        c.drawString(2.4 * cm, alto - 1.9 * cm, "GERENCIA MÉDICA")
        c.setFont("DejaVuSerif-Bold", 24)
        c.drawString(2.4 * cm, alto - 4.6 * cm, "Informe Diario")
        c.setFont("DejaVuSerif", 12)
        c.drawString(2.4 * cm, alto - 5.6 * cm, "Detección de errores en dictámenes médicos")
        c.setFillColor(colors.HexColor("#b8c4d6"))
        c.setFont("DejaVuSans", 8.5)
        c.drawString(2.4 * cm, alto - 6.6 * cm, f"Dictámenes emitidos el {larga(emision)}")
        self.pie(c, "Documento generado por el sistema de detección automática de inconsistencias")

    def fondo_interior(self, c, emision):
        alto, ancho = A4[1], A4[0]
        c.setFillColor(AZUL)
        c.rect(0, alto - 1.2 * cm, ancho, 1.2 * cm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("DejaVuSans-Bold", 7)
        c.drawString(2 * cm, alto - 0.75 * cm, "INFORME DIARIO · DETECCIÓN DE ERRORES EN DICTÁMENES MÉDICOS")
        c.setFont("DejaVuSans", 7)
        c.drawRightString(ancho - 2 * cm, alto - 0.75 * cm, f"Emisión: {emision:%d/%m/%Y}")
        self.pie(c, "Gerencia Médica · Área de Auditoría y Control de Calidad · Uso interno · Confidencial")

    def pie(self, c, texto):
        c.setStrokeColor(LINEA)
        c.line(2 * cm, 1.7 * cm, A4[0] - 2 * cm, 1.7 * cm)
        c.setFillColor(GRIS)
        c.setFont("DejaVuSans", 7)
        c.drawString(2 * cm, 1.3 * cm, texto)
