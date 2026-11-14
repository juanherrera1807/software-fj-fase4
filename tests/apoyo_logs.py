"""
Apoyo compartido para las pruebas: aísla el archivo de logs.

Cada módulo de pruebas importa ``setUpModule`` y ``tearDownModule`` desde
aquí. Así, mientras se ejecutan sus pruebas, el logger escribe en un archivo
temporal y el log real de la aplicación (logs/software_fj.log) no se modifica.
"""

import tempfile
from pathlib import Path

from software_fj.registro import ARCHIVO_LOGS, redirigir_logs

# Carpeta temporal activa mientras se ejecuta un módulo de pruebas
_carpeta_temporal = None


def setUpModule() -> None:
    """Antes de las pruebas de un módulo: el log se desvía a un archivo temporal."""
    global _carpeta_temporal
    _carpeta_temporal = tempfile.TemporaryDirectory()
    redirigir_logs(Path(_carpeta_temporal.name) / "pruebas.log")


def tearDownModule() -> None:
    """Después de las pruebas: se restaura el log real y se borra el temporal."""
    # Primero se cierra el archivo temporal (en Windows no se puede borrar abierto)
    redirigir_logs(ARCHIVO_LOGS)
    _carpeta_temporal.cleanup()
