from datetime import datetime
from pathlib import Path

from system.contexto_ejecucion.servicios.servicio_logging.logging_service import LoggingService

CARPETA = Path(__file__).resolve().parents[4] / "logs"  # ubicación local de los logs


# Dummy: reemplaza a FileLoggingService.
class LocalLoggingService(LoggingService):
    """Registra los eventos en logs/ejecucion-<aaaa>-<mm>-<dd>_<hh>-<mm>-<ss>.log."""

    def __init__(self, credentials):
        self.credentials = credentials
        CARPETA.mkdir(parents=True, exist_ok=True)
        self.ruta = CARPETA / f"ejecucion-{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        self.archivo = open(self.ruta, "a", encoding="utf-8", buffering=1)

    def registrar(self, nivel, mensaje):
        self.archivo.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} [{nivel}] {mensaje}\n")

    def info(self, mensaje):
        self.registrar("INFO", mensaje)

    def warning(self, mensaje):
        self.registrar("WARNING", mensaje)

    def error(self, mensaje):
        self.registrar("ERROR", mensaje)
