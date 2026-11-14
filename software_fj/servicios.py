"""
Módulo de servicios de Software FJ.

Contiene la clase abstracta Servicio y tres servicios especializados:
ReservaSala, AlquilerEquipo y Asesoria. Cada uno sobrescribe los métodos
para calcular costos, describirse y validar sus parámetros (polimorfismo).
"""

from abc import abstractmethod  # Para declarar métodos que las hijas deben implementar

from .entidad import Entidad  # Clase abstracta base
from .excepciones import (  # Excepciones personalizadas usadas en este módulo
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)

# Impuesto por defecto (IVA en Colombia: 19 %)
IVA = 0.19
# Descuento máximo permitido (50 %) para evitar cálculos absurdos
DESCUENTO_MAXIMO = 0.5


class Servicio(Entidad):
    """Clase abstracta que representa un servicio ofrecido por Software FJ."""

    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        # Se inicializa la parte común (ID y fecha) con el prefijo SRV
        super().__init__("SRV")
        # Se valida que el nombre exista
        if not nombre or not str(nombre).strip():
            raise ParametroFaltanteError("nombre")
        # Se valida que la tarifa sea un número positivo
        if not isinstance(tarifa_base, (int, float)) or isinstance(tarifa_base, bool) or tarifa_base <= 0:
            raise ServicioInvalidoError(f"La tarifa base debe ser un número mayor que cero, se recibió '{tarifa_base}'")
        # Nombre del servicio (privado)
        self.__nombre = str(nombre).strip()
        # Tarifa base por unidad de tiempo (privada)
        self.__tarifa_base = float(tarifa_base)
        # Indica si el servicio puede reservarse (privado)
        self.__disponible = bool(disponible)

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------
    @property
    def nombre(self) -> str:
        """Nombre del servicio."""
        return self.__nombre

    @property
    def tarifa_base(self) -> float:
        """Tarifa base del servicio."""
        return self.__tarifa_base

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está disponible."""
        return self.__disponible

    def habilitar(self) -> None:
        """Marca el servicio como disponible."""
        self.__disponible = True

    def deshabilitar(self) -> None:
        """Marca el servicio como no disponible (ej. mantenimiento)."""
        self.__disponible = False

    def verificar_disponibilidad(self) -> None:
        """Lanza ServicioNoDisponibleError si el servicio no se puede reservar."""
        # Si está deshabilitado, no se puede usar
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre)

    # ------------------------------------------------------------------
    # Métodos abstractos (cada servicio los implementa a su manera)
    # ------------------------------------------------------------------
    @abstractmethod
    def costo_base(self, duracion: float, **parametros) -> float:
        """Costo sin impuestos ni descuentos para la duración indicada."""

    @abstractmethod
    def validar_parametros(self, duracion: float, **parametros) -> None:
        """Valida la duración y los parámetros propios del servicio."""

    def validar(self) -> bool:
        """Valida el estado general del servicio."""
        # La tarifa debe seguir siendo positiva
        if self.__tarifa_base <= 0:
            raise ServicioInvalidoError("Tarifa base inválida")
        return True

    # ------------------------------------------------------------------
    # Método "sobrecargado": calcular_costo
    # ------------------------------------------------------------------
    def calcular_costo(self, duracion: float, *args: float, **parametros) -> float:
        """
        Calcula el costo del servicio. Simula sobrecarga de métodos
        (Python no la tiene de forma nativa) aceptando varias firmas:

        - calcular_costo(duracion)                        -> costo base
        - calcular_costo(duracion, impuesto)              -> base + impuesto
        - calcular_costo(duracion, impuesto, descuento)   -> base + impuesto - descuento
        - calcular_costo(duracion, impuesto=..., descuento=..., <parámetros del servicio>)
        """
        # Más de dos argumentos posicionales extra no corresponde a ninguna firma
        if len(args) > 2:
            raise CalculoInconsistenteError(f"calcular_costo recibe como máximo 3 argumentos posicionales, se recibieron {len(args) + 1}")
        # Se toman impuesto y descuento de la posición o del nombre (por defecto 0)
        impuesto = args[0] if len(args) >= 1 else parametros.pop("impuesto", 0.0)
        descuento = args[1] if len(args) == 2 else parametros.pop("descuento", 0.0)
        # Se eliminan claves repetidas si también llegaron por nombre
        parametros.pop("impuesto", None)
        parametros.pop("descuento", None)
        try:
            # Primero se validan los parámetros propios del servicio
            self.validar_parametros(duracion, **parametros)
            # Se calcula el costo base con la implementación de la clase hija
            base = self.costo_base(duracion, **parametros)
            # Se aplica la fórmula: base * (1 + impuesto) * (1 - descuento)
            total = base * (1 + float(impuesto)) * (1 - float(descuento))
        except (TypeError, ValueError) as error:
            # Encadenamiento: el error técnico se convierte en un error del dominio
            raise CalculoInconsistenteError(f"No se pudo calcular el costo de '{self.nombre}': {error}") from error
        # Se verifican rangos de impuesto y descuento
        if not 0 <= float(impuesto) <= 1:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango (0 a 1): {impuesto}")
        if not 0 <= float(descuento) <= DESCUENTO_MAXIMO:
            raise CalculoInconsistenteError(f"Descuento fuera de rango (0 a {DESCUENTO_MAXIMO}): {descuento}")
        # Un costo negativo o cero indica un cálculo inconsistente
        if total <= 0:
            raise CalculoInconsistenteError(f"El costo calculado no es válido: {total}")
        # Se redondea a dos decimales (pesos con centavos)
        return round(total, 2)

    def calcular_costo_con_iva(self, duracion: float, **parametros) -> float:
        """Atajo que aplica el IVA vigente."""
        # Reutiliza calcular_costo con el impuesto por defecto
        return self.calcular_costo(duracion, IVA, **parametros)

    @staticmethod
    def _validar_duracion(duracion: float, minimo: float, maximo: float, unidad: str) -> None:
        """Validación común de duración para todos los servicios."""
        # La duración es obligatoria
        if duracion is None:
            raise ParametroFaltanteError("duracion")
        # Debe ser numérica (se excluye bool, que en Python es subclase de int)
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool):
            raise ServicioInvalidoError(f"La duración debe ser numérica, se recibió '{duracion}'")
        # Debe estar dentro del rango permitido
        if not minimo <= duracion <= maximo:
            raise ServicioInvalidoError(f"La duración debe estar entre {minimo} y {maximo} {unidad}, se recibió {duracion}")


class ReservaSala(Servicio):
    """Reserva de salas de reuniones, cobrada por hora."""

    def __init__(self, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True) -> None:
        # Se inicializa la parte común del servicio
        super().__init__(nombre, tarifa_hora, disponible)
        # La capacidad debe ser un entero positivo
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ServicioInvalidoError(f"La capacidad de la sala debe ser un entero positivo, se recibió '{capacidad}'")
        # Número máximo de personas en la sala
        self.__capacidad = capacidad

    @property
    def capacidad(self) -> int:
        """Capacidad máxima de la sala."""
        return self.__capacidad

    def validar_parametros(self, duracion: float, **parametros) -> None:
        # Las salas se reservan entre 1 y 12 horas
        self._validar_duracion(duracion, 1, 12, "horas")
        # Se obtiene el número de asistentes (por defecto 1)
        personas = parametros.get("personas", 1)
        # Debe ser un entero positivo que no supere la capacidad
        if not isinstance(personas, int) or personas <= 0:
            raise ServicioInvalidoError(f"Número de personas inválido: '{personas}'")
        if personas > self.__capacidad:
            raise ServicioInvalidoError(f"La sala '{self.nombre}' admite {self.__capacidad} personas, se solicitaron {personas}")

    def costo_base(self, duracion: float, **parametros) -> float:
        # Costo por horas
        costo = self.tarifa_base * duracion
        # Recargo fijo del 10 % si se solicita proyector
        if parametros.get("proyector", False):
            costo *= 1.10
        return costo

    def describir(self) -> str:
        return f"Sala {self.id}: {self.nombre} | capacidad {self.__capacidad} | ${self.tarifa_base:,.0f}/hora | {'disponible' if self.disponible else 'NO disponible'}"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos, cobrado por día y por unidad."""

    def __init__(self, nombre: str, tarifa_dia: float, unidades: int, disponible: bool = True) -> None:
        # Se inicializa la parte común del servicio
        super().__init__(nombre, tarifa_dia, disponible)
        # Las unidades en inventario deben ser un entero no negativo
        if not isinstance(unidades, int) or isinstance(unidades, bool) or unidades < 0:
            raise ServicioInvalidoError(f"Las unidades disponibles deben ser un entero >= 0, se recibió '{unidades}'")
        # Inventario de equipos
        self.__unidades = unidades

    @property
    def unidades(self) -> int:
        """Unidades en inventario."""
        return self.__unidades

    def verificar_disponibilidad(self) -> None:
        # Además de la regla general, sin inventario el servicio no está disponible
        super().verificar_disponibilidad()
        if self.__unidades == 0:
            raise ServicioNoDisponibleError(f"{self.nombre} (sin unidades en inventario)")

    def validar_parametros(self, duracion: float, **parametros) -> None:
        # Los equipos se alquilan entre 1 y 30 días
        self._validar_duracion(duracion, 1, 30, "días")
        # Cantidad de equipos solicitados (por defecto 1)
        cantidad = parametros.get("cantidad", 1)
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ServicioInvalidoError(f"Cantidad de equipos inválida: '{cantidad}'")
        # No se pueden alquilar más unidades de las que hay
        if cantidad > self.__unidades:
            raise ServicioNoDisponibleError(f"{self.nombre} (solicitadas {cantidad}, disponibles {self.__unidades})")

    def costo_base(self, duracion: float, **parametros) -> float:
        # Costo por días y cantidad de equipos
        costo = self.tarifa_base * duracion * parametros.get("cantidad", 1)
        # Seguro opcional: 5 % adicional
        if parametros.get("seguro", False):
            costo *= 1.05
        return costo

    def describir(self) -> str:
        return f"Equipo {self.id}: {self.nombre} | {self.__unidades} unidades | ${self.tarifa_base:,.0f}/día | {'disponible' if self.disponible else 'NO disponible'}"


class Asesoria(Servicio):
    """Asesoría especializada, cobrada por hora según el nivel del asesor."""

    # Multiplicador de la tarifa según el nivel del asesor
    NIVELES = {"basico": 1.0, "avanzado": 1.5, "experto": 2.0}

    def __init__(self, nombre: str, tarifa_hora: float, especialidad: str, nivel: str = "basico", disponible: bool = True) -> None:
        # Se inicializa la parte común del servicio
        super().__init__(nombre, tarifa_hora, disponible)
        # La especialidad es obligatoria
        if not especialidad or not str(especialidad).strip():
            raise ParametroFaltanteError("especialidad")
        # El nivel debe ser uno de los permitidos
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(f"Nivel de asesoría '{nivel}' no válido. Opciones: {', '.join(self.NIVELES)}")
        # Área de la asesoría (ej. ciberseguridad)
        self.__especialidad = str(especialidad).strip()
        # Nivel del asesor
        self.__nivel = nivel

    @property
    def especialidad(self) -> str:
        """Área de la asesoría."""
        return self.__especialidad

    @property
    def nivel(self) -> str:
        """Nivel del asesor."""
        return self.__nivel

    def validar_parametros(self, duracion: float, **parametros) -> None:
        # Las asesorías duran entre 0.5 y 8 horas
        self._validar_duracion(duracion, 0.5, 8, "horas")
        # La modalidad debe ser presencial o virtual
        modalidad = parametros.get("modalidad", "virtual")
        if modalidad not in ("presencial", "virtual"):
            raise ServicioInvalidoError(f"Modalidad '{modalidad}' no válida (presencial o virtual)")

    def costo_base(self, duracion: float, **parametros) -> float:
        # Tarifa por hora multiplicada por el factor del nivel
        costo = self.tarifa_base * duracion * self.NIVELES[self.__nivel]
        # La modalidad presencial tiene un recargo de transporte de 20 000
        if parametros.get("modalidad", "virtual") == "presencial":
            costo += 20_000
        return costo

    def describir(self) -> str:
        return f"Asesoría {self.id}: {self.nombre} ({self.__especialidad}, nivel {self.__nivel}) | ${self.tarifa_base:,.0f}/hora | {'disponible' if self.disponible else 'NO disponible'}"
