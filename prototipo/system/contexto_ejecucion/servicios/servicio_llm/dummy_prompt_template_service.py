from system.contexto_ejecucion.servicios.servicio_llm.llm_decorator import LLMDecorator


# Dummy: reemplaza a TemplatePromptService.
class DummyPromptTemplateService(LLMDecorator):
    """Construye el prompt a partir de la plantilla indicada por prompt_id y los parámetros de prompt_params."""

    PLANTILLAS = {
        "tipo_contingencia": (
            "Sos auditor médico de una ART. El dictamen informa como Tipo de AT/EP: '{tipo}'. "
            "Leé la descripción de la contingencia y respondé si corresponde a un accidente laboral "
            "o a un accidente in itinere, con su subtipo y la cita que lo justifica.\n"
            "Descripción de la contingencia: {descripcion}"
        ),
    }

    def __init__(self, service, logger):
        self.service = service  # LLMService decorado
        self.logger = logger

    def procesar(self, request):
        if "prompt_id" in request:
            plantilla = self.PLANTILLAS[request["prompt_id"]]
            request["prompt"] = plantilla.format(**request.get("prompt_params", {}))
            self.logger.info(f"DummyPromptTemplateService: prompt construido con la plantilla '{request['prompt_id']}'")
        return self.service.procesar(request)
