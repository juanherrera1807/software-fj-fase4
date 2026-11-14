"""
Módulo con la clase Reserva.

Una reserva integra un cliente, un servicio, una duración y un estado.
Implementa confirmación, cancelación y procesamiento, usando todas las
formas de manejo de excepciones pedidas: try/except, try/except/else,
try/except/finally y encadenamiento de excepciones (raise ... from ...).
"""

from enum import Enum  # Para definir los estados posibles de una reserva

from .cliente import Cliente  # Clase Cliente
from .entidad import Entidad  # Clase abstracta base
from .excepciones import (  # Excepciones personalizadas
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from .registro import obtener_logger  # Logger del sistema
from .servicios import Servicio  # Clase abstracta Servicio

# Logger propio de este módulo
logger = obtener_logger("reserva")


class EstadoReserva(Enum):
    """Estados por los que puede pasar una reserva."""

    PENDIENTE = "pendiente"  # Recién creada, aún no confirmada
    CONFIRMADA = "confirmada"  # Confirmada, pendiente de procesar el pago
    PROCESADA = "procesada"  # Pagada y finalizada
    CANCELADA = "cancelada"  # Cancelada por el cliente o el sistema
    FALLIDA = "fallida"  # Falló durante el procesamiento


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: float, **parametros) -> None:
        # Se inicializa la parte común (ID y fecha) con el prefijo RES
        super().__init__("RES")
        # El cliente debe ser una instancia de Cliente
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente válido")
        # El servicio debe ser una instancia de alguna subclase de Servicio
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio válido")
        # Cliente que hace la reserva
        self.__cliente = cliente
        # Servicio reservado
        self.__servicio = servicio
        # Duración (horas o días, según el servicio)
        self.__duracion = duracion
        # Parámetros adicionales del servicio (personas, cantidad, modalidad...)
        self.__parametros = dict(parametros)
        # Toda reserva inicia en estado pendiente
        self.__estado = EstadoReserva.PENDIENTE
        # El costo se calcula al procesar
        self.__costo = None
        # Se valida la reserva completa; si falla se encadena el error original
        try:
            self.validar()
        except SoftwareFJError as error:
            raise ReservaInvalidaError(f"Datos de reserva inválidos: {error}") from error

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------
    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion(self) -> float:
        return self.__duracion

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo(self) -> float | None:
        return self.__costo

    # ------------------------------------------------------------------
    # Métodos abstractos implementados
    # ------------------------------------------------------------------
    def validar(self) -> bool:
        """Valida que la duración y los parámetros sean correctos para el servicio."""
        # Se delega la validación al servicio (polimorfismo)
        self.__servicio.validar_parametros(self.__duracion, **self.__parametros)
        return True

    def describir(self) -> str:
        costo = f"${self.__costo:,.2f}" if self.__costo is not None else "sin calcular"
        return f"Reserva {self.id}: {self.__cliente.nombre} -> {self.__servicio.nombre} | duración {self.__duracion} | estado {self.__estado.value} | costo {costo}"

    # ------------------------------------------------------------------
    # Operaciones del ciclo de vida
    # ------------------------------------------------------------------
    def confirmar(self) -> None:
        """Confirma la reserva. Usa try/except/else."""
        # Solo se pueden confirmar reservas pendientes
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(f"No se puede confirmar la reserva {self.id} en estado '{self.__estado.value}'")
        try:
            # Se comprueba que el servicio siga disponible
            self.__servicio.verificar_disponibilidad()
        except ServicioNoDisponibleError:
            # Se registra el fallo y se vuelve a lanzar para que lo maneje quien llamó
            logger.warning("Confirmación rechazada para %s: servicio no disponible", self.id)
            raise
        else:
            # Solo si no hubo excepción se cambia el estado
            self.__estado = EstadoReserva.CONFIRMADA
            logger.info("Reserva %s confirmada", self.id)

    def cancelar(self, motivo: str = "sin motivo") -> None:
        """Cancela la reserva si aún no ha sido procesada."""
        # No se puede cancelar algo ya procesado o ya cancelado
        if self.__estado in (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA):
            raise OperacionNoPermitidaError(f"No se puede cancelar la reserva {self.id} en estado '{self.__estado.value}'")
        # Se cambia el estado y se registra el motivo
        self.__estado = EstadoReserva.CANCELADA
        logger.info("Reserva %s cancelada. Motivo: %s", self.id, motivo)

    def procesar(self, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """
        Procesa (cobra) la reserva. Usa try/except/else/finally y
        encadenamiento: cualquier error de cálculo se envuelve en
        ReservaInvalidaError conservando la causa original.
        """
        # Solo se pueden procesar reservas confirmadas
        if self.__estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(f"La reserva {self.id} debe estar confirmada para procesarse (estado actual: '{self.__estado.value}')")
        try:
            # Se calcula el costo usando la variante "sobrecargada" con impuesto y descuento
            costo = self.__servicio.calcular_costo(self.__duracion, impuesto, descuento, **self.__parametros)
        except CalculoInconsistenteError as error:
            # La reserva queda marcada como fallida
            self.__estado = EstadoReserva.FALLIDA
            # Encadenamiento: se lanza un error de reserva cuya causa es el error de cálculo
            raise ReservaInvalidaError(f"No se pudo procesar la reserva {self.id}") from error
        else:
            # Si el cálculo fue exitoso se guarda el costo y se marca como procesada
            self.__costo = costo
            self.__estado = EstadoReserva.PROCESADA
            logger.info("Reserva %s procesada por $%.2f", self.id, costo)
            return costo
        finally:
            # Siempre se deja constancia del intento, haya fallado o no
            logger.info("Intento de procesamiento de %s finalizado con estado '%s'", self.id, self.__estado.value)
