from system.ingesta_y_transformacion.dictamen.dictamen_leaf import DictamenLeaf


class Lesion(DictamenLeaf):
    """Lesión informada en la sección de incapacidad y su porcentaje."""

    def __init__(self, logger):
        self.logger = logger

    def readFrom(self, reader):
        self.datos = reader.readSection("lesion")

    def nombre(self):
        return self.datos.get("nombre")

    def porcentaje(self):
        return self.datos.get("porcentaje")

    def detectar(self, visitor):
        visitor.visitar_lesion(self)
