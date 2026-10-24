# Prototipo: detección de incongruencias en dictámenes médicos

Prototipo de la tesina sobre el diseño de una herramienta que detecta incongruencias en los dictámenes médicos que emite la Superintendencia de Riesgos del Trabajo (SRT), errores que le interesan a las Aseguradoras de Riesgos del Trabajo (ART).

El prototipo muestra cómo se integran las soluciones del diseño (`diseño.pdf`): lee dictámenes en PDF, arma un **Blackboard** por dictamen, le aplica **reglas** de detección (una de ellas consulta a un LLM), resume los errores encontrados y genera el **informe diario para la Gerencia Médica**.

---

## Ejecución

**Requisitos**

- Python 3.10
- Fuentes DejaVu en `/usr/share/fonts/truetype/dejavu/` (las usa el PDF del informe)
- Dependencias: `pypdf`, `reportlab`, `python-dotenv`

```bash
pip install -r requirements.txt
python main.py
```

**Flujo de `main.py`**

1. `LocalContext` crea los servicios de credenciales, logging y LLM.
2. Se arman las reglas (`Regla` = identificador + `Condicion` + `DictamenVisitor`) y el analizador, y se registran en el `Control`.
3. `LocalReader` recorre los PDF y cada `Dictamen` se reconstruye a sí mismo.
4. `MotorSecuencial` crea un `Blackboard` por dictamen y le pide al `Control` que ejecute las fuentes de conocimiento.
5. `LocalSender` le pide el `Reporte` a `ReporteGerMedPDF` y lo guarda.

---

## Dictámenes de prueba

En `datos/dictamenes/` hay tres dictámenes ficticios, cada uno pensado para un caso:

| Archivo | Caso | Qué contiene | Resultado esperado |
|---|---|---|---|
| `dictamen_medico_calculo_incapacidad.pdf` | Error de cálculo | Dos lesiones (1,00 % + 0,05 %) y factores de ponderación (0,11 % + 0,10 %): la suma da **1,26 %**, pero el total informado es **2,00 %** | `ReglaErrorCalculoIncapacidad`: **detectado**. `ReglaErrorTipoContingencia`: no detectado |
| `dictamen_medico_tipo_contingencia.pdf` | Error de contingencia | Tipo de AT/EP "Accidente Laboral", pero la descripción dice "*camino al trabajo*, caminando se patina…" (es un accidente in itinere). No fija porcentaje de incapacidad | `ReglaErrorTipoContingencia`: **detectado**. `ReglaErrorCalculoIncapacidad`: **no evaluada** (no hay sección de incapacidad) |
| `dictamen_medico_correcto.pdf` | Sin errores | Total informado 7,00 %, que coincide con el cálculo. Accidente laboral bien clasificado | Ninguna regla detecta errores |

---

## Qué devuelve

### 1. Informe diario en PDF

`datos/resultados/Informe_Diario_Dictamenes_<dd-mm-aaaa>_generado.pdf`

- **Portada**: fecha de emisión de los dictámenes, fecha de elaboración, destinatario, indicadores (*3 dictámenes analizados*, *2 alertas detectadas*) y el objeto del informe, que resume los errores encontrados.
- **Una página por dictamen con errores**: Nro. de reporte, trabajador, expediente SRT, tipo de contingencia, motivo, diagnóstico e incapacidad dictaminada. Debajo, un recuadro por error con:
  - una **justificación** en lenguaje médico (la genera `ResumenAnalizador`);
  - una tabla **Concepto / Informado / Esperado**. Por ejemplo, *Porcentaje total: 2,00 % → 1,26 %* o *Tipo de AT/EP: Accidente Laboral → In Itinere*.

El dictamen correcto solo se cuenta en la portada y no tiene página propia.

### 2. Log de ejecución

`logs/ejecucion-<aaaa>-<mm>-<dd>_<hh>-<mm>-<ss>.log`: todos los módulos reciben el mismo `LoggingService` por constructor y registran lo que hacen. Para ver el estado de cada regla:

```bash
grep "sobre" logs/<último>.log
```

```
ReglaErrorCalculoIncapacidad sobre dictamen_medico_calculo_incapacidad.pdf: detectado
ReglaErrorTipoContingencia sobre dictamen_medico_calculo_incapacidad.pdf: no detectado
ReglaErrorCalculoIncapacidad sobre dictamen_medico_correcto.pdf: no detectado
ReglaErrorTipoContingencia sobre dictamen_medico_correcto.pdf: no detectado
ReglaErrorTipoContingencia sobre dictamen_medico_tipo_contingencia.pdf: detectado
ReglaErrorCalculoIncapacidad sobre dictamen_medico_tipo_contingencia.pdf: no evaluada
```

---

## Distribución de clases (estructura de módulos)

Las carpetas siguen la **Estructura de Módulos** del diseño: un módulo que se divide en otros es una carpeta, y cada módulo hoja es un archivo con su clase.

```
main.py                                   Cliente / Injector
system/                                   System
├── procesamiento/                        Procesamiento
│   ├── motor_general.py                    MotorGeneral (abstracta)
│   └── motor_secuencial.py                 MotorSecuencial
├── ingesta_y_transformacion/             IngestaYTransformacion
│   ├── fuente/                             Fuente
│   │   ├── reader.py                         Reader (abstracta)
│   │   └── local_reader.py                   LocalReader
│   ├── section_data.py                     SectionData
│   └── dictamen/                           Dictamen
│       ├── dictamen_component.py             DictamenComponent (abstracta)
│       ├── dictamen_composite.py             DictamenComposite (abstracta)
│       ├── dictamen_leaf.py                  DictamenLeaf (abstracta)
│       ├── dictamen.py                       Dictamen (raíz del Composite)
│       └── secciones/                        Secciones
│           ├── seccion_incapacidad.py          SeccionIncapacidad
│           ├── lesion.py                       Lesion
│           ├── factor_ponderacion.py           FactorPonderacion
│           ├── seccion_fundamentos.py          SeccionFundamentos       (agregada)
│           └── seccion_datos_principales.py    SeccionDatosPrincipales  (agregada)
├── contexto_ejecucion/                   ContextoEjecucion
│   ├── contextos/                          Contextos
│   │   ├── execution_context.py              ExecutionContext (abstracta)
│   │   └── local_context.py                  LocalContext
│   └── servicios/                          Servicios
│       ├── servicio_logging/                 ServicioLogging
│       │   ├── logging_service.py              LoggingService (abstracta)
│       │   └── local_logging_service.py        LocalLoggingService
│       ├── servicio_llm/                     ServicioLLM
│       │   ├── llm_service.py                  LLMService (abstracta)
│       │   ├── base_llm_service.py             BaseLLMService (abstracta)
│       │   ├── dummy_model_llm_service.py      DummyModelLLMService
│       │   ├── llm_decorator.py                LLMDecorator (abstracta)
│       │   ├── dummy_prompt_template_service.py DummyPromptTemplateService
│       │   ├── request.py                      Request
│       │   └── response.py                     Response
│       └── servicio_credenciales/            ServicioCredenciales
│           ├── credentials_service.py          CredentialsService (abstracta)
│           └── local_credentials_service.py    LocalCredentialsService
├── deteccion/                            Deteccion
│   ├── blackboard.py                       Blackboard
│   ├── control.py                          Control
│   ├── elementos_blackboard/               ElementosBlackboard (sin ElemBB)
│   │   ├── resultado_regla.py                ResultadoRegla, Estado
│   │   └── analisis.py                       Analisis
│   ├── estrategias_control/                EstrategiasControl
│   │   ├── estrategia_control.py             EstrategiaControl (abstracta)
│   │   └── estrategia_basica_control.py      EstrategiaBasicaControl
│   └── fuentes_conocimiento/               FuentesConocimiento
│       ├── fuente_conocimiento.py            FuenteConocimiento (abstracta)
│       ├── condiciones/                      Condiciones
│       │   ├── condicion.py                    Condicion (abstracta)
│       │   ├── seccion_incapacidad_condicion.py SeccionIncapacidadCondicion
│       │   ├── contingencia_no_in_itinere.py   ContingenciaNoInItinere
│       │   └── todas_las_reglas_ejecutadas.py  TodasLasReglasEjecutadas
│       ├── reglas/                           Reglas
│       │   ├── regla.py                        Regla
│       │   └── visitors/                       Visitors
│       │       ├── dictamen_visitor.py           DictamenVisitor (abstracta), ErrorDetectado
│       │       ├── error_calculo_incapacidad.py  ErrorCalculoIncapacidad
│       │       └── error_tipo_contingencia.py    ErrorTipoContingencia
│       └── analizadores/                     Analizadores
│           ├── analizador.py                   Analizador (abstracta)
│           └── resumen_analizador.py           ResumenAnalizador
└── formateo_y_envio/                     FormateoYEnvio
    ├── formateo/                           Formateo
    │   ├── estrategia_formato.py             EstrategiaFormato (abstracta)
    │   ├── reporte_ger_med_pdf.py            ReporteGerMedPDF
    │   └── reporte.py                        Reporte
    └── envio/                              Envio
        ├── sender.py                         Sender (abstracta)
        └── local_sender.py                   LocalSender
```

Del diseño no se implementan las alternativas que el prototipo no usa: `MotorParalelo`, `ApiReader`, `DataBaseReader`, `ConsoleLoggingService`, `RAGBaremoService`, `PRODCredentialsService`, `ReglasConLLMEjecutadas`, `ErrorPorcentajeLesion`, `CostoAnalizador`, `AhorroAnalizador`, `ReporteEjecutivoCSV`, `ReporteInternoPKL`, `EmailSender` y `SharepointSender`. Tampoco se implementa `ElemBB` (trazabilidad).

---

## Clases concretas

### Procesamiento

| Clase | Qué hace |
|---|---|
| `MotorSecuencial` | Procesa los dictámenes uno tras otro: crea un `Blackboard` por dictamen y delega su ejecución en el `Control`. |

### IngestaYTransformacion

| Clase | Qué hace |
|---|---|
| `LocalReader` | Lee los PDF de `datos/dictamenes/` con pypdf, descarta encabezados y pies, y separa las secciones por sus títulos. |
| `SectionData` | Contenedor clave → valor con una parte de la información del dictamen, la que entrega el `Reader`. |
| `Dictamen` | Raíz del Composite: se reconstruye desde el `Reader` con las secciones presentes y propaga el visitor a sus hijos. |
| `SeccionIncapacidad` | Sección compuesta con el porcentaje total, la capacidad restante y sus `Lesion` y `FactorPonderacion` hijas. |
| `Lesion` | Hoja con una lesión de la tabla de incapacidad y su porcentaje. |
| `FactorPonderacion` | Hoja con un factor de ponderación (tipo, descripción y ajuste). |
| `SeccionFundamentos` | Hoja con el tipo de AT/EP, la descripción de la contingencia y la fecha del accidente. |
| `SeccionDatosPrincipales` | Hoja con los datos de identificación que usa el informe: emisión, expediente, damnificado, motivo, diagnóstico y contingencia definida. |

### ContextoEjecucion

| Clase | Qué hace |
|---|---|
| `LocalContext` | Crea los servicios locales. Comparte un único logger por ejecución. |
| `LocalCredentialsService` | Lee las credenciales del archivo `.env`. |
| `LocalLoggingService` | Escribe los eventos con nivel y hora en `logs/ejecucion-<fecha>_<hora>.log`. |
| `DummyModelLLMService` | Simula el modelo: devuelve una respuesta fija según palabras clave del prompt (p. ej. "camino al trabajo"), junto con la cita que la justifica. |
| `DummyPromptTemplateService` | Decorator que arma el prompt con la plantilla de `prompt_id` y los `prompt_params`, y delega en el modelo. |
| `Request` / `Response` | Alias de `dict` para la consulta y la respuesta del servicio LLM. |

### Deteccion

| Clase | Qué hace |
|---|---|
| `Blackboard` | Guarda el dictamen (nivel 1), un `ResultadoRegla` por regla (nivel 2) y los `Analisis` (nivel 3). |
| `Control` | Evalúa las precondiciones de las fuentes pendientes y ejecuta la que elige la estrategia. Si ninguna se cumple, las reglas pendientes quedan *no evaluadas*. |
| `ResultadoRegla` (+ `Estado`) | Resultado de una regla: su id, el estado (`detectado`, `no detectado`, `no evaluada`) y el motivo en JSON. |
| `Analisis` | Resultado de un analizador: id y contenido en JSON. |
| `EstrategiaBasicaControl` | Elige la primera candidata, en orden de registro. |
| `Regla` | Fuente de conocimiento que combina una `Condicion` (precondición) con un `DictamenVisitor` (acción) y registra el `ResultadoRegla`. Con ella se arman `ReglaErrorCalculoIncapacidad` y `ReglaErrorTipoContingencia` en `main.py`. |
| `SeccionIncapacidadCondicion` | Se cumple si el dictamen tiene sección de incapacidad. |
| `ContingenciaNoInItinere` | Se cumple si el tipo de AT/EP no dice "in itinere". Así se evita consultar al LLM sin necesidad. |
| `TodasLasReglasEjecutadas` | Se cumple cuando todas las reglas ya dejaron su `ResultadoRegla` en el Blackboard. |
| `ErrorCalculoIncapacidad` | Visitor que suma lesiones y ajustes de los factores y compara el resultado con el total informado (tolerancia 0,01). |
| `ErrorTipoContingencia` | Visitor que consulta al `LLMService` si la descripción corresponde a un accidente in itinere informado como laboral. |
| `ErrorDetectado` | Excepción que lanza un visitor al detectar el error. Lleva el motivo en JSON. |
| `ResumenAnalizador` | Se activa con `TodasLasReglasEjecutadas` y escribe un `Analisis` por error: título, justificación médica y filas Informado/Esperado. |

### FormateoYEnvio

| Clase | Qué hace |
|---|---|
| `ReporteGerMedPDF` | Estrategia de formato que arma con reportlab el informe diario: portada con totales y una página por dictamen con errores. |
| `Reporte` | El reporte ya generado (bytes del archivo) y sus metadatos (nombre sugerido y título). |
| `LocalSender` | Pide el reporte a la estrategia de formato y lo guarda en `datos/resultados/`. |

---