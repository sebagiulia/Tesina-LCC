from system.deteccion.fuentes_conocimiento.condiciones.condicion import Condicion


class TodasLasReglasEjecutadas(Condicion):
    """Se cumple si cada una de las reglas del sistema ya registró su ResultadoRegla."""

    REGLAS_ID = ["ReglaErrorCalculoIncapacidad", "ReglaErrorTipoContingencia"]

    def __init__(self, logger):
        self.logger = logger

    def evaluar(self, blackboard):
        return all(blackboard.resultado_de(regla_id) is not None for regla_id in self.REGLAS_ID)
