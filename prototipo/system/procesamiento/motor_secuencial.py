from system.deteccion.blackboard import Blackboard
from system.procesamiento.motor_general import MotorGeneral


class MotorSecuencial(MotorGeneral):
    """Procesa los dictámenes uno tras otro, en orden de registro."""

    def __init__(self, control, logger):
        self.control = control
        self.logger = logger
        self.dictamenes = []

    def registrar(self, dictamen):
        self.dictamenes.append(dictamen)

    def ejecutar(self):
        blackboards = []
        for dictamen in self.dictamenes:
            self.logger.info(f"MotorSecuencial: procesando {dictamen.nombre()}")
            blackboard = Blackboard(dictamen)
            self.control.ejecutar(blackboard)
            blackboards.append(blackboard)
        return blackboards
