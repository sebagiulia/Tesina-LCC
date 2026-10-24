from system.deteccion.elementos_blackboard.resultado_regla import Estado, ResultadoRegla
from system.deteccion.fuentes_conocimiento.fuente_conocimiento import FuenteConocimiento
from system.deteccion.fuentes_conocimiento.reglas.visitors.dictamen_visitor import ErrorDetectado


class Regla(FuenteConocimiento):
    """Regla de negocio: compone una Condicion (precondición) y un DictamenVisitor (acción)."""

    def __init__(self, id, condicion, visitor, logger):
        self.id = id
        self.condicion = condicion
        self.visitor = visitor
        self.logger = logger

    def nombre(self):
        return self.id

    def precondicion(self, blackboard):
        return self.condicion.evaluar(blackboard)

    def ejecutar(self, blackboard):
        if not self.precondicion(blackboard):
            resultado = ResultadoRegla(self.id, Estado.NO_EVALUADA, f"No se cumple {type(self.condicion).__name__}")
        else:
            try:
                blackboard.dictamen().detectar(self.visitor)
                resultado = ResultadoRegla(self.id, Estado.NO_DETECTADO, "")
            except ErrorDetectado as error:
                resultado = ResultadoRegla(self.id, Estado.DETECTADO, error.motivo)
        self.logger.info(f"{self.id} sobre {blackboard.dictamen().nombre()}: {resultado.estado().value}")
        blackboard.registrar(resultado)
