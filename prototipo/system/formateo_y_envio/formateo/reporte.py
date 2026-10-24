class Reporte:
    """Reporte ya generado y sus metadatos (el primero es el nombre de archivo sugerido)."""

    def __init__(self, archivo: bytes, metadatos: list):
        self._archivo, self._metadatos = archivo, metadatos

    def archivo(self):
        return self._archivo

    def metadatos(self):
        return self._metadatos
