import re

from system.contexto_ejecucion.servicios.servicio_llm.base_llm_service import BaseLLMService


# Dummy: reemplaza a ClaudeService (u OllamaService).
class DummyModelLLMService(BaseLLMService):
    """Simula al modelo: elige una respuesta hardcodeada según palabras clave contenidas en el prompt."""

    # (palabras clave, respuesta). Se usa la primera entrada cuya clave aparezca en el prompt.
    RESPUESTAS = [
        (("camino al trabajo", "yendo al trabajo", "hacia el trabajo", "de su casa al trabajo"),
         {"status": "Error", "clasificacion": "In Itinere", "subtipo": "De la casa al trabajo",
          "contingencia": "Accidente In Itinere"}),
        (("camino a su casa", "camino a casa", "volviendo del trabajo", "regreso a su domicilio"),
         {"status": "Error", "clasificacion": "In Itinere", "subtipo": "Del trabajo a la casa",
          "contingencia": "Accidente In Itinere"}),
    ]
    RESPUESTA_POR_DEFECTO = {"status": "Ok", "clasificacion": "Accidente Laboral"}

    def __init__(self, credentials, logger):
        self.credentials = credentials
        self.logger = logger
        if not credentials.get("LLM_API_KEY"):
            logger.warning("DummyModelLLMService: LLM_API_KEY no está definida en .env")

    def procesar(self, request):
        prompt = request["prompt"]
        for claves, respuesta in self.RESPUESTAS:
            clave = next((c for c in claves if c in prompt.lower()), None)
            if clave:
                # Simula la cita textual que devolvería el modelo: el fragmento que contiene la clave.
                evidencia = re.search(rf"{clave}[^,.]*,[^,.]*", prompt, re.IGNORECASE) or re.search(clave, prompt, re.IGNORECASE)
                self.logger.info(f"DummyModelLLMService: clave '{clave}' encontrada en el prompt")
                return {**respuesta, "evidencia": evidencia.group(0).strip()}
        self.logger.info("DummyModelLLMService: ninguna clave encontrada, respuesta por defecto")
        return dict(self.RESPUESTA_POR_DEFECTO)
