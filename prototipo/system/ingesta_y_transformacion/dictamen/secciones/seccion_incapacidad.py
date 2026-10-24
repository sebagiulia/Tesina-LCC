from system.ingesta_y_transformacion.dictamen.dictamen_composite import DictamenComposite
from system.ingesta_y_transformacion.dictamen.secciones.factor_ponderacion import FactorPonderacion
from system.ingesta_y_transformacion.dictamen.secciones.lesion import Lesion


class SeccionIncapacidad(DictamenComposite):
    """Sección de incapacidad: contiene componentes Lesion y FactorPonderacion (como en la tesis)."""

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
        self.incapacidad = reader.readFloat("incapacidadTotal")
        self.capRestante = reader.readFloat("capacidadRestante")
        # Datos de la conclusión de la sección, usados por el reporte.
        self.datos = {clave: reader.readString(clave) for clave in ("tipo", "grado", "caracter")}

        for _ in range(reader.readCount("lesion")):
            lesion = Lesion(self.logger)
            lesion.readFrom(reader)
            self.add(lesion)

        for _ in range(reader.readCount("factorPonderacion")):
            factor = FactorPonderacion(self.logger)
            factor.readFrom(reader)
            self.add(factor)
        self.logger.info(f"SeccionIncapacidad: total {self.incapacidad} %, {len(self.hijos)} componentes")

    def nombre(self):
        return "Seccion Incapacidad"

    def incapacidadTotal(self):
        return self.incapacidad

    def capacidadRestante(self):
        return self.capRestante

    def tipo(self):
        return self.datos["tipo"]

    def grado(self):
        return self.datos["grado"]

    def caracter(self):
        return self.datos["caracter"]

    def detectar(self, visitor):
        for hijo in self.getChildren():
            hijo.detectar(visitor)
        visitor.visitar_seccion_incapacidad(self)
