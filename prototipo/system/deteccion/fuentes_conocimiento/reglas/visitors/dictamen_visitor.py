from abc import ABC, abstractmethod


class ErrorDetectado(Exception):
    """La lanza un visitor al detectar la incongruencia; motivo describe el error (JSON)."""

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


class DictamenVisitor(ABC):
    """Un método visitar_* por cada tipo concreto de componente del dictamen.
    visitar_dictamen, visitar_seccion_fundamentos y visitar_seccion_datos_principales se agregan
    por las secciones nuevas (ítem de cambio 2). Los servicios se inyectan por constructor."""

    @abstractmethod
    def visitar_dictamen(self, dictamen): ...

    @abstractmethod
    def visitar_seccion_incapacidad(self, seccion): ...

    @abstractmethod
    def visitar_lesion(self, lesion): ...

    @abstractmethod
    def visitar_factor_ponderacion(self, factor): ...

    @abstractmethod
    def visitar_seccion_fundamentos(self, seccion): ...

    @abstractmethod
    def visitar_seccion_datos_principales(self, seccion): ...
