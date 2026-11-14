"""
Programa principal: simulación del Sistema Integral de Gestión de Clientes,
Servicios y Reservas de Software FJ.

Ejecuta más de 10 operaciones completas (válidas e inválidas) para demostrar
que el sistema maneja los errores de forma controlada, los registra en el
archivo logs/software_fj.log y nunca se detiene.

Uso:
    python main.py
"""

from software_fj import SistemaGestion  # Fachada del sistema
from software_fj.registro import ARCHIVO_LOGS  # Ruta del archivo de logs
from software_fj.servicios import IVA  # Impuesto por defecto

# Ancho de las líneas separadoras en la consola
ANCHO = 78


def imprimir_resultado(numero: int, resultado) -> None:
    """Muestra en consola el resultado de una operación simulada."""
    # Marca visual según el resultado
    marca = "OK   " if resultado.exitosa else "ERROR"
    print(f"{numero:>2}. [{marca}] {resultado.descripcion}")
    # Si fue exitosa se muestra el valor devuelto; si no, el mensaje de error
    detalle = resultado.valor if resultado.exitosa else resultado.error
    if detalle is not None:
        print(f"      -> {detalle}")


def flujo_completo(sistema: SistemaGestion, documento: str, servicio_id: str, duracion: float,
                   impuesto: float = IVA, descuento: float = 0.0, **parametros):
    """Crea, confirma y procesa una reserva. Devuelve la reserva final."""
    # Se crea la reserva en estado pendiente
    reserva = sistema.crear_reserva(documento, servicio_id, duracion, **parametros)
    # Se confirma (verifica disponibilidad del servicio)
    reserva.confirmar()
    # Se procesa (calcula el costo con impuesto y descuento)
    reserva.procesar(impuesto, descuento)
    return reserva


def ejecutar_simulacion() -> tuple[list, SistemaGestion]:
    """Ejecuta todas las operaciones simuladas y devuelve sus resultados."""
    sistema = SistemaGestion()
    # Lista donde se acumulan los resultados de cada operación
    resultados = []

    def correr(descripcion, operacion):
        # Ejecuta la operación de forma segura, la muestra y guarda el resultado
        resultado = sistema.ejecutar(descripcion, operacion)
        resultados.append(resultado)
        imprimir_resultado(len(resultados), resultado)
        return resultado

    # ---------------------------------------------------------------
    print("=" * ANCHO)
    print("SOFTWARE FJ - Simulación del sistema de gestión".center(ANCHO))
    print("=" * ANCHO)

    print("\n--- Registro de clientes ---")
    correr("Registrar cliente válido: Ana Gómez",
           lambda: sistema.registrar_cliente("Ana Gómez", "1012345678", "ana.gomez@correo.com", "3001234567"))
    correr("Registrar cliente válido: Carlos Pérez",
           lambda: sistema.registrar_cliente("Carlos Pérez", "79888777", "carlos@empresa.co", "3159876543"))
    correr("Registrar cliente con correo inválido",
           lambda: sistema.registrar_cliente("Luisa Martínez", "52111222", "luisa-correo.com", "3104445566"))
    correr("Registrar cliente sin nombre (parámetro faltante)",
           lambda: sistema.registrar_cliente("", "1033444555", "sin.nombre@correo.com", "3201112233"))
    correr("Registrar cliente con documento duplicado",
           lambda: sistema.registrar_cliente("Ana Duplicada", "1012345678", "otra@correo.com", "3001112222"))

    print("\n--- Creación de servicios ---")
    sala = correr("Crear sala de reuniones 'Sala Andes'",
                  lambda: sistema.crear_servicio("sala", nombre="Sala Andes", tarifa_hora=50_000, capacidad=10))
    sala_pequena = correr("Crear sala 'Sala Caribe'",
                          lambda: sistema.crear_servicio("sala", nombre="Sala Caribe", tarifa_hora=35_000, capacidad=4))
    equipo = correr("Crear alquiler de equipo 'Portátil i7'",
                    lambda: sistema.crear_servicio("equipo", nombre="Portátil i7", tarifa_dia=80_000, unidades=5))
    asesoria = correr("Crear asesoría 'Ciberseguridad' nivel experto",
                      lambda: sistema.crear_servicio("asesoria", nombre="Auditoría de seguridad", tarifa_hora=120_000,
                                                     especialidad="Ciberseguridad", nivel="experto"))
    correr("Crear servicio con tarifa negativa",
           lambda: sistema.crear_servicio("sala", nombre="Sala Error", tarifa_hora=-10_000, capacidad=5))
    correr("Crear servicio de tipo inexistente 'transporte'",
           lambda: sistema.crear_servicio("transporte", nombre="Van", tarifa=1000))
    correr("Crear asesoría con nivel inválido 'maestro'",
           lambda: sistema.crear_servicio("asesoria", nombre="Asesoría X", tarifa_hora=90_000,
                                          especialidad="Redes", nivel="maestro"))
    correr("Crear equipo con datos incompletos (sin unidades)",
           lambda: sistema.crear_servicio("equipo", nombre="Proyector", tarifa_dia=40_000))

    # IDs de los servicios creados correctamente (se usan en las reservas)
    id_sala = sala.valor.id
    id_sala_pequena = sala_pequena.valor.id
    id_equipo = equipo.valor.id
    id_asesoria = asesoria.valor.id

    print("\n--- Reservas ---")
    correr("Reserva exitosa: Ana, Sala Andes 3 h, 8 personas, con proyector e IVA",
           lambda: flujo_completo(sistema, "1012345678", id_sala, 3, personas=8, proyector=True))
    correr("Reserva exitosa: Carlos, 2 portátiles por 5 días con seguro y 10 % de descuento",
           lambda: flujo_completo(sistema, "79888777", id_equipo, 5, descuento=0.10, cantidad=2, seguro=True))
    correr("Reserva exitosa: Ana, asesoría presencial de 2 h sin impuesto",
           lambda: flujo_completo(sistema, "1012345678", id_asesoria, 2, impuesto=0.0, modalidad="presencial"))
    correr("Reserva fallida: Sala Caribe para 12 personas (supera capacidad)",
           lambda: sistema.crear_reserva("79888777", id_sala_pequena, 2, personas=12))
    correr("Reserva fallida: cliente inexistente",
           lambda: sistema.crear_reserva("99999999", id_sala, 2))
    correr("Reserva fallida: 10 portátiles (solo hay 5 en inventario)",
           lambda: sistema.crear_reserva("1012345678", id_equipo, 2, cantidad=10))
    correr("Reserva fallida: duración de 20 horas en sala (máximo 12)",
           lambda: sistema.crear_reserva("1012345678", id_sala, 20))

    # Reserva pendiente sobre la sala Caribe, que luego se deshabilita
    pendiente = correr("Crear reserva pendiente: Carlos, Sala Caribe 2 h",
                       lambda: sistema.crear_reserva("79888777", id_sala_pequena, 2, personas=3))
    correr("Deshabilitar 'Sala Caribe' por mantenimiento",
           lambda: sistema.buscar_servicio(id_sala_pequena).deshabilitar())
    correr("Confirmar reserva sobre servicio no disponible",
           lambda: pendiente.valor.confirmar())
    correr("Procesar reserva sin confirmar (operación no permitida)",
           lambda: pendiente.valor.procesar())
    correr("Cancelar reserva pendiente",
           lambda: pendiente.valor.cancelar("Sala en mantenimiento"))
    correr("Cancelar de nuevo la misma reserva (operación no permitida)",
           lambda: pendiente.valor.cancelar())

    # Reserva que falla durante el procesamiento por un descuento inválido
    abusiva = correr("Crear y confirmar reserva de asesoría 1 h",
                     lambda: _crear_y_confirmar(sistema, "79888777", id_asesoria, 1))
    correr("Procesar con descuento del 90 % (cálculo inconsistente, error encadenado)",
           lambda: abusiva.valor.procesar(IVA, 0.9))
    correr("Cálculo con impuesto no numérico (error encadenado)",
           lambda: sistema.buscar_servicio(id_sala).calcular_costo(2, "diez"))
    correr("Cancelar una reserva ya procesada (operación no permitida)",
           lambda: sistema.reservas[0].cancelar())

    print("\n--- Sobrecarga de calcular_costo (Sala Andes, 2 h) ---")
    servicio_sala = sistema.buscar_servicio(id_sala)
    correr("calcular_costo(duracion)", lambda: servicio_sala.calcular_costo(2))
    correr("calcular_costo(duracion, impuesto)", lambda: servicio_sala.calcular_costo(2, IVA))
    correr("calcular_costo(duracion, impuesto, descuento)", lambda: servicio_sala.calcular_costo(2, IVA, 0.15))
    correr("calcular_costo(duracion, descuento=..., personas=...)",
           lambda: servicio_sala.calcular_costo(2, descuento=0.2, personas=5))

    print("\n--- Error inesperado (red de seguridad) ---")
    correr("Operación con un fallo no previsto (conversión imposible)", lambda: int("no-es-numero"))

    return resultados, sistema


def _crear_y_confirmar(sistema: SistemaGestion, documento: str, servicio_id: str, duracion: float, **parametros):
    """Crea una reserva y la deja confirmada (sin procesar)."""
    reserva = sistema.crear_reserva(documento, servicio_id, duracion, **parametros)
    reserva.confirmar()
    return reserva


def imprimir_resumen(resultados: list, sistema: SistemaGestion) -> None:
    """Muestra el resumen final de la simulación."""
    exitosas = sum(1 for r in resultados if r.exitosa)
    print("\n" + "=" * ANCHO)
    print("RESUMEN".center(ANCHO))
    print("=" * ANCHO)
    print(f"Operaciones ejecutadas: {len(resultados)}  |  exitosas: {exitosas}  |  con error controlado: {len(resultados) - exitosas}")
    print(f"Clientes registrados: {len(sistema.clientes)}  |  servicios: {len(sistema.servicios)}  |  reservas: {len(sistema.reservas)}")
    print("\nEstado final de las reservas:")
    for reserva in sistema.reservas:
        print(f"  - {reserva.describir()}")
    print(f"\nEl sistema terminó sin interrupciones. Revise el log en: {ARCHIVO_LOGS}")


if __name__ == "__main__":
    # Punto de entrada: se ejecuta la simulación y se muestra el resumen
    resultados_finales, sistema_final = ejecutar_simulacion()
    imprimir_resumen(resultados_finales, sistema_final)
