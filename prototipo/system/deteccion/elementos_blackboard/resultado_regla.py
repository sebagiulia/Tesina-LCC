from enum import Enum


class Estado(Enum):
    DETECTADO = "detectado"
    NO_DETECTADO = "no detectado"
    NO_EVALUADA = "no evaluada"  # su precondición no se cumplió


class ResultadoRegla:
    """Nivel 2 del Blackboard: resultado de una regla y su motivo.
    En el diseño hereda de ElemBB (trazabilidad), que no se implementa en el prototipo."""

    def __init__(self, regla_id, estado, motivo):
        self._regla_id, self._estado, self._motivo = regla_id, estado, motivo

    def regla_id(self):
        return self._regla_id

    def estado(self):
        return self._estado

    def motivo(self):
        return self._motivo
