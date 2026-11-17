"""Pruebas unitarias automatizadas para verificar requisitos de la Fase 4.

Ejecute: python -m unittest pruebas -v
"""

import unittest
from decimal import Decimal
from modelos import Cliente, Entidad
from servicios import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import Reserva
from gestor import GestorSoftwareFJ
from excepciones import (DatosInvalidos, RegistroDuplicado,
                         ServicioNoDisponible, OperacionNoPermitida)


class PruebasSoftwareFJ(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorSoftwareFJ()
        self.gestor.registrar_cliente(Cliente("12345", "Laura", "laura@ejemplo.com"))
        self.gestor.registrar_cliente(Cliente("54321", "Mario", "mario@ejemplo.com"))
        self.gestor.registrar_servicio(ReservaSala("S1", "Sala 1", 10000, 4))
        self.gestor.registrar_servicio(AlquilerEquipo("E1", "Tableta", 5000, 3))
        self.gestor.registrar_servicio(AsesoriaEspecializada("A1", "Mentoría", 20000, "POO"))

    def test_01_abstraccion(self):
        with self.assertRaises(TypeError):
            Entidad("X")
        with self.assertRaises(TypeError):
            Servicio("X", "No concreto", 1000)

    def test_02_correo_invalido(self):
        with self.assertRaises(DatosInvalidos):
            Cliente("99999", "X", "correo_erroneo")

    def test_03_duplicado(self):
        with self.assertRaises(RegistroDuplicado):
            self.gestor.registrar_cliente(Cliente("12345", "Duplicado", "d@ejemplo.com"))

    def test_04_tarifa_negativa(self):
        with self.assertRaises(DatosInvalidos):
            ReservaSala("XX", "Sala", -1, 2)

    def test_05_sala_excede_aforo(self):
        with self.assertRaises(DatosInvalidos):
            self.gestor.crear_reserva("R1", "12345", "S1", "2030-01-01 10:00", 2,
                                     {"participantes": 5})
        self.assertEqual(len(self.gestor.reservas), 0)

    def test_06_reserva_confirmacion_y_procesamiento(self):
        r = self.gestor.crear_reserva("R1", "12345", "S1", "2030-01-01 10:00", 2,
                                      {"participantes": 2})
        self.assertEqual(r.estado, Reserva.PENDIENTE)
        self.gestor.confirmar_reserva("R1")
        monto = self.gestor.procesar_reserva("R1", 10, 19)
        self.assertEqual(monto, Decimal("21420.00"))
        self.assertEqual(r.estado, Reserva.PROCESADA)

    def test_07_bloqueo_sala_superpuesta(self):
        self.gestor.crear_reserva("R1", "12345", "S1", "2030-01-01 10:00", 2,
                                  {"participantes": 2})
        with self.assertRaises(ServicioNoDisponible):
            self.gestor.crear_reserva("R2", "54321", "S1", "2030-01-01 11:00", 1,
                                      {"participantes": 2})

    def test_08_franjas_contiguas_permitidas(self):
        self.gestor.crear_reserva("R1", "12345", "S1", "2030-01-01 10:00", 2,
                                  {"participantes": 2})
        self.gestor.crear_reserva("R2", "54321", "S1", "2030-01-01 12:00", 1,
                                  {"participantes": 2})
        self.assertEqual(len(self.gestor.reservas), 2)

    def test_09_stock_concurrente(self):
        self.gestor.crear_reserva("R1", "12345", "E1", "2030-01-01 10:00", 2,
                                  {"unidades": 2})
        with self.assertRaises(ServicioNoDisponible):
            self.gestor.crear_reserva("R2", "54321", "E1", "2030-01-01 10:30", 1,
                                      {"unidades": 2})

    def test_10_cancelacion_libera_recurso(self):
        self.gestor.crear_reserva("R1", "12345", "E1", "2030-01-01 10:00", 2,
                                  {"unidades": 3})
        self.gestor.cancelar_reserva("R1")
        self.gestor.crear_reserva("R2", "54321", "E1", "2030-01-01 10:30", 1,
                                  {"unidades": 3})
        self.assertEqual(len(self.gestor.reservas), 2)

    def test_11_no_procesar_cancelada(self):
        self.gestor.crear_reserva("R1", "12345", "S1", "2030-01-01 10:00", 2,
                                  {"participantes": 2})
        self.gestor.cancelar_reserva("R1")
        with self.assertRaises(OperacionNoPermitida):
            self.gestor.procesar_reserva("R1")

    def test_12_encadenamiento_de_excepcion_fecha(self):
        with self.assertRaises(DatosInvalidos) as respuesta:
            self.gestor.crear_reserva("R1", "12345", "A1", "fecha-invalida", 2,
                                      {"tema": "Herencia", "modalidad": "virtual"})
        self.assertIsNotNone(respuesta.exception.__cause__)

    def test_13_polimorfismo_servicios(self):
        for tipo, codigo, detalles in [
            (ReservaSala, "S1", {"participantes": 2}),
            (AlquilerEquipo, "E1", {"unidades": 2}),
            (AsesoriaEspecializada, "A1", {"tema": "Python", "modalidad": "virtual"}),
        ]:
            servicio = self.gestor.buscar_servicio(codigo)
            self.assertIsInstance(servicio, tipo)
            self.assertGreater(servicio.calcular_costo(2, detalles), 0)
            self.assertTrue(servicio.describir())

    def test_14_parametros_faltantes(self):
        with self.assertRaises(DatosInvalidos):
            self.gestor.crear_reserva("R1", "12345", "A1", "2030-01-01 10:00", 2,
                                      {"modalidad": "virtual"})

    def test_15_error_calculo_sin_cambiar_estado(self):
        reserva = self.gestor.crear_reserva("R1", "12345", "S1", "2030-01-01 10:00", 2,
                                           {"participantes": 2})
        self.gestor.confirmar_reserva("R1")
        with self.assertRaises(DatosInvalidos):
            self.gestor.procesar_reserva("R1", descuento=120)
        self.assertEqual(reserva.estado, Reserva.CONFIRMADA)
        self.assertIsNone(reserva.total)


if __name__ == "__main__":
    unittest.main(verbosity=2)
