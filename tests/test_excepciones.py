"""
Pruebas de las excepciones personalizadas y del registro (logs).

Ejecutar desde la raíz del proyecto con:
    python -m unittest discover -s tests -v
"""

import logging
import tempfile
import unittest
from pathlib import Path

from software_fj.excepciones import (
    CalculoInconsistenteError,
    ClienteInvalidoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    SoftwareFJError,
    ValidacionError,
)
from software_fj.registro import ARCHIVO_LOGS, NOMBRE_LOGGER, configurar_logger, obtener_logger


class TestExcepciones(unittest.TestCase):
    def test_todas_heredan_de_la_base(self):
        clases = (ClienteInvalidoError, ParametroFaltanteError, ServicioInvalidoError, ServicioNoDisponibleError,
                  ReservaInvalidaError, OperacionNoPermitidaError, CalculoInconsistenteError, EntidadNoEncontradaError)
        for clase in clases:
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, SoftwareFJError))

    def test_errores_de_validacion_comparten_padre(self):
        for clase in (ClienteInvalidoError, ParametroFaltanteError, ServicioInvalidoError):
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, ValidacionError))

    def test_codigo_y_mensaje_en_texto(self):
        error = ClienteInvalidoError("correo inválido")
        self.assertEqual(error.codigo, "SFJ-101")
        self.assertEqual(str(error), "[SFJ-101] correo inválido")

    def test_parametro_faltante_guarda_el_nombre(self):
        error = ParametroFaltanteError("telefono")
        self.assertEqual(error.parametro, "telefono")
        self.assertIn("telefono", str(error))

    def test_entidad_no_encontrada(self):
        self.assertIn("SFJ-500", str(EntidadNoEncontradaError("cliente", "123")))

    def test_encadenamiento_conserva_la_causa(self):
        with self.assertRaises(CalculoInconsistenteError) as contexto:
            try:
                float("abc")
            except ValueError as error:
                raise CalculoInconsistenteError("cálculo inválido") from error
        self.assertIsInstance(contexto.exception.__cause__, ValueError)


class TestRegistro(unittest.TestCase):
    def test_logger_hijo_hereda_del_principal(self):
        logger = obtener_logger("prueba")
        self.assertEqual(logger.name, f"{NOMBRE_LOGGER}.prueba")
        self.assertTrue(logging.getLogger(NOMBRE_LOGGER).handlers)

    def test_archivo_de_logs_por_defecto(self):
        self.assertEqual(ARCHIVO_LOGS.name, "software_fj.log")

    def test_escribe_en_archivo(self):
        logger_principal = logging.getLogger(NOMBRE_LOGGER)
        manejadores_originales = list(logger_principal.handlers)
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "sub" / "prueba.log"
            for manejador in manejadores_originales:
                logger_principal.removeHandler(manejador)
            try:
                configurar_logger(archivo).error("mensaje de prueba")
                for manejador in logger_principal.handlers:
                    manejador.close()
                self.assertIn("mensaje de prueba", archivo.read_text(encoding="utf-8"))
            finally:
                for manejador in list(logger_principal.handlers):
                    logger_principal.removeHandler(manejador)
                for manejador in manejadores_originales:
                    logger_principal.addHandler(manejador)


if __name__ == "__main__":
    unittest.main()
