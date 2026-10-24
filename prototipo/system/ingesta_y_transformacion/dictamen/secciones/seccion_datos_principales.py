from datetime import datetime

from system.ingesta_y_transformacion.dictamen.dictamen_leaf import DictamenLeaf


class SeccionDatosPrincipales(DictamenLeaf):
    """Datos de identificación del dictamen: emisión, expediente, damnificado, motivo,
    diagnóstico y contingencia definida (títulos DATOS PRINCIPALES, DAMNIFICADO, DIAGNÓSTICO y CONCLUSIONES)."""

    def __init__(self, logger):
        self.logger = logger

    def readFrom(self, reader):
        self.datos = reader.readSection("seccionDatosPrincipales")

    def nombre(self):
        return "Seccion Datos Principales"

    def fechaEmision(self):
        return datetime.strptime(self.datos.get("fechaEmision"), "%d/%m/%Y").date()

    def expediente(self):
        return self.datos.get("expediente")

    def nroReporte(self):
        """Número con el que se identifica el dictamen en el informe: el Nro. Expediente SRT."""
        return self.datos.get("expediente")

    def damnificado(self):
        return self.datos.get("damnificado")

    def motivo(self):
        return self.datos.get("motivo")

    def diagnostico(self):
        return self.datos.get("diagnostico")

    def contingenciaDefinida(self):
        return self.datos.get("contingenciaDefinida")

    def detectar(self, visitor):
        visitor.visitar_seccion_datos_principales(self)
