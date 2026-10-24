from system.deteccion.fuentes_conocimiento.reglas.regla import Regla


class Control:
    """Coordina las fuentes de conocimiento sobre un Blackboard: chequea sus precondiciones
    y delega en la EstrategiaControl la elección de la próxima a ejecutar."""

    def __init__(self, estrategia, logger):
        self.estrategia = estrategia
        self.logger = logger
        self.fuentes = []

    def registrar(self, fuente):
        self.fuentes.append(fuente)

    def ejecutar(self, blackboard):
        pendientes = list(self.fuentes)
        while pendientes:
            candidatas = [f for f in pendientes if f.precondicion(blackboard)]
            if candidatas:
                fuente = self.estrategia.elegir(candidatas)
                self.logger.info(f"Control: ejecuta {fuente.nombre()}")
                fuente.ejecutar(blackboard)
                pendientes.remove(fuente)
                continue
            # Sin candidatas: las reglas pendientes ya no pueden evaluarse y registran NO_EVALUADA.
            reglas = [f for f in pendientes if isinstance(f, Regla)]
            if not reglas:
                break
            for regla in reglas:
                regla.ejecutar(blackboard)
                pendientes.remove(regla)
        for fuente in pendientes:
            self.logger.warning(f"Control: {fuente.nombre()} no se ejecutó (precondición no cumplida)")
