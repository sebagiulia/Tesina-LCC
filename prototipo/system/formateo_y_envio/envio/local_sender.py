from pathlib import Path

from system.formateo_y_envio.envio.sender import Sender

CARPETA = Path(__file__).resolve().parents[3] / "datos" / "resultados"  # destino local de los reportes


class LocalSender(Sender):
    """Guarda el reporte en datos/resultados/. Agrega el sufijo _generado para no pisar el informe esperado."""

    def __init__(self, estrategia, logger, credentials):
        self.estrategia = estrategia
        self.logger = logger
        self.credentials = credentials
        self.reporte = None

    def generar(self, blackboards):
        self.reporte = self.estrategia.formatear(blackboards)
        self.logger.info(f"LocalSender: reporte generado con {type(self.estrategia).__name__}")

    def enviar(self):
        nombre = Path(self.reporte.metadatos()[0])
        CARPETA.mkdir(parents=True, exist_ok=True)
        ruta = CARPETA / f"{nombre.stem}_generado{nombre.suffix}"
        ruta.write_bytes(self.reporte.archivo())
        self.logger.info(f"LocalSender: reporte guardado en {ruta}")
