"""Cliente (Injector): arma el contexto, inyecta los servicios y ejecuta el flujo del diseño.

Uso: python main.py
"""
from system.contexto_ejecucion.contextos.local_context import LocalContext
from system.deteccion.control import Control
from system.deteccion.estrategias_control.estrategia_basica_control import EstrategiaBasicaControl
from system.deteccion.fuentes_conocimiento.analizadores.resumen_analizador import ResumenAnalizador
from system.deteccion.fuentes_conocimiento.condiciones.contingencia_no_in_itinere import ContingenciaNoInItinere
from system.deteccion.fuentes_conocimiento.condiciones.seccion_incapacidad_condicion import SeccionIncapacidadCondicion
from system.deteccion.fuentes_conocimiento.condiciones.todas_las_reglas_ejecutadas import TodasLasReglasEjecutadas
from system.deteccion.fuentes_conocimiento.reglas.regla import Regla
from system.deteccion.fuentes_conocimiento.reglas.visitors.error_calculo_incapacidad import ErrorCalculoIncapacidad
from system.deteccion.fuentes_conocimiento.reglas.visitors.error_tipo_contingencia import ErrorTipoContingencia
from system.formateo_y_envio.envio.local_sender import LocalSender
from system.formateo_y_envio.formateo.reporte_ger_med_pdf import ReporteGerMedPDF
from system.ingesta_y_transformacion.dictamen.dictamen import Dictamen
from system.ingesta_y_transformacion.fuente.local_reader import LocalReader
from system.procesamiento.motor_secuencial import MotorSecuencial


def main():
    contexto = LocalContext()
    credenciales = contexto.createCredentialsService()
    logger = contexto.createLoggingService()
    llm_service = contexto.createLLMService()  # DummyLLMService
    logger.info("Inicio de ejecución")

    # Regla ErrorCalculoIncapacidad: se activa cuando la sección de incapacidad existe.
    seccion_incapacidad_condicion = SeccionIncapacidadCondicion(logger)
    error_calculo_incapacidad = ErrorCalculoIncapacidad(logger)
    regla_error_calculo_incapacidad = Regla(
        "ReglaErrorCalculoIncapacidad",
        seccion_incapacidad_condicion,
        error_calculo_incapacidad,
        logger)

    # Regla ErrorTipoContingencia: se activa cuando el tipo de contingencia no es in itinere.
    contingencia_no_in_itinere = ContingenciaNoInItinere(logger)
    error_tipo_contingencia = ErrorTipoContingencia(llm_service, logger)
    regla_error_tipo_contingencia = Regla(
        "ReglaErrorTipoContingencia",
        contingencia_no_in_itinere,
        error_tipo_contingencia,
        logger)

    # Analizador: se activa cuando todas las reglas fueron evaluadas.
    todas_las_reglas_ejecutadas = TodasLasReglasEjecutadas(logger)
    resumen_analizador = ResumenAnalizador(todas_las_reglas_ejecutadas, logger)

    estrategia_control = EstrategiaBasicaControl(logger)
    control = Control(estrategia_control, logger)
    control.registrar(regla_error_calculo_incapacidad)
    control.registrar(regla_error_tipo_contingencia)
    control.registrar(resumen_analizador)

    # Ingesta y procesamiento general.
    reader = LocalReader(credenciales, logger)
    motor = MotorSecuencial(control, logger)
    
    try:
        while reader.hasNext():
            dictamen = Dictamen(logger)
            dictamen.readFrom(reader)
            motor.registrar(dictamen)
        blackboards = motor.ejecutar()

        # Formateo y envío.
        reporte_ger_med_pdf = ReporteGerMedPDF(logger)
        sender = LocalSender(reporte_ger_med_pdf, logger, credenciales)
        sender.generar(blackboards)
        sender.enviar()
    except Exception as error:
        logger.error(f"Ejecución interrumpida: {error!r}")
        raise
    logger.info("Fin de ejecución")


if __name__ == "__main__":
    main()
