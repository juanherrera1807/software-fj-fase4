"""Pruebas de la clase abstracta Entidad y de la clase Cliente."""

import unittest

from apoyo_logs import setUpModule, tearDownModule  # noqa: F401 - aísla el archivo de logs
from software_fj.cliente import Cliente
from software_fj.entidad import Entidad
from software_fj.excepciones import ClienteInvalidoError, ParametroFaltanteError


def nuevo_cliente(documento: str = "1012345678") -> Cliente:
    return Cliente("Ana Gómez", documento, "ana@correo.com", "3001234567")


class TestEntidad(unittest.TestCase):
    def test_entidad_no_se_puede_instanciar(self):
        with self.assertRaises(TypeError):
            Entidad("X")

    def test_ids_consecutivos_por_tipo(self):
        primero, segundo = nuevo_cliente("11111111"), nuevo_cliente("22222222")
        self.assertTrue(primero.id.startswith("CLI-"))
        self.assertEqual(int(segundo.id[4:]), int(primero.id[4:]) + 1)

    def test_str_usa_describir(self):
        cliente = nuevo_cliente()
        self.assertEqual(str(cliente), cliente.describir())


class TestCliente(unittest.TestCase):
    def test_cliente_valido(self):
        cliente = nuevo_cliente()
        self.assertEqual(cliente.nombre, "Ana Gómez")
        self.assertTrue(cliente.validar())

    def test_correo_se_normaliza_en_minusculas(self):
        cliente = Cliente("Ana Gómez", "1012345678", "ANA@Correo.COM", "3001234567")
        self.assertEqual(cliente.correo, "ana@correo.com")

    def test_correo_invalido(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("Ana Gómez", "1012345678", "ana-correo.com", "3001234567")

    def test_documento_con_letras(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("Ana Gómez", "10A2345678", "ana@correo.com", "3001234567")

    def test_telefono_corto(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("Ana Gómez", "1012345678", "ana@correo.com", "300")

    def test_nombre_faltante(self):
        with self.assertRaises(ParametroFaltanteError) as contexto:
            Cliente("   ", "1012345678", "ana@correo.com", "3001234567")
        self.assertEqual(contexto.exception.parametro, "nombre")

    def test_tipo_incorrecto(self):
        with self.assertRaises(ClienteInvalidoError):
            Cliente("Ana Gómez", 1012345678, "ana@correo.com", "3001234567")

    def test_setter_valida_al_modificar(self):
        cliente = nuevo_cliente()
        with self.assertRaises(ClienteInvalidoError):
            cliente.telefono = "abc"
        self.assertEqual(cliente.telefono, "3001234567")

    def test_descripcion_no_expone_documento(self):
        self.assertNotIn("1012345678", nuevo_cliente().describir())


if __name__ == "__main__":
    unittest.main()
