# Software FJ — Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto de la **Fase 4 — Componente práctico** del curso **Programación (213023)**, UNAD.

Sistema orientado a objetos en Python, **sin bases de datos**, que gestiona clientes, servicios (reserva de salas, alquiler de equipos y asesorías especializadas) y reservas. Aplica abstracción, herencia, polimorfismo y encapsulación, y un manejo avanzado de excepciones. Toda la información vive en objetos y listas en memoria; el único archivo que se escribe es el **log de eventos y errores**.

**Autor:** Juan Herrera ([@juanherrera1807](https://github.com/juanherrera1807))

## Requisitos

- Python 3.10 o superior.
- Sin librerías externas: solo la biblioteca estándar.
- *(Opcional)* [`coverage`](https://coverage.readthedocs.io/) únicamente para medir la cobertura de las pruebas.

## Cómo ejecutar

```bash
# Simulación completa (35 operaciones válidas e inválidas)
python main.py

# Pruebas unitarias
python -m unittest discover -s tests -v

# Cobertura de pruebas (requiere: pip install coverage)
python -m coverage run -m unittest discover -s tests
python -m coverage report
```

Al terminar, el registro de la ejecución queda en `logs/software_fj.log`.

## Estructura del proyecto

```
.
├── main.py                    # Punto de entrada: simulación de 35 operaciones
├── software_fj/
│   ├── __init__.py            # Exporta las clases principales del paquete
│   ├── excepciones.py         # Jerarquía de excepciones personalizadas
│   ├── registro.py            # Configuración del archivo de logs
│   ├── entidad.py             # Clase abstracta Entidad (ID y fecha de creación)
│   ├── cliente.py             # Cliente con datos personales encapsulados y validados
│   ├── servicios.py           # Servicio abstracto + ReservaSala, AlquilerEquipo, Asesoria
│   ├── reserva.py             # Reserva: confirmar, cancelar y procesar
│   └── sistema.py             # SistemaGestion: listas internas y ejecución segura
├── tests/                     # 78 pruebas unitarias (cobertura del 100 %)
├── .coveragerc                # Configuración de la medición de cobertura
└── logs/                      # Se crea al ejecutar (ignorado por git)
```

## Diseño orientado a objetos

```
Entidad (abstracta)
├── Cliente
├── Reserva
└── Servicio (abstracta)
    ├── ReservaSala       — cobro por hora, capacidad, recargo por proyector
    ├── AlquilerEquipo    — cobro por día y unidad, inventario, seguro opcional
    └── Asesoria          — cobro por hora según nivel, modalidad presencial/virtual
```

| Principio | Dónde se aplica |
|---|---|
| **Abstracción** | `Entidad` y `Servicio` heredan de `ABC` y declaran métodos abstractos (`describir`, `validar`, `costo_base`, `validar_parametros`). |
| **Herencia** | `Cliente`, `Reserva` y `Servicio` heredan de `Entidad`; los tres servicios heredan de `Servicio`. |
| **Polimorfismo** | Cada servicio sobrescribe `costo_base`, `validar_parametros` y `describir`; `Reserva` y `SistemaGestion` los usan sin conocer el tipo concreto. |
| **Encapsulación** | Atributos privados (`__nombre`, `__correo`, `__estado`, ...) expuestos mediante propiedades; los *setters* de `Cliente` validan cada cambio. `SistemaGestion` devuelve tuplas para no exponer sus listas internas. |
| **Sobrecarga de métodos** | `Servicio.calcular_costo` acepta varias firmas (ver abajo). |

### Sobrecarga de `calcular_costo`

Python no tiene sobrecarga nativa, así que se simula con argumentos variables:

```python
sala.calcular_costo(2)                       # costo base
sala.calcular_costo(2, 0.19)                 # base + impuesto
sala.calcular_costo(2, 0.19, 0.15)           # base + impuesto - descuento
sala.calcular_costo(2, descuento=0.2, personas=8)  # por nombre + parámetros propios
sala.calcular_costo_con_iva(2)               # atajo con el IVA vigente (19 %)
```

## Manejo de excepciones

### Excepciones personalizadas

Todas heredan de `SoftwareFJError` y tienen un código que facilita ubicarlas en el log.

```
SoftwareFJError                    (SFJ-000)
├── ValidacionError                (SFJ-100)
│   ├── ClienteInvalidoError       (SFJ-101)
│   ├── ParametroFaltanteError     (SFJ-102)
│   └── ServicioInvalidoError      (SFJ-103)
├── ServicioNoDisponibleError      (SFJ-200)
├── ReservaInvalidaError           (SFJ-300)
├── OperacionNoPermitidaError      (SFJ-301)
├── CalculoInconsistenteError      (SFJ-400)
└── EntidadNoEncontradaError       (SFJ-500)
```

### Bloques utilizados

| Construcción | Ubicación | Propósito |
|---|---|---|
| `try/except` | `registro.configurar_logger` | Si el archivo de logs no se puede abrir, se usa la consola y la app sigue. |
| `try/except/else` | `Reserva.confirmar` | Solo cambia el estado a *confirmada* si el servicio está disponible. |
| `try/except/else/finally` | `Reserva.procesar` | Cobra la reserva; ante un error la marca como *fallida* y siempre registra el intento. |
| `try/except/else/finally` | `SistemaGestion.ejecutar` | Red de seguridad: ningún error, previsto o no, detiene la aplicación. |
| Encadenamiento `raise ... from` | `Servicio.calcular_costo`, `Reserva.__init__`, `Reserva.procesar`, `SistemaGestion.crear_servicio` | Convierte un error técnico (`ValueError`, `TypeError`) o de dominio en uno más general sin perder la causa original. |

Ejemplo de encadenamiento registrado en el log:

```
[SFJ-300] No se pudo procesar la reserva RES-0008 | causa: CalculoInconsistenteError: [SFJ-400] Descuento fuera de rango (0 a 0.5): 0.9
```

## Simulación (`main.py`)

Ejecuta **35 operaciones** agrupadas en cinco bloques. 17 terminan con éxito y 18 fallan de forma controlada, sin que el programa se detenga.

| Bloque | Ejemplos de casos inválidos |
|---|---|
| Registro de clientes | correo sin `@`, nombre faltante, documento duplicado |
| Creación de servicios | tarifa negativa, tipo inexistente, nivel de asesoría no válido, datos incompletos |
| Reservas | cliente inexistente, exceso de personas o de duración, inventario insuficiente, servicio deshabilitado, procesar sin confirmar, cancelar dos veces, descuento del 90 %, impuesto no numérico |
| Sobrecarga de `calcular_costo` | — (muestra las cuatro variantes) |
| Error inesperado | conversión imposible capturada por la red de seguridad |

## Archivo de logs

`logs/software_fj.log` registra, con fecha, nivel y módulo, cada evento relevante:

```
2026-11-14 17:07:01,530 | ERROR    | software_fj.sistema | Operación fallida 'Registrar cliente con correo inválido': [SFJ-101] Correo electrónico inválido: 'luisa-correo.com'
```

| Nivel | Uso |
|---|---|
| `INFO` | Inicio y fin de cada operación, confirmaciones, cancelaciones y cobros |
| `WARNING` | Confirmaciones rechazadas por servicio no disponible |
| `ERROR` | Errores del dominio (`SoftwareFJError`), con su causa encadenada |
| `CRITICAL` | Errores inesperados, con la traza completa |

## Pruebas

78 pruebas con `unittest` cubren el **100 % de las líneas y ramas** del código, incluidos los casos límite y las rutas defensivas (por ejemplo, el respaldo a consola cuando el archivo de logs no se puede abrir).

| Archivo | Qué prueba |
|---|---|
| `test_excepciones.py` | Jerarquía, códigos, encadenamiento y escritura del log |
| `test_cliente.py` | `Entidad` abstracta y validaciones de `Cliente` |
| `test_servicios.py` | Creación, polimorfismo, sobrecarga y disponibilidad de servicios |
| `test_reserva.py` | Ciclo de vida de la reserva y transiciones no permitidas |
| `test_sistema.py` | Listas internas, búsquedas y ejecución segura |
| `test_casos_limite.py` | Propiedades, validaciones poco frecuentes y código defensivo |
| `test_main.py` | Resumen final y ejecución de `main.py` como programa |

Las pruebas no modifican el log real: `tests/apoyo_logs.py` desvía el logger a un archivo temporal mientras se ejecuta cada módulo de pruebas (mediante `registro.redirigir_logs`) y lo restaura al terminar. Así, `logs/software_fj.log` solo contiene los eventos de la aplicación.

## Flujo de trabajo en GitHub

1. Cada módulo se desarrolla en su propia rama (`feature/...`, `test/...`, `docs/...`).
2. Cada tarea tiene un issue asociado.
3. Commits pequeños y descriptivos con prefijos convencionales (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
4. Los cambios se integran a `main` mediante pull requests.
