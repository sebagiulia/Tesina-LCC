from system.ingesta_y_transformacion.dictamen.dictamen_leaf import DictamenLeaf


class FactorPonderacion(DictamenLeaf):
    """Factor de ponderación informado en la sección de incapacidad: su tipo y su ajuste."""

    def __init__(self, logger):
        self.logger = logger

    def readFrom(self, reader):
        self.datos = reader.readSection("factorPonderacion")

    def nombre(self):
        return self.datos.get("tipo")

    def tipo(self):
        return self.datos.get("tipo")

    def descripcion(self):
        return self.datos.get("descripcion")

    def ajuste(self):
        return self.datos.get("ajuste")

    def detectar(self, visitor):
        visitor.visitar_factor_ponderacion(self)
