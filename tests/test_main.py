"""Pruebas del punto de entrada main.py (resumen e inicio del programa)."""

import contextlib
import io
import runpy
import unittest
from pathlib import Path

import main

# Ruta de main.py, usada para ejecutarlo como lo haría el usuario
RUTA_MAIN = Path(__file__).resolve().parent.parent / "main.py"


class TestMain(unittest.TestCase):
    def test_imprimir_resumen(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            resultados, sistema = main.ejecutar_simulacion()
            main.imprimir_resumen(resultados, sistema)
        texto = salida.getvalue()
        self.assertIn("RESUMEN", texto)
        self.assertIn(f"Operaciones ejecutadas: {len(resultados)}", texto)
        self.assertIn("terminó sin interrupciones", texto)

    def test_ejecucion_como_programa(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            runpy.run_path(str(RUTA_MAIN), run_name="__main__")
        self.assertIn("RESUMEN", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
