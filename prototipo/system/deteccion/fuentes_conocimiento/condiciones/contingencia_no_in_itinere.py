import re

from system.deteccion.fuentes_conocimiento.condiciones.condicion import Condicion


# ContingenciaNoInitinere en el diseño.
class ContingenciaNoInItinere(Condicion):
    """Se cumple si el campo Tipo de AT/EP no indica in itinere (evita una consulta innecesaria al LLM)."""

    def __init__(self, logger):
        self.logger = logger

    def evaluar(self, blackboard):
        dictamen = blackboard.dictamen()
        resultado = False
        if dictamen.hasChild("Seccion Fundamentos"):
            fundamentos = next(h for h in dictamen.getChildren() if h.nombre() == "Seccion Fundamentos")
            resultado = "itinere" not in re.sub(r"[\s-]", "", (fundamentos.tipoContingencia() or "").lower())
        self.logger.info(f"ContingenciaNoInItinere: {resultado}")
        return resultado
