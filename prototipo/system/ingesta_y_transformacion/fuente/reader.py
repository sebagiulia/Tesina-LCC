from abc import ABC, abstractmethod

from system.ingesta_y_transformacion.section_data import SectionData


class Reader(ABC):
    """Reader del patrón Serializer: oculta la fuente (Backend) y el formato de los dictámenes.
    Las implementaciones reciben CredentialsService y LoggingService por constructor.
    readFloat no está en el diseño: se agrega porque los porcentajes son decimales."""

    @abstractmethod
    def hasNext(self) -> bool: ...

    @abstractmethod
    def readInt(self, clave: str) -> int: ...

    @abstractmethod
    def readFloat(self, clave: str) -> float: ...

    @abstractmethod
    def readString(self, clave: str) -> str: ...

    @abstractmethod
    def readSection(self, clave: str) -> SectionData:
        """Devuelve la siguiente sección del tipo indicado."""

    @abstractmethod
    def readCount(self, clave: str) -> int: ...
