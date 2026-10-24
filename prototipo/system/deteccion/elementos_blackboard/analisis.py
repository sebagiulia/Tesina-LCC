class Analisis:
    """Nivel 3 del Blackboard: resultado de un analizador.
    En el diseño hereda de ElemBB (trazabilidad), que no se implementa en el prototipo."""

    def __init__(self, analisis_id, analisis):
        self._analisis_id, self._analisis = analisis_id, analisis

    def analisis_id(self):
        return self._analisis_id

    def analisis(self):
        return self._analisis
