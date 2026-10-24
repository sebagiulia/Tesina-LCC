from abc import ABC

from system.contexto_ejecucion.servicios.servicio_llm.llm_service import LLMService


class BaseLLMService(LLMService, ABC):
    """Mecanismo principal: consulta directa al modelo de lenguaje (ConcreteComponent).
    Las implementaciones reciben un CredentialsService por constructor."""
