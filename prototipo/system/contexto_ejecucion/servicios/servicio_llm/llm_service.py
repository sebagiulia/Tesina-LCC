from abc import ABC, abstractmethod

from system.contexto_ejecucion.servicios.servicio_llm.request import Request
from system.contexto_ejecucion.servicios.servicio_llm.response import Response


class LLMService(ABC):
    """Interfaz uniforme para ejecutar consultas sobre modelos de lenguaje (Component del Decorator)."""

    @abstractmethod
    def procesar(self, request: Request) -> Response: ...
