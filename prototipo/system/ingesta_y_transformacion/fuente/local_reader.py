import re
from pathlib import Path

from pypdf import PdfReader

from system.ingesta_y_transformacion.fuente.reader import Reader
from system.ingesta_y_transformacion.section_data import SectionData

# Títulos de sección tal como aparecen en el PDF del dictamen.
TITULOS = {
    "DATOS PRINCIPALES", "DAMNIFICADO", "FUNDAMENTOS Y DESCRIPCION DEL ACCIDENTE/ENFERMEDAD", "PREEXISTENCIAS",
    "EXAMEN FÍSICO", "ESTUDIOS Y/O DOCUMENTACIÓN PRESENTADA", "DIAGNÓSTICO", "CONCLUSIONES",
    "PRESTACIONES EN ESPECIE", "INCAPACIDAD", "Aclaración:", "FIRMAS Y ACLARACIONES",
}
FIN_ENCABEZADO = "Documento generado con datos ficticios"  # última línea del bloque repetido en cada página
CAMPO = re.compile(r"^([A-ZÁÉÍÓÚÑ][^:]{0,60}?):\s*(.*)$")       # "Clave: valor"
NUMERO = re.compile(r"^(\d+(?:\.\d+)?)%?$")                      # celda numérica de la tabla de incapacidad
CARPETA = Path(__file__).resolve().parents[3] / "datos" / "dictamenes"  # ubicación local de los PDF


# Dummy: reemplaza a PdfReader (lee PDF de una carpeta local en lugar del almacenamiento de la empresa).
class LocalReader(Reader):
    """Lee los dictámenes PDF de una carpeta e identifica sus secciones por los títulos."""

    def __init__(self, credentials, logger):
        self.credentials = credentials
        self.logger = logger
        self.archivos = sorted(CARPETA.glob("*.pdf"))
        self.valores, self.secciones = {}, {}
        logger.info(f"LocalReader: {len(self.archivos)} dictámenes en {CARPETA}")

    def hasNext(self):
        return bool(self.archivos)

    def readSection(self, clave):
        # "dictamen" avanza al próximo PDF; el resto devuelve la siguiente sección de ese tipo.
        if clave == "dictamen":
            self.cargar(self.archivos.pop(0))
        return self.secciones[clave].pop(0)

    def readCount(self, clave):
        return len(self.secciones.get(clave, []))

    def readString(self, clave):
        return self.valores.get(clave)

    def readFloat(self, clave):
        valor = self.valores.get(clave)
        return float(valor.rstrip("%")) if valor else None

    def readInt(self, clave):
        valor = self.readFloat(clave)
        return None if valor is None else int(valor)

    def cargar(self, archivo):
        """Extrae el texto del PDF, quita encabezados/pies y arma las secciones del dictamen."""
        self.logger.info(f"LocalReader: leyendo {archivo.name}")
        lineas, emision = [], None
        for pagina in PdfReader(archivo).pages:
            texto = pagina.extract_text().splitlines()
            corte = next(i for i, l in enumerate(texto) if l.startswith(FIN_ENCABEZADO))
            emision = emision or re.search(r"Emisión: (\S+)", "\n".join(texto[:corte])).group(1)
            lineas += [l.strip() for l in texto[corte + 1:] if l.strip()]

        titulos, actual = {}, None
        for linea in lineas:
            if linea in TITULOS:
                actual = titulos.setdefault(linea, [])
            elif actual is not None:
                actual.append(linea)

        datos = campos(titulos.get("DATOS PRINCIPALES", []) + titulos.get("DAMNIFICADO", []))
        fundamentos = campos(titulos.get("FUNDAMENTOS Y DESCRIPCION DEL ACCIDENTE/ENFERMEDAD", []))
        diagnostico = campos(titulos.get("DIAGNÓSTICO", []))
        conclusiones = campos(titulos.get("CONCLUSIONES", []))
        damnificado = datos.get("Damnificado", "").split(" - ")  # CUIL - NOMBRE - TIPO DOC - NRO

        self.valores = {}
        self.secciones = {
            "dictamen": [SectionData(archivo=archivo.name)],
            "seccionDatosPrincipales": [SectionData(
                fechaEmision=emision,
                expediente=datos.get("Nro. Expediente SRT"),
                damnificado=damnificado[1] if len(damnificado) > 1 else None,
                motivo=fundamentos.get("Motivo de la presentación"),
                diagnostico=diagnostico.get("Diagnóstico"),
                contingenciaDefinida=conclusiones.get("Contingencia definida al momento de dictaminar"),
            )],
        }
        if fundamentos:
            self.secciones["seccionFundamentos"] = [SectionData(
                tipoContingencia=fundamentos.get("Tipo de AT/EP"),
                descripcionContingencia=fundamentos.get("Descripción de la contingencia"),
                fecha=fundamentos.get("Fecha Accidente"),
            )]

        # La sección de incapacidad solo existe si el dictamen fija porcentaje (tiene la tabla de cálculo).
        incapacidad = titulos.get("INCAPACIDAD", [])
        if "Porcentaje total:" in incapacidad:
            total = incapacidad.index("Porcentaje total:")
            valores = campos(incapacidad[:incapacidad.index("Lesión")] + incapacidad[total + 2:])  # campos fuera de la tabla
            subtotal = next(i for i, l in enumerate(incapacidad) if l.startswith("SubTotal"))
            factores = incapacidad.index("Factores de ponderación")
            self.valores = {
                "incapacidadTotal": incapacidad[total + 1], "capacidadRestante": valores.get("Capacidad restante"),
                "tipo": valores.get("Tipo"), "grado": valores.get("Grado"), "caracter": valores.get("Caracter"),
            }
            self.secciones["seccionIncapacidad"] = [SectionData()]
            self.secciones["lesion"] = [
                SectionData(nombre=texto, porcentaje=numeros[-1])
                for texto, numeros in filas(incapacidad[incapacidad.index("Porcentaje(%)") + 1:subtotal])
            ]
            self.secciones["factorPonderacion"] = [
                SectionData(tipo=texto.partition(":")[0], descripcion=texto.partition(":")[2].strip(), ajuste=numeros[-1])
                for texto, numeros in filas(incapacidad[factores + 1:total])
            ]

        faltantes = [k for s in self.secciones.values() for d in s for k, v in d.valores.items() if v is None]
        if faltantes:
            self.logger.warning(f"LocalReader: campos no encontrados en {archivo.name}: {faltantes}")


def campos(lineas):
    """Agrupa líneas "Clave: valor"; las líneas sin clave continúan el valor anterior."""
    resultado, clave = {}, None
    for linea in lineas:
        coincidencia = CAMPO.match(linea)
        if coincidencia and coincidencia.group(1) not in resultado:
            clave = coincidencia.group(1)
            resultado[clave] = coincidencia.group(2)
        elif clave:
            resultado[clave] += " " + linea
    return resultado


def filas(lineas):
    """Agrupa las filas de la tabla de incapacidad: (texto de la fila, [números de sus columnas])."""
    resultado, texto, numeros = [], [], []
    for linea in lineas:
        coincidencia = NUMERO.match(linea)
        if coincidencia:
            numeros.append(float(coincidencia.group(1)))
            continue
        if numeros:
            resultado.append((" ".join(texto), numeros))
            texto, numeros = [], []
        texto.append(linea)
    if numeros:
        resultado.append((" ".join(texto), numeros))
    return resultado
