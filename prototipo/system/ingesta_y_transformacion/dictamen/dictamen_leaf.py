from abc import ABC

from system.ingesta_y_transformacion.dictamen.dictamen_component import DictamenComponent


class DictamenLeaf(DictamenComponent, ABC):
    """Sección elemental del dictamen (hoja del Composite)."""
