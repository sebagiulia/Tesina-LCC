from abc import ABC, abstractmethod


class ExecutionContext(ABC):
    """Abstract Factory de los servicios dependientes del entorno.
    Los servicios creados se inyectan por constructor; ningún módulo recibe el ExecutionContext."""

    @abstractmethod
    def createLoggingService(self): ...

    @abstractmethod
    def createLLMService(self): ...

    @abstractmethod
    def createCredentialsService(self): ...
