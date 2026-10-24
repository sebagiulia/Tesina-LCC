from system.deteccion.fuentes_conocimiento.condiciones.condicion import Condicion


# Dummy: reemplaza a MalaCargaNoDetectada como precondición de la regla de cálculo de incapacidad.
class SeccionIncapacidadCondicion(Condicion):
    """Se cumple si el dictamen tiene sección de incapacidad."""

    def __init__(self, logger):
        self.logger = logger

    def evaluar(self, blackboard):
        resultado = blackboard.dictamen().hasChild("Seccion Incapacidad")
        self.logger.info(f"SeccionIncapacidadCondicion: {resultado}")
        return resultado
