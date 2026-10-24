from system.deteccion.estrategias_control.estrategia_control import EstrategiaControl


# Dummy: reemplaza a MenorCostoPrimero / MayorAhorroPrimero.
class EstrategiaBasicaControl(EstrategiaControl):
    """Secuencial: elige la primera candidata en orden de registro."""

    def __init__(self, logger):
        self.logger = logger

    def elegir(self, candidatas):
        self.logger.info(f"EstrategiaBasicaControl: candidatas {[c.nombre() for c in candidatas]}")
        return candidatas[0]
