from abc import ABC, abstractmethod


class EstrategiaControl(ABC):
    """Criterio para elegir, entre las fuentes de conocimiento candidatas, la próxima a ejecutar."""

    @abstractmethod
    def elegir(self, candidatas: list): ...
