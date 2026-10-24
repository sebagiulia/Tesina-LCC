import json

from system.deteccion.elementos_blackboard.analisis import Analisis
from system.deteccion.elementos_blackboard.resultado_regla import Estado
from system.deteccion.fuentes_conocimiento.analizadores.analizador import Analizador


def pct(valor):
    return f"{valor:.2f}".replace(".", ",") + " %"


# ResumenErroresAnalizador en el diseño.
class ResumenAnalizador(Analizador):
    """Resume cada error detectado en lenguaje comprensible para el ámbito médico (RF-04).
    Registra un Analisis por error cuyo contenido es JSON: título, justificación y filas
    (concepto, informado, esperado) para fundamentar la detección."""

    def __init__(self, condicion, logger):
        self.condicion = condicion
        self.logger = logger

    def nombre(self):
        return "ResumenAnalizador"

    def precondicion(self, blackboard):
        return self.condicion.evaluar(blackboard)

    def ejecutar(self, blackboard):
        resumenes = {"ReglaErrorCalculoIncapacidad": self.resumir_calculo,
                     "ReglaErrorTipoContingencia": self.resumir_contingencia}
        for resultado in blackboard.resultados():
            if resultado.estado() != Estado.DETECTADO:
                continue
            if resultado.regla_id() not in resumenes:
                self.logger.warning(f"ResumenAnalizador: no hay resumen para {resultado.regla_id()}")
                continue
            resumen = resumenes[resultado.regla_id()](json.loads(resultado.motivo()))
            blackboard.registrar(Analisis(f"Resumen{resultado.regla_id()}", json.dumps(resumen, ensure_ascii=False)))
            self.logger.info(f"ResumenAnalizador: {resumen['titulo']} en {blackboard.dictamen().nombre()}")

    def resumir_calculo(self, d):
        lesiones = "; ".join(f"{nombre}, {pct(p)}" for nombre, p in d["lesiones"])
        factores = [f for f in d["factores"] if f[2]]  # los factores sin ajuste no aportan al cálculo
        detalle_factores = " y ".join(f"{tipo.lower()} {pct(ajuste)}" for tipo, _, ajuste in factores)
        cantidad = "una única lesión" if len(d["lesiones"]) == 1 else f"{len(d['lesiones'])} lesiones"
        return {
            "titulo": "Error de cálculo de incapacidad",
            "justificacion": (
                f"El dictamen pondera {cantidad} ({lesiones}), lo que da un subtotal de {pct(d['subtotal'])}. "
                f"Al sumar los factores de ponderación informados en el mismo dictamen ({detalle_factores}), "
                f"el porcentaje total resultante es {pct(d['calculado'])}. "
                f"Sin embargo, se consignó un total de {pct(d['informado'])}."
            ),
            "filas": [[f"Lesión: {nombre}", pct(p), pct(p)] for nombre, p in d["lesiones"]]
                     + [["Subtotal de lesiones", pct(d["subtotal"]), pct(d["subtotal"])]]
                     + [[f"{tipo}: {desc}", pct(a), pct(a)] for tipo, desc, a in factores]
                     + [["Porcentaje total", pct(d["informado"]), pct(d["calculado"])]],
        }

    def resumir_contingencia(self, d):
        return {
            "titulo": "Error de tipo de contingencia",
            "justificacion": (
                f"La descripción de la contingencia indica que el trabajador «{d['evidencia']}». "
                f"El siniestro ocurrió durante el trayecto ({d['subtipo'].lower()}), por lo que corresponde "
                f"clasificarlo como accidente in itinere (art. 6 de la Ley 24.557). No obstante, el dictamen lo "
                f"consigna como {d['tipo']} y define la contingencia como {d['contingencia_definida']}. "
                f"La clasificación incorrecta afecta la trazabilidad estadística del siniestro y puede tener "
                f"impacto en instancias posteriores del trámite."
            ),
            "filas": [
                ["Tipo de AT/EP", d["tipo"], d["clasificacion"]],
                ["Subtipo", "—", d["subtipo"]],
                ["Contingencia definida", d["contingencia_definida"], d["contingencia"]],
            ],
        }
