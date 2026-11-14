"""Pruebas de la clase Reserva y de su ciclo de vida."""

import unittest

from software_fj.cliente import Cliente
from software_fj.excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from software_fj.reserva import EstadoReserva, Reserva
from software_fj.servicios import IVA, ReservaSala


def nuevo_cliente() -> Cliente:
    return Cliente("Ana Gómez", "1012345678", "ana@correo.com", "3001234567")


def nueva_sala() -> ReservaSala:
    return ReservaSala("Sala Andes", 50_000, 10)


class TestReserva(unittest.TestCase):
    def setUp(self):
        self.reserva = Reserva(nuevo_cliente(), nueva_sala(), 2, personas=5)

    def test_flujo_completo(self):
        self.assertIs(self.reserva.estado, EstadoReserva.PENDIENTE)
        self.reserva.confirmar()
        self.assertIs(self.reserva.estado, EstadoReserva.CONFIRMADA)
        self.assertEqual(self.reserva.procesar(IVA), 119_000)
        self.assertIs(self.reserva.estado, EstadoReserva.PROCESADA)
        self.assertEqual(self.reserva.costo, 119_000)

    def test_reserva_invalida_encadena_causa(self):
        with self.assertRaises(ReservaInvalidaError) as contexto:
            Reserva(nuevo_cliente(), nueva_sala(), 50)
        self.assertIsInstance(contexto.exception.__cause__, ServicioInvalidoError)

    def test_reserva_sin_cliente(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva("cliente", nueva_sala(), 2)

    def test_reserva_sin_servicio(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva(nuevo_cliente(), "sala", 2)

    def test_confirmar_servicio_no_disponible(self):
        self.reserva.servicio.deshabilitar()
        with self.assertRaises(ServicioNoDisponibleError):
            self.reserva.confirmar()
        self.assertIs(self.reserva.estado, EstadoReserva.PENDIENTE)

    def test_procesar_sin_confirmar(self):
        with self.assertRaises(OperacionNoPermitidaError):
            self.reserva.procesar()

    def test_confirmar_dos_veces(self):
        self.reserva.confirmar()
        with self.assertRaises(OperacionNoPermitidaError):
            self.reserva.confirmar()

    def test_cancelar_procesada(self):
        self.reserva.confirmar()
        self.reserva.procesar()
        with self.assertRaises(OperacionNoPermitidaError):
            self.reserva.cancelar()

    def test_cancelar_pendiente(self):
        self.reserva.cancelar("prueba")
        self.assertIs(self.reserva.estado, EstadoReserva.CANCELADA)

    def test_procesar_con_error_marca_fallida(self):
        self.reserva.confirmar()
        with self.assertRaises(ReservaInvalidaError) as contexto:
            self.reserva.procesar(IVA, 0.9)
        self.assertIsInstance(contexto.exception.__cause__, CalculoInconsistenteError)
        self.assertIs(self.reserva.estado, EstadoReserva.FALLIDA)

    def test_descripcion(self):
        self.assertIn("pendiente", self.reserva.describir())


if __name__ == "__main__":
    unittest.main()
