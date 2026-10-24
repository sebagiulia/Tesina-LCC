from datetime import datetime

from system.ingesta_y_transformacion.dictamen.dictamen_leaf import DictamenLeaf


class SeccionFundamentos(DictamenLeaf):
    """Sección "Fundamentos y descripción del accidente/enfermedad"."""

    def __init__(self, logger):
        self.logger = logger

    def readFrom(self, reader):
        self.datos = reader.readSection("seccionFundamentos")

    def nombre(self):
        return "Seccion Fundamentos"

    def tipoContingencia(self):
        return self.datos.get("tipoContingencia")

    def descripcionContingencia(self):
        return self.datos.get("descripcionContingencia")

    def fecha(self):
        """Fecha del accidente."""
        return datetime.strptime(self.datos.get("fecha"), "%d/%m/%Y").date()

    def detectar(self, visitor):
        visitor.visitar_seccion_fundamentos(self)
