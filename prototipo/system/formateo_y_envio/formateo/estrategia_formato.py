from abc import ABC, abstractmethod


class EstrategiaFormato(ABC):
    """Consolida los resultados de todos los Blackboard en un Reporte."""

    @abstractmethod
    def formatear(self, blackboards: list): ...
