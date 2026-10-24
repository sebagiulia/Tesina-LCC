class SectionData:
    """Almacena parte de la información de un dictamen (clave -> Value)."""

    def __init__(self, **valores):
        self.valores = dict(valores)

    def set(self, clave, valor):
        self.valores[clave] = valor

    def get(self, clave):
        return self.valores.get(clave)
