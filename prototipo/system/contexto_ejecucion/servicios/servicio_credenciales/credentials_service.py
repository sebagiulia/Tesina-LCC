from abc import ABC, abstractmethod


class CredentialsService(ABC):
    """Interfaz uniforme para acceder a las credenciales requeridas por el sistema."""

    @abstractmethod
    def get(self, clave: str) -> str: ...
