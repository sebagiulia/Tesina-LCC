from abc import ABC, abstractmethod


class Condicion(ABC):
    """Condición de aplicabilidad (dependencia) evaluada sobre el Blackboard."""

    @abstractmethod
    def evaluar(self, blackboard) -> bool: ...
