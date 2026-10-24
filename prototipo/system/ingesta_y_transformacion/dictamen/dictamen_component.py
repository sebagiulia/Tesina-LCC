from abc import ABC, abstractmethod


class DictamenComponent(ABC):
    """Component del Composite, Serializable del Serializer y Element del Visitor.
    En el diseño hereda de ElemBB (trazabilidad), que no se implementa en el prototipo."""

    @abstractmethod
    def nombre(self) -> str: ...

    @abstractmethod
    def readFrom(self, reader):
        """Reconstruye el componente a partir del Reader."""

    @abstractmethod
    def detectar(self, visitor):
        """Delega en el método visitar_* del visitor que corresponde al tipo concreto."""
