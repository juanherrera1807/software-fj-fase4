"""
Módulo con la clase Cliente.

El cliente encapsula sus datos personales en atributos privados y solo
permite modificarlos a través de propiedades que validan cada valor.
"""

import re  # Expresiones regulares para validar correo, documento y teléfono

from .entidad import Entidad  # Clase abstracta base
from .excepciones import ClienteInvalidoError, ParametroFaltanteError  # Errores propios

# Patrón de correo electrónico: texto@dominio.extensión
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
# Patrón de documento: solo dígitos, entre 6 y 12 caracteres
PATRON_DOCUMENTO = re.compile(r"^\d{6,12}$")
# Patrón de teléfono: 10 dígitos (formato celular colombiano)
PATRON_TELEFONO = re.compile(r"^\d{10}$")
# Patrón de nombre: letras (con tildes y ñ) y espacios, mínimo 3 caracteres
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]{3,60}$")


class Cliente(Entidad):
    """Representa a un cliente de Software FJ con datos validados."""

    def __init__(self, nombre: str, documento: str, correo: str, telefono: str) -> None:
        # Se inicializa la parte común (ID y fecha) con el prefijo CLI
        super().__init__("CLI")
        # Cada asignación pasa por el setter correspondiente, que valida el valor
        self.nombre = nombre
        # Documento de identidad del cliente
        self.documento = documento
        # Correo electrónico de contacto
        self.correo = correo
        # Teléfono de contacto
        self.telefono = telefono

    # ------------------------------------------------------------------
    # Validación genérica reutilizada por todos los setters
    # ------------------------------------------------------------------
    @staticmethod
    def _validar_campo(campo: str, valor: object, patron: re.Pattern, mensaje: str) -> str:
        """Comprueba que el valor exista, sea texto y cumpla el patrón dado."""
        # Si el valor es None o una cadena vacía, falta el parámetro
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(campo)
        # Si no es texto, el tipo de dato es incorrecto
        if not isinstance(valor, str):
            raise ClienteInvalidoError(f"El campo '{campo}' debe ser texto, se recibió {type(valor).__name__}")
        # Se eliminan espacios sobrantes al inicio y al final
        limpio = valor.strip()
        # Si no cumple el patrón, el formato es inválido
        if not patron.match(limpio):
            raise ClienteInvalidoError(f"{mensaje}: '{limpio}'")
        # Se devuelve el valor limpio y validado
        return limpio

    # ------------------------------------------------------------------
    # Propiedades (encapsulación de datos personales)
    # ------------------------------------------------------------------
    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        # Devuelve el atributo privado
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        # Valida y guarda el nombre
        self.__nombre = self._validar_campo("nombre", valor, PATRON_NOMBRE, "Nombre inválido (solo letras, 3 a 60 caracteres)")

    @property
    def documento(self) -> str:
        """Documento de identidad del cliente."""
        # Devuelve el atributo privado
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        # Valida y guarda el documento
        self.__documento = self._validar_campo("documento", valor, PATRON_DOCUMENTO, "Documento inválido (6 a 12 dígitos)")

    @property
    def correo(self) -> str:
        """Correo electrónico del cliente."""
        # Devuelve el atributo privado
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        # Valida, normaliza a minúsculas y guarda el correo
        self.__correo = self._validar_campo("correo", valor, PATRON_CORREO, "Correo electrónico inválido").lower()

    @property
    def telefono(self) -> str:
        """Teléfono del cliente."""
        # Devuelve el atributo privado
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        # Valida y guarda el teléfono
        self.__telefono = self._validar_campo("telefono", valor, PATRON_TELEFONO, "Teléfono inválido (10 dígitos)")

    @property
    def documento_enmascarado(self) -> str:
        """Documento con los primeros dígitos ocultos, para mostrarlo en logs."""
        # Solo se muestran los últimos 4 dígitos para proteger el dato personal
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]

    # ------------------------------------------------------------------
    # Métodos abstractos implementados
    # ------------------------------------------------------------------
    def validar(self) -> bool:
        """Revalida todos los campos del cliente."""
        # Se reasignan los valores para que pasen otra vez por los setters
        self.nombre = self.__nombre
        self.documento = self.__documento
        self.correo = self.__correo
        self.telefono = self.__telefono
        # Si ningún setter lanzó excepción, el cliente es válido
        return True

    def describir(self) -> str:
        """Descripción del cliente sin exponer el documento completo."""
        # Se usa el documento enmascarado para no exponer datos sensibles
        return f"Cliente {self.id}: {self.nombre} (doc. {self.documento_enmascarado}, {self.correo})"
