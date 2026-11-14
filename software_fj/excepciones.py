"""
Módulo de excepciones personalizadas del sistema Software FJ.

Se define una jerarquía de excepciones propia para que cada tipo de error
del dominio (clientes, servicios, reservas, cálculos) pueda capturarse de
forma específica o, si se desea, de forma general mediante la clase base.
"""


class SoftwareFJError(Exception):
    """Excepción base de la que heredan todos los errores del sistema."""

    def __init__(self, mensaje: str, codigo: str = "SFJ-000") -> None:
        # Se llama al constructor de Exception para conservar el mensaje estándar
        super().__init__(mensaje)
        # Mensaje legible que describe el error
        self.mensaje = mensaje
        # Código interno que facilita identificar el error en el archivo de logs
        self.codigo = codigo

    def __str__(self) -> str:
        # Representación en texto: código entre corchetes seguido del mensaje
        return f"[{self.codigo}] {self.mensaje}"


# ---------------------------------------------------------------------------
# Errores de validación de datos
# ---------------------------------------------------------------------------

class ValidacionError(SoftwareFJError):
    """Error genérico cuando un dato no cumple las reglas de validación."""

    def __init__(self, mensaje: str, codigo: str = "SFJ-100") -> None:
        # Reutiliza el constructor de la clase base con un código por defecto
        super().__init__(mensaje, codigo)


class ClienteInvalidoError(ValidacionError):
    """Se lanza cuando los datos personales de un cliente son inválidos."""

    def __init__(self, mensaje: str) -> None:
        # Código específico para errores de clientes
        super().__init__(mensaje, "SFJ-101")


class ParametroFaltanteError(ValidacionError):
    """Se lanza cuando falta un parámetro obligatorio en una operación."""

    def __init__(self, parametro: str) -> None:
        # Se guarda el nombre del parámetro faltante para poder consultarlo
        self.parametro = parametro
        # Se construye un mensaje descriptivo con el nombre del parámetro
        super().__init__(f"Falta el parámetro obligatorio '{parametro}'", "SFJ-102")


class ServicioInvalidoError(ValidacionError):
    """Se lanza cuando un servicio se intenta crear con datos incorrectos."""

    def __init__(self, mensaje: str) -> None:
        # Código específico para errores en la creación de servicios
        super().__init__(mensaje, "SFJ-103")


# ---------------------------------------------------------------------------
# Errores de disponibilidad y operación
# ---------------------------------------------------------------------------

class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio que no está disponible."""

    def __init__(self, nombre_servicio: str) -> None:
        # Mensaje que indica cuál servicio no está disponible
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible", "SFJ-200")


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando los datos de una reserva son incorrectos."""

    def __init__(self, mensaje: str) -> None:
        # Código específico para reservas mal formadas
        super().__init__(mensaje, "SFJ-300")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una transición de estado no permitida."""

    def __init__(self, mensaje: str) -> None:
        # Código específico para operaciones prohibidas (ej. cancelar algo procesado)
        super().__init__(mensaje, "SFJ-301")


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo de costos produce un resultado inválido."""

    def __init__(self, mensaje: str) -> None:
        # Código específico para errores en cálculos de costos
        super().__init__(mensaje, "SFJ-400")


class EntidadNoEncontradaError(SoftwareFJError):
    """Se lanza cuando se busca un cliente, servicio o reserva inexistente."""

    def __init__(self, tipo: str, identificador: str) -> None:
        # Mensaje que indica el tipo de entidad y el identificador buscado
        super().__init__(f"No existe {tipo} con identificador '{identificador}'", "SFJ-500")
