from abc import ABC, abstractmethod

from system.contexto_ejecucion.servicios.servicio_llm.llm_service import LLMService


class LLMDecorator(LLMService, ABC):
    """Decorator: las implementaciones reciben el LLMService decorado por constructor
    y procesar delega en él."""

    @abstractmethod
    def procesar(self, request): ...
