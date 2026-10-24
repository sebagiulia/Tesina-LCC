from abc import ABC, abstractmethod

from system.ingesta_y_transformacion.dictamen.dictamen_component import DictamenComponent


class DictamenComposite(DictamenComponent, ABC):
    """Sección del dictamen compuesta por otras secciones."""

    @abstractmethod
    def add(self, componente): ...

    @abstractmethod
    def getChildren(self) -> list: ...

    @abstractmethod
    def hasChild(self, nombre: str) -> bool:
        """Indica si tiene un componente hijo con el nombre indicado."""
