"""
Módulo con la clase SistemaGestion.

Administra las listas internas de clientes, servicios y reservas (sin base
de datos) y ofrece un método seguro para ejecutar operaciones: cualquier
error se registra en el log y la aplicación sigue funcionando.
"""

from dataclasses import dataclass  # Para definir el resultado de cada operación
from typing import Any, Callable  # Tipos para las anotaciones

from .cliente import Cliente  # Clase Cliente
from .excepciones import (  # Excepciones personalizadas
    ClienteInvalidoError,
    EntidadNoEncontradaError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from .registro import obtener_logger  # Logger del sistema
from .reserva import Reserva  # Clase Reserva
from .servicios import AlquilerEquipo, Asesoria, ReservaSala, Servicio  # Servicios

# Logger propio de este módulo
logger = obtener_logger("sistema")

# Catálogo de tipos de servicio que el sistema sabe crear (extensible)
TIPOS_SERVICIO = {
    "sala": ReservaSala,
    "equipo": AlquilerEquipo,
    "asesoria": Asesoria,
}


@dataclass(frozen=True)
class ResultadoOperacion:
    """Resultado inmutable de una operación simulada."""

    descripcion: str  # Qué se intentó hacer
    exitosa: bool  # True si terminó sin errores
    valor: Any = None  # Objeto o valor devuelto (si fue exitosa)
    error: str | None = None  # Mensaje de error (si falló)


class SistemaGestion:
    """Fachada que gestiona clientes, servicios y reservas en memoria."""

    def __init__(self) -> None:
        # Lista interna de clientes registrados
        self.__clientes: list[Cliente] = []
        # Lista interna de servicios ofrecidos
        self.__servicios: list[Servicio] = []
        # Lista interna de reservas realizadas
        self.__reservas: list[Reserva] = []
        logger.info("Sistema de gestión Software FJ iniciado")

    # ------------------------------------------------------------------
    # Consultas (se devuelven copias para no exponer las listas internas)
    # ------------------------------------------------------------------
    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self.__clientes)

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        return tuple(self.__servicios)

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self.__reservas)

    def buscar_cliente(self, documento: str) -> Cliente:
        """Busca un cliente por documento o lanza EntidadNoEncontradaError."""
        for cliente in self.__clientes:
            if cliente.documento == documento:
                return cliente
        raise EntidadNoEncontradaError("cliente", documento)

    def buscar_servicio(self, servicio_id: str) -> Servicio:
        """Busca un servicio por ID o lanza EntidadNoEncontradaError."""
        for servicio in self.__servicios:
            if servicio.id == servicio_id:
                return servicio
        raise EntidadNoEncontradaError("servicio", servicio_id)

    def buscar_reserva(self, reserva_id: str) -> Reserva:
        """Busca una reserva por ID o lanza EntidadNoEncontradaError."""
        for reserva in self.__reservas:
            if reserva.id == reserva_id:
                return reserva
        raise EntidadNoEncontradaError("reserva", reserva_id)

    # ------------------------------------------------------------------
    # Operaciones de registro
    # ------------------------------------------------------------------
    def registrar_cliente(self, nombre: str, documento: str, correo: str, telefono: str) -> Cliente:
        """Crea y registra un cliente; no permite documentos repetidos."""
        # Se crea el cliente (los setters validan cada dato)
        cliente = Cliente(nombre, documento, correo, telefono)
        # Se comprueba que no exista otro cliente con el mismo documento
        if any(c.documento == cliente.documento for c in self.__clientes):
            raise ClienteInvalidoError(f"Ya existe un cliente con documento {cliente.documento_enmascarado}")
        # Se agrega a la lista interna
        self.__clientes.append(cliente)
        logger.info("Cliente registrado: %s", cliente.describir())
        return cliente

    def crear_servicio(self, tipo: str, **datos) -> Servicio:
        """Crea un servicio del tipo indicado ('sala', 'equipo' o 'asesoria')."""
        # Se busca la clase correspondiente al tipo
        clase = TIPOS_SERVICIO.get(tipo)
        if clase is None:
            raise ServicioInvalidoError(f"Tipo de servicio '{tipo}' no existe. Opciones: {', '.join(TIPOS_SERVICIO)}")
        try:
            # Se instancia la clase con los datos recibidos
            servicio = clase(**datos)
        except TypeError as error:
            # Faltan o sobran argumentos: se encadena como error del dominio
            raise ServicioInvalidoError(f"Datos incompletos o incorrectos para crear '{tipo}': {error}") from error
        # Se agrega a la lista interna
        self.__servicios.append(servicio)
        logger.info("Servicio creado: %s", servicio.describir())
        return servicio

    def crear_reserva(self, documento_cliente: str, servicio_id: str, duracion: float, **parametros) -> Reserva:
        """Crea una reserva pendiente para un cliente y servicio existentes."""
        # Se buscan las entidades relacionadas (pueden lanzar EntidadNoEncontradaError)
        cliente = self.buscar_cliente(documento_cliente)
        servicio = self.buscar_servicio(servicio_id)
        # Se crea la reserva (valida duración y parámetros)
        reserva = Reserva(cliente, servicio, duracion, **parametros)
        # Se agrega a la lista interna
        self.__reservas.append(reserva)
        logger.info("Reserva creada: %s", reserva.describir())
        return reserva

    # ------------------------------------------------------------------
    # Ejecución segura de operaciones
    # ------------------------------------------------------------------
    def ejecutar(self, descripcion: str, operacion: Callable[[], Any]) -> ResultadoOperacion:
        """
        Ejecuta una operación sin que un error detenga la aplicación.
        Errores del dominio se registran como ERROR; errores inesperados
        como CRITICAL con su traza completa.
        """
        logger.info(">>> Iniciando operación: %s", descripcion)
        try:
            # Se ejecuta la operación recibida
            valor = operacion()
        except SoftwareFJError as error:
            # Error esperado del dominio: se registra con su causa encadenada, si existe
            causa = f" | causa: {type(error.__cause__).__name__}: {error.__cause__}" if error.__cause__ else ""
            logger.error("Operación fallida '%s': %s%s", descripcion, error, causa)
            return ResultadoOperacion(descripcion, False, error=f"{error}{causa}")
        except Exception as error:  # noqa: BLE001 - red de seguridad para no detener la app
            # Error no previsto: se registra con traza completa y la app sigue
            logger.critical("Error inesperado en '%s': %s", descripcion, error, exc_info=True)
            return ResultadoOperacion(descripcion, False, error=f"Error inesperado: {type(error).__name__}: {error}")
        else:
            # La operación terminó bien
            logger.info("Operación exitosa: %s", descripcion)
            return ResultadoOperacion(descripcion, True, valor=valor)
        finally:
            # Se marca siempre el fin de la operación en el log
            logger.info("<<< Fin de operación: %s", descripcion)
