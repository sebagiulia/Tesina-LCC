from abc import ABC, abstractmethod


class Sender(ABC):
    """Contexto del Strategy de formato. Las implementaciones reciben EstrategiaFormato,
    LoggingService y CredentialsService por constructor: generar delega la construcción
    del Reporte en la EstrategiaFormato y enviar lo entrega al destino."""

    @abstractmethod
    def generar(self, blackboards): ...

    @abstractmethod
    def enviar(self): ...
