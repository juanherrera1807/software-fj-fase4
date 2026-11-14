"""
Módulo con la clase abstracta Entidad.

Representa cualquier entidad general del sistema (clientes, servicios y
reservas). Define los atributos y comportamientos comunes que todas las
clases derivadas deben tener.
"""

from abc import ABC, abstractmethod  # Herramientas para definir clases abstractas
from collections import defaultdict  # Diccionario con valor por defecto
from datetime import datetime  # Para registrar la fecha de creación
from itertools import count  # Generador de números consecutivos para los IDs


class Entidad(ABC):
    """Clase abstracta base de todas las entidades del sistema."""

    # Un contador independiente por prefijo (CLI, SRV, RES) para generar IDs únicos
    _secuencias = defaultdict(lambda: count(1))

    def __init__(self, prefijo: str) -> None:
        # Identificador único con prefijo según el tipo (ej. CLI-0001)
        self.__id = f"{prefijo}-{next(Entidad._secuencias[prefijo]):04d}"
        # Fecha y hora en que se creó la entidad
        self.__fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        """Identificador único de la entidad (solo lectura)."""
        # Se expone el atributo privado sin permitir modificarlo
        return self.__id

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha de creación de la entidad (solo lectura)."""
        # Se expone la fecha sin permitir modificarla
        return self.__fecha_creacion

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción en texto de la entidad."""
        # Cada clase hija debe implementar su propia descripción

    @abstractmethod
    def validar(self) -> bool:
        """Verifica que el estado interno de la entidad sea válido."""
        # Cada clase hija define sus propias reglas de validación

    def __str__(self) -> str:
        # Al imprimir la entidad se muestra su descripción
        return self.describir()
