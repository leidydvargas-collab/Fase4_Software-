"""Reserva, máquina de estados y validación de transiciones."""

from datetime import timedelta
from modelos import Entidad, Cliente
from servicios import Servicio
from utilidades import numero_decimal, inicio_reserva
from excepciones import DatosInvalidos, OperacionNoPermitida


class Reserva(Entidad):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    PROCESADA = "PROCESADA"
    CANCELADA = "CANCELADA"

    def __init__(self, codigo, cliente, servicio, inicio, duracion, detalles):
        super().__init__(codigo)
        if not isinstance(cliente, Cliente):
            raise DatosInvalidos("Reserva: se requiere un Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("Reserva: se requiere un Servicio válido.")
        self.__cliente = cliente
        self.__servicio = servicio
        self.__inicio = inicio_reserva(inicio)
        self.__duracion = numero_decimal(duracion, "Duración (horas)")
        self.__detalles = dict(servicio.validar_parametros(self.__duracion, detalles))
        self.__estado = self.PENDIENTE
        self.__total = None

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def inicio(self):
        return self.__inicio

    @property
    def fin(self):
        return self.inicio + timedelta(hours=float(self.__duracion))

    @property
    def duracion(self):
        return self.__duracion

    @property
    def detalles(self):
        return self.__detalles.copy()

    @property
    def estado(self):
        return self.__estado

    @property
    def total(self):
        return self.__total

    def confirmar(self):
        if self.__estado != self.PENDIENTE:
            raise OperacionNoPermitida("Solo se puede confirmar una reserva PENDIENTE.")
        self.__estado = self.CONFIRMADA

    def cancelar(self):
        if self.__estado not in (self.PENDIENTE, self.CONFIRMADA):
            raise OperacionNoPermitida("Solo se puede cancelar una reserva pendiente o confirmada.")
        self.__estado = self.CANCELADA

    def procesar(self, descuento=0, impuesto=0):
        if self.__estado != self.CONFIRMADA:
            raise OperacionNoPermitida("Solo se puede procesar una reserva CONFIRMADA.")
        # Importante: el estado cambia SOLO DESPUÉS de calcular con éxito.
        total = self.__servicio.calcular_costo(self.__duracion, self.__detalles,
                                                descuento, impuesto)
        self.__total = total
        self.__estado = self.PROCESADA
        return total

    def resumen(self):
        monto = "sin calcular" if self.__total is None else f"${self.__total}"
        return (f"Reserva {self.codigo}: cliente={self.cliente.codigo}, "
                f"servicio={self.servicio.codigo}, {self.inicio:%Y-%m-%d %H:%M}, "
                f"{self.__duracion} h, estado={self.__estado}, costo={monto}")
      
