from abc import ABC, abstractmethod


class FuenteConocimiento(ABC):
    """Fuente de conocimiento del Blackboard: una precondición (delegada en la Condicion
    recibida por constructor) y una acción. nombre() no está en el diseño: identifica la fuente en el log."""

    @abstractmethod
    def nombre(self) -> str: ...

    @abstractmethod
    def precondicion(self, blackboard) -> bool: ...

    @abstractmethod
    def ejecutar(self, blackboard): ...
