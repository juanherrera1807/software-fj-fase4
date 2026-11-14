"""
Pruebas de casos límite y de código defensivo.

Complementan las pruebas de cada módulo para cubrir propiedades de solo
lectura, validaciones poco frecuentes y rutas de error que en el flujo
normal no se alcanzan (por ejemplo, un archivo de logs que no se puede abrir).
"""

import contextlib
import io
import logging
import unittest
from datetime import datetime
from unittest import mock

from software_fj.cliente import Cliente
from software_fj.excepciones import (
    CalculoInconsistenteError,
    EntidadNoEncontradaError,
    ParametroFaltanteError,
    ServicioInvalidoError,
)
from software_fj.registro import NOMBRE_LOGGER, configurar_logger
from software_fj.reserva import Reserva
from software_fj.servicios import AlquilerEquipo, Asesoria, ReservaSala, Servicio
from software_fj.sistema import SistemaGestion


def nuevo_cliente() -> Cliente:
    """Cliente válido reutilizado en varias pruebas."""
    return Cliente("Ana Gómez", "1012345678", "ana@correo.com", "3001234567")


class ServicioDeCostoCero(Servicio):
    """Doble de prueba: un servicio cuyo costo base es cero.

    Permite comprobar la protección contra costos no positivos, que con los
    servicios reales no puede ocurrir porque sus tarifas siempre son mayores que cero.
    """

    def costo_base(self, duracion: float, **parametros) -> float:
        return 0.0

    def validar_parametros(self, duracion: float, **parametros) -> None:
        return None

    def describir(self) -> str:
        return "Servicio de prueba con costo cero"


class TestEntidadPropiedades(unittest.TestCase):
    def test_fecha_creacion_es_un_datetime(self):
        cliente = nuevo_cliente()
        self.assertIsInstance(cliente.fecha_creacion, datetime)


class TestServiciosCasosLimite(unittest.TestCase):
    def setUp(self):
        self.sala = ReservaSala("Sala Andes", 50_000, 10)
        self.equipo = AlquilerEquipo("Portátil i7", 80_000, 3)
        self.asesoria = Asesoria("Auditoría", 100_000, "Ciberseguridad", "experto")

    def test_validar_servicio_correcto(self):
        self.assertTrue(self.sala.validar())

    def test_validar_detecta_tarifa_corrupta(self):
        # Se altera el atributo privado para simular un estado interno corrupto
        self.sala._Servicio__tarifa_base = 0
        with self.assertRaises(ServicioInvalidoError):
            self.sala.validar()

    def test_impuesto_fuera_de_rango(self):
        with self.assertRaises(CalculoInconsistenteError):
            self.sala.calcular_costo(2, 1.5)

    def test_costo_total_no_positivo(self):
        servicio = ServicioDeCostoCero("Gratis", 1)
        with self.assertRaises(CalculoInconsistenteError):
            servicio.calcular_costo(1)

    def test_duracion_faltante(self):
        with self.assertRaises(ParametroFaltanteError):
            self.sala.calcular_costo(None)

    def test_personas_no_positivas(self):
        with self.assertRaises(ServicioInvalidoError):
            self.sala.calcular_costo(2, personas=0)

    def test_unidades_negativas_al_crear_equipo(self):
        with self.assertRaises(ServicioInvalidoError):
            AlquilerEquipo("Tablet", 30_000, -1)

    def test_cantidad_de_equipos_no_positiva(self):
        with self.assertRaises(ServicioInvalidoError):
            self.equipo.calcular_costo(2, cantidad=0)

    def test_propiedades_de_solo_lectura(self):
        self.assertEqual(self.sala.capacidad, 10)
        self.assertEqual(self.equipo.unidades, 3)
        self.assertEqual(self.asesoria.especialidad, "Ciberseguridad")
        self.assertEqual(self.asesoria.nivel, "experto")


class TestReservaPropiedades(unittest.TestCase):
    def test_cliente_y_duracion(self):
        cliente = nuevo_cliente()
        reserva = Reserva(cliente, ReservaSala("Sala Andes", 50_000, 10), 2)
        self.assertIs(reserva.cliente, cliente)
        self.assertEqual(reserva.duracion, 2)


class TestSistemaCasosLimite(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaGestion()
        self.sistema.registrar_cliente("Ana Gómez", "1012345678", "ana@correo.com", "3001234567")
        self.sala = self.sistema.crear_servicio("sala", nombre="Sala Andes", tarifa_hora=50_000, capacidad=10)

    def test_servicios_registrados(self):
        self.assertEqual(self.sistema.servicios, (self.sala,))

    def test_buscar_reserva_inexistente(self):
        # Con una reserva existente, la búsqueda recorre la lista sin encontrar el ID
        self.sistema.crear_reserva("1012345678", self.sala.id, 2)
        with self.assertRaises(EntidadNoEncontradaError):
            self.sistema.buscar_reserva("RES-9999")


class TestRegistroRespaldo(unittest.TestCase):
    def test_usa_consola_si_no_puede_abrir_el_archivo(self):
        logger_principal = logging.getLogger(NOMBRE_LOGGER)
        manejadores_originales = list(logger_principal.handlers)
        for manejador in manejadores_originales:
            logger_principal.removeHandler(manejador)
        salida = io.StringIO()
        try:
            # Se simula un disco sin permisos de escritura
            with mock.patch("software_fj.registro.logging.FileHandler", side_effect=OSError("sin permisos")), \
                    contextlib.redirect_stdout(salida):
                logger = configurar_logger()
            self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
            self.assertIn("no se pudo abrir el archivo de logs", salida.getvalue())
        finally:
            for manejador in list(logger_principal.handlers):
                logger_principal.removeHandler(manejador)
            for manejador in manejadores_originales:
                logger_principal.addHandler(manejador)


if __name__ == "__main__":
    unittest.main()
