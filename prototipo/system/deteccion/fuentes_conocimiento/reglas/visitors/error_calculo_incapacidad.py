import json

from system.deteccion.fuentes_conocimiento.reglas.visitors.dictamen_visitor import DictamenVisitor, ErrorDetectado

TOLERANCIA = 0.01


class ErrorCalculoIncapacidad(DictamenVisitor):
    """Detecta si el porcentaje total informado difiere de la suma de lesiones y factores de ponderación
    (cálculo simplificado de la tesis, sin preexistencias)."""

    def __init__(self, logger):
        self.logger = logger
        self.lesiones, self.factores = [], []

    def visitar_dictamen(self, dictamen):
        pass

    def visitar_seccion_fundamentos(self, seccion):
        pass

    def visitar_seccion_datos_principales(self, seccion):
        pass

    def visitar_lesion(self, lesion):
        self.lesiones.append(lesion)

    def visitar_factor_ponderacion(self, factor):
        self.factores.append(factor)

    def visitar_seccion_incapacidad(self, seccion):
        # Se visitan los hijos antes que la sección: acá se compara y se reinicia el estado.
        lesiones, factores, self.lesiones, self.factores = self.lesiones, self.factores, [], []
        subtotal = round(sum(l.porcentaje() for l in lesiones), 2)
        calculada = round(subtotal + sum(f.ajuste() for f in factores), 2)
        self.logger.info(f"ErrorCalculoIncapacidad: informada {seccion.incapacidadTotal()} %, calculada {calculada} %")
        if abs(calculada - seccion.incapacidadTotal()) > TOLERANCIA:
            raise ErrorDetectado(json.dumps({
                "lesiones": [[l.nombre(), l.porcentaje()] for l in lesiones],
                "subtotal": subtotal,
                "factores": [[f.tipo(), f.descripcion(), f.ajuste()] for f in factores],
                "informado": seccion.incapacidadTotal(),
                "calculado": calculada,
            }, ensure_ascii=False))
