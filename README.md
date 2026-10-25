# Software FJ — Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto colaborativo de la **Fase 4 — Componente práctico** del curso **Programación (213023)**, UNAD.

Sistema orientado a objetos en Python, **sin bases de datos**, que gestiona clientes, servicios (reserva de salas, alquiler de equipos y asesorías especializadas) y reservas. Aplica abstracción, herencia, polimorfismo, encapsulación y un manejo avanzado de excepciones. Todos los eventos y errores se registran en un archivo de logs.

## Integrantes

| # | Integrante | Usuario GitHub | Aporte | Estado |
|---|---|---|---|---|
| 1 | Juan Herrera | [@juanherrera1807](https://github.com/juanherrera1807) | Estructura base, excepciones personalizadas y archivo de logs | ✅ |
| 2 | _completar_ | _completar_ | _completar_ | ⏳ |
| 3 | _completar_ | _completar_ | _completar_ | ⏳ |
| 4 | _completar_ | _completar_ | _completar_ | ⏳ |
| 5 | _completar_ | _completar_ | _completar_ | ⏳ |

## Requisitos

- Python 3.10 o superior
- Sin librerías externas (solo la biblioteca estándar)

## Ejecución de pruebas

```bash
python -m unittest discover -s tests -v
```

## Estructura actual

```
.
├── software_fj/
│   ├── __init__.py
│   ├── excepciones.py   # Jerarquía de excepciones personalizadas
│   └── registro.py      # Configuración del archivo de logs (logs/software_fj.log)
└── tests/
    └── test_excepciones.py
```

## Excepciones personalizadas disponibles

Todas heredan de `SoftwareFJError`, y cada una tiene un código que facilita ubicarla en el log.

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

## Uso del logger

```python
from software_fj.registro import obtener_logger

logger = obtener_logger("mi_modulo")
logger.info("Evento registrado")
logger.error("Error registrado")
```

## Flujo de trabajo en GitHub

1. Cada integrante trabaja en su propia rama.
2. Cada tarea tiene un issue asignado.
3. Se hacen commits pequeños y descriptivos (`feat:`, `fix:`, `docs:`, `test:`).
4. Los cambios se integran a `main` mediante pull requests revisados por otro integrante.
