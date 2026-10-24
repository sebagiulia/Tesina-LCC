from abc import ABC

from system.deteccion.fuentes_conocimiento.fuente_conocimiento import FuenteConocimiento


class Analizador(FuenteConocimiento, ABC):
    """ejecutar procesa los ResultadoRegla del Blackboard y registra en él un Analisis."""
