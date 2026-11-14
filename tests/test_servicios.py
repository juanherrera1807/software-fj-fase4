"""Pruebas de la clase abstracta Servicio y de los servicios especializados."""

import unittest

from software_fj.excepciones import (
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioInvalidoError,
    ServicioNoDisponibleError,
)
from software_fj.servicios import IVA, AlquilerEquipo, Asesoria, ReservaSala, Servicio


def nueva_sala(capacidad: int = 10) -> ReservaSala:
    return ReservaSala("Sala Andes", 50_000, capacidad)


class TestCreacionDeServicios(unittest.TestCase):
    def test_servicio_no_se_puede_instanciar(self):
        with self.assertRaises(TypeError):
            Servicio("Genérico", 1000)

    def test_tarifa_negativa(self):
        with self.assertRaises(ServicioInvalidoError):
            ReservaSala("Sala", -1, 5)

    def test_capacidad_invalida(self):
        with self.assertRaises(ServicioInvalidoError):
            ReservaSala("Sala", 1000, 0)

    def test_nombre_faltante(self):
        with self.assertRaises(ParametroFaltanteError):
            AlquilerEquipo("", 1000, 3)

    def test_asesoria_nivel_invalido(self):
        with self.assertRaises(ServicioInvalidoError):
            Asesoria("Asesoría", 1000, "Redes", nivel="maestro")

    def test_asesoria_sin_especialidad(self):
        with self.assertRaises(ParametroFaltanteError):
            Asesoria("Asesoría", 1000, "")


class TestCalculoDeCostos(unittest.TestCase):
    def test_polimorfismo_costo(self):
        casos = [
            (nueva_sala(), 2, {}, 100_000),
            (AlquilerEquipo("Portátil", 80_000, 5), 3, {"cantidad": 2}, 480_000),
            (Asesoria("Auditoría", 100_000, "Seguridad", "avanzado"), 2, {}, 300_000),
        ]
        for servicio, duracion, parametros, esperado in casos:
            with self.subTest(servicio=type(servicio).__name__):
                self.assertEqual(servicio.calcular_costo(duracion, **parametros), esperado)

    def test_sobrecarga_calcular_costo(self):
        sala = nueva_sala()
        self.assertEqual(sala.calcular_costo(2), 100_000)
        self.assertEqual(sala.calcular_costo(2, IVA), 119_000)
        self.assertEqual(sala.calcular_costo(2, IVA, 0.15), 101_150)
        self.assertEqual(sala.calcular_costo(2, descuento=0.2), 80_000)
        self.assertEqual(sala.calcular_costo_con_iva(2), 119_000)

    def test_recargos_opcionales(self):
        self.assertEqual(nueva_sala().calcular_costo(1, proyector=True), 55_000)
        self.assertEqual(AlquilerEquipo("Portátil", 100_000, 2).calcular_costo(1, seguro=True), 105_000)
        self.assertEqual(Asesoria("A", 100_000, "Redes").calcular_costo(1, modalidad="presencial"), 120_000)

    def test_sobrecarga_demasiados_argumentos(self):
        with self.assertRaises(CalculoInconsistenteError):
            nueva_sala().calcular_costo(2, 0.19, 0.1, 5)

    def test_descuento_excesivo(self):
        with self.assertRaises(CalculoInconsistenteError):
            nueva_sala().calcular_costo(2, IVA, 0.9)

    def test_impuesto_no_numerico_encadena_causa(self):
        with self.assertRaises(CalculoInconsistenteError) as contexto:
            nueva_sala().calcular_costo(2, "diez")
        self.assertIsInstance(contexto.exception.__cause__, ValueError)


class TestValidacionYDisponibilidad(unittest.TestCase):
    def test_personas_superan_capacidad(self):
        with self.assertRaises(ServicioInvalidoError):
            nueva_sala(4).validar_parametros(2, personas=5)

    def test_duracion_fuera_de_rango(self):
        with self.assertRaises(ServicioInvalidoError):
            nueva_sala().validar_parametros(20)

    def test_duracion_no_numerica(self):
        with self.assertRaises(ServicioInvalidoError):
            nueva_sala().validar_parametros("dos")

    def test_equipo_sin_inventario_no_disponible(self):
        with self.assertRaises(ServicioNoDisponibleError):
            AlquilerEquipo("Proyector", 40_000, 0).verificar_disponibilidad()

    def test_equipo_cantidad_mayor_al_inventario(self):
        with self.assertRaises(ServicioNoDisponibleError):
            AlquilerEquipo("Portátil", 80_000, 2).validar_parametros(1, cantidad=5)

    def test_asesoria_modalidad_invalida(self):
        with self.assertRaises(ServicioInvalidoError):
            Asesoria("Asesoría", 1000, "Redes").validar_parametros(1, modalidad="satelital")

    def test_deshabilitar_y_habilitar(self):
        sala = nueva_sala()
        sala.deshabilitar()
        with self.assertRaises(ServicioNoDisponibleError):
            sala.verificar_disponibilidad()
        sala.habilitar()
        sala.verificar_disponibilidad()


if __name__ == "__main__":
    unittest.main()
