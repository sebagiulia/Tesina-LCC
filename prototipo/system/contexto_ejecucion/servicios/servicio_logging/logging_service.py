from abc import ABC, abstractmethod


class LoggingService(ABC):
    """Interfaz uniforme para registrar eventos generados durante la ejecución.
    Las implementaciones reciben un CredentialsService por constructor."""

    @abstractmethod
    def info(self, mensaje: str): ...

    @abstractmethod
    def warning(self, mensaje: str): ...

    @abstractmethod
    def error(self, mensaje: str): ...
