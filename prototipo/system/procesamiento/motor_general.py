from abc import ABC, abstractmethod


class MotorGeneral(ABC):
    """Algoritmo de procesamiento general: un Blackboard por cada dictamen registrado,
    delegando en el Control (recibido por constructor) la ejecución sobre cada uno."""

    @abstractmethod
    def registrar(self, dictamen): ...

    @abstractmethod
    def ejecutar(self) -> list: ...
