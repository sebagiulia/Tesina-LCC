from system.ingesta_y_transformacion.dictamen.dictamen_composite import DictamenComposite
from system.ingesta_y_transformacion.dictamen.secciones.seccion_datos_principales import SeccionDatosPrincipales
from system.ingesta_y_transformacion.dictamen.secciones.seccion_fundamentos import SeccionFundamentos
from system.ingesta_y_transformacion.dictamen.secciones.seccion_incapacidad import SeccionIncapacidad


class Dictamen(DictamenComposite):
    """Raíz del Composite: un dictamen completo con las secciones presentes en la fuente."""

    def __init__(self, logger):
        self.logger = logger
        self.hijos = []

    def add(self, componente):
        self.hijos.append(componente)

    def getChildren(self):
        return list(self.hijos)

    def hasChild(self, nombre):
        return any(h.nombre() == nombre for h in self.hijos)

    def readFrom(self, reader):
        self.archivo = reader.readSection("dictamen").get("archivo")

        # Siempre presente: la arma el Reader con los datos de identificación.
        datos_principales = SeccionDatosPrincipales(self.logger)
        datos_principales.readFrom(reader)
        self.add(datos_principales)

        # Opcionales: se agregan solo si la fuente las contiene.
        if reader.readCount("seccionFundamentos"):
            fundamentos = SeccionFundamentos(self.logger)
            fundamentos.readFrom(reader)
            self.add(fundamentos)

        if reader.readCount("seccionIncapacidad"):
            incapacidad = SeccionIncapacidad(self.logger)
            incapacidad.readFrom(reader)
            self.add(incapacidad)

        self.logger.info(f"Dictamen {self.archivo}: secciones {[h.nombre() for h in self.hijos]}")

    def nombre(self):
        return self.archivo

    def detectar(self, visitor):
        for hijo in self.getChildren():
            hijo.detectar(visitor)
        visitor.visitar_dictamen(self)
