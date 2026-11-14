"""Pruebas de SistemaGestion y de la simulación completa de main.py."""

import contextlib
import io
import unittest

from apoyo_logs import setUpModule, tearDownModule  # noqa: F401 - aísla el archivo de logs
from software_fj.excepciones import ClienteInvalidoError, EntidadNoEncontradaError, ServicioInvalidoError
from software_fj.sistema import SistemaGestion


class TestSistemaGestion(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaGestion()
        self.sistema.registrar_cliente("Ana Gómez", "1012345678", "ana@correo.com", "3001234567")
        self.sala = self.sistema.crear_servicio("sala", nombre="Sala Andes", tarifa_hora=50_000, capacidad=10)

    def test_cliente_duplicado(self):
        with self.assertRaises(ClienteInvalidoError):
            self.sistema.registrar_cliente("Otra", "1012345678", "otra@correo.com", "3001112222")

    def test_tipo_servicio_inexistente(self):
        with self.assertRaises(ServicioInvalidoError):
            self.sistema.crear_servicio("transporte", nombre="Van")

    def test_servicio_datos_incompletos_encadena_type_error(self):
        with self.assertRaises(ServicioInvalidoError) as contexto:
            self.sistema.crear_servicio("equipo", nombre="Proyector", tarifa_dia=1000)
        self.assertIsInstance(contexto.exception.__cause__, TypeError)

    def test_crear_y_buscar_reserva(self):
        reserva = self.sistema.crear_reserva("1012345678", self.sala.id, 2, personas=3)
        self.assertIs(self.sistema.buscar_reserva(reserva.id), reserva)

    def test_reserva_cliente_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.sistema.crear_reserva("99999999", self.sala.id, 2)

    def test_listas_internas_no_se_exponen(self):
        self.assertIsInstance(self.sistema.clientes, tuple)
        self.assertEqual(len(self.sistema.clientes), 1)

    def test_ejecutar_captura_error_del_dominio(self):
        resultado = self.sistema.ejecutar("falla", lambda: self.sistema.buscar_servicio("SRV-9999"))
        self.assertFalse(resultado.exitosa)
        self.assertIn("SFJ-500", resultado.error)

    def test_ejecutar_captura_error_inesperado(self):
        resultado = self.sistema.ejecutar("división", lambda: 1 / 0)
        self.assertFalse(resultado.exitosa)
        self.assertIn("ZeroDivisionError", resultado.error)

    def test_ejecutar_exitoso(self):
        resultado = self.sistema.ejecutar("suma", lambda: 2 + 2)
        self.assertTrue(resultado.exitosa)
        self.assertEqual(resultado.valor, 4)


class TestSimulacion(unittest.TestCase):
    def test_simulacion_completa_no_se_detiene(self):
        import main

        with contextlib.redirect_stdout(io.StringIO()):
            resultados, sistema = main.ejecutar_simulacion()
        self.assertGreaterEqual(len(resultados), 10)
        self.assertTrue(any(r.exitosa for r in resultados))
        self.assertTrue(any(not r.exitosa for r in resultados))
        self.assertEqual(len(sistema.clientes), 2)


if __name__ == "__main__":
    unittest.main()
