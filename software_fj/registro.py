"""
Módulo de registro (logging) del sistema Software FJ.

Configura un único logger que escribe todos los eventos y errores en un
archivo de texto. Es el único uso de archivos del sistema, tal como lo
exige el enunciado (no se usan bases de datos).
"""

import logging  # Módulo estándar de Python para registrar eventos
from pathlib import Path  # Manejo de rutas independiente del sistema operativo

# Carpeta donde se guardará el archivo de logs (junto a la raíz del proyecto)
CARPETA_LOGS = Path(__file__).resolve().parent.parent / "logs"
# Ruta completa del archivo de logs
ARCHIVO_LOGS = CARPETA_LOGS / "software_fj.log"
# Formato de cada línea: fecha, nivel, módulo y mensaje
FORMATO_LOG = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
# Nombre del logger raíz del sistema
NOMBRE_LOGGER = "software_fj"


def configurar_logger(archivo: Path = ARCHIVO_LOGS, nivel: int = logging.INFO) -> logging.Logger:
    """Crea (una sola vez) y devuelve el logger principal del sistema."""
    # Se obtiene el logger por nombre; logging garantiza que sea único
    logger = logging.getLogger(NOMBRE_LOGGER)
    # Si ya tiene manejadores, ya fue configurado: se devuelve tal cual
    if logger.handlers:
        return logger
    # Se define el nivel mínimo de mensajes que se registrarán
    logger.setLevel(nivel)
    try:
        # Se crea la carpeta de logs si no existe
        Path(archivo).parent.mkdir(parents=True, exist_ok=True)
        # Manejador que escribe en el archivo con codificación UTF-8 (tildes, ñ)
        manejador = logging.FileHandler(archivo, encoding="utf-8")
    except OSError as error:
        # Si no se puede escribir en disco, se registra en consola para no detener la app
        manejador = logging.StreamHandler()
        # Se avisa por consola del problema con el archivo
        print(f"Advertencia: no se pudo abrir el archivo de logs ({error}). Se usará la consola.")
    # Se asigna el formato a las líneas del log
    manejador.setFormatter(logging.Formatter(FORMATO_LOG))
    # Se agrega el manejador al logger
    logger.addHandler(manejador)
    # Se evita que los mensajes se dupliquen en el logger raíz de Python
    logger.propagate = False
    # Se devuelve el logger listo para usar
    return logger


def obtener_logger(modulo: str) -> logging.Logger:
    """Devuelve un logger hijo para un módulo concreto (ej. 'software_fj.cliente')."""
    # Se garantiza que el logger principal esté configurado
    configurar_logger()
    # Se devuelve un logger hijo que hereda la configuración del principal
    return logging.getLogger(f"{NOMBRE_LOGGER}.{modulo}")
