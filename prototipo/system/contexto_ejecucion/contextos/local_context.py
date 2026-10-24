from system.contexto_ejecucion.contextos.execution_context import ExecutionContext
from system.contexto_ejecucion.servicios.servicio_credenciales.local_credentials_service import LocalCredentialsService
from system.contexto_ejecucion.servicios.servicio_llm.dummy_model_llm_service import DummyModelLLMService
from system.contexto_ejecucion.servicios.servicio_llm.dummy_prompt_template_service import DummyPromptTemplateService
from system.contexto_ejecucion.servicios.servicio_logging.local_logging_service import LocalLoggingService


# Dummy: reemplaza a DEVContext (y a PRODContext en producción).
class LocalContext(ExecutionContext):
    """Familia de servicios locales: credenciales en .env, logs en archivo y LLM simulado."""

    def __init__(self):
        self.logger = None

    def createCredentialsService(self):
        return LocalCredentialsService()

    def createLoggingService(self):
        # Un único archivo de log por ejecución.
        if self.logger is None:
            self.logger = LocalLoggingService(self.createCredentialsService())
        return self.logger

    def createLLMService(self):
        # "DummyLLMService": el modelo dummy decorado con el servicio de plantillas.
        modelo = DummyModelLLMService(self.createCredentialsService(), self.createLoggingService())
        return DummyPromptTemplateService(modelo, self.createLoggingService())
