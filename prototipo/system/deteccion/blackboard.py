from system.deteccion.elementos_blackboard.analisis import Analisis
from system.deteccion.elementos_blackboard.resultado_regla import ResultadoRegla


class Blackboard:
    """Nivel 1: el dictamen (no se modifica). Nivel 2: un ResultadoRegla por regla. Nivel 3: los Analisis."""

    def __init__(self, dictamen):
        self.registrar_dictamen(dictamen)
        self._resultados, self._analisis = {}, {}

    def registrar_dictamen(self, dictamen):
        self._dictamen = dictamen

    def dictamen(self):
        return self._dictamen

    def registrar(self, elemento):
        # Python no tiene sobrecarga: registrar(ResultadoRegla) y registrar(Analisis) del diseño.
        if isinstance(elemento, ResultadoRegla):
            self._resultados[elemento.regla_id()] = elemento
        elif isinstance(elemento, Analisis):
            self._analisis[elemento.analisis_id()] = elemento

    def resultado_de(self, regla_id):
        return self._resultados.get(regla_id)

    def resultados(self):
        return list(self._resultados.values())

    def analisis_de(self, analisis_id):
        return self._analisis.get(analisis_id)

    def analisis(self):
        return list(self._analisis.values())
