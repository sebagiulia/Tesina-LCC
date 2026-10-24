import json

from system.deteccion.fuentes_conocimiento.reglas.visitors.dictamen_visitor import DictamenVisitor, ErrorDetectado


class ErrorTipoContingencia(DictamenVisitor):
    """Detecta accidentes in itinere registrados como accidente de trabajo, interpretando
    la descripción de la contingencia con un LLMService."""

    def __init__(self, llm_service, logger):
        self.llm_service = llm_service
        self.logger = logger
        self.contingencia_definida = None

    def visitar_dictamen(self, dictamen):
        pass

    def visitar_seccion_incapacidad(self, seccion):
        pass

    def visitar_lesion(self, lesion):
        pass

    def visitar_factor_ponderacion(self, factor):
        pass

    def visitar_seccion_datos_principales(self, seccion):
        self.contingencia_definida = seccion.contingenciaDefinida()

    def visitar_seccion_fundamentos(self, seccion):
        request = {
            "prompt_id": "tipo_contingencia",
            "prompt_params": {"tipo": seccion.tipoContingencia(), "descripcion": seccion.descripcionContingencia()},
        }
        response = self.llm_service.procesar(request)
        self.logger.info(f"ErrorTipoContingencia: respuesta del LLM {response}")
        if response["status"] != "Ok":
            raise ErrorDetectado(json.dumps({
                "tipo": seccion.tipoContingencia(),
                "contingencia_definida": self.contingencia_definida,
                **response,
            }, ensure_ascii=False))
