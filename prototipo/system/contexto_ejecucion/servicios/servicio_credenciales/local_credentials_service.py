from pathlib import Path

from dotenv import dotenv_values

from system.contexto_ejecucion.servicios.servicio_credenciales.credentials_service import CredentialsService

ENV = Path(__file__).resolve().parents[4] / ".env"  # archivo local de credenciales


# Dummy: reemplaza a DEVCredentialsService (y a PRODCredentialsService en producción).
class LocalCredentialsService(CredentialsService):
    """Lee las credenciales de un archivo .env local."""

    def __init__(self):
        self.valores = dotenv_values(ENV)

    def get(self, clave):
        return self.valores.get(clave)
