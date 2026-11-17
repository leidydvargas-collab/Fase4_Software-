"""Gestión de entidades en listas de memoria y control de disponibilidad."""

from modelos import Cliente
from servicios import Servicio
from reservas import Reserva
from excepciones import (DatosInvalidos, RegistroDuplicado,
                         RegistroNoEncontrado, ServicioNoDisponible)
from utilidades import texto_obligatorio


class GestorSoftwareFJ:
    """Mantiene toda la información de negocio en memoria, SIN BD."""

    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []

    @property
    def clientes(self):
        return tuple(self.__clientes)

    @property
    def servicios(self):
        return tuple(self.__servicios)

    @property
    def reservas(self):
        return tuple(self.__reservas)

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidos("Registrar cliente: se requiere un objeto Cliente.")
        if any(c.codigo == cliente.codigo for c in self.__clientes):
            raise RegistroDuplicado(f"Ya existe un cliente {cliente.codigo}.")
        self.__clientes.append(cliente)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidos("Registrar servicio: objeto de tipo Servicio requerido.")
        if any(s.codigo == servicio.codigo for s in self.__servicios):
            raise RegistroDuplicado(f"Ya existe un servicio {servicio.codigo}.")
        self.__servicios.append(servicio)
        return servicio

    def buscar_cliente(self, codigo):
        codigo = texto_obligatorio(codigo, "Identificación")
        for cliente in self.__clientes:
            if cliente.codigo == codigo:
                return cliente
        raise RegistroNoEncontrado(f"Cliente {codigo} no encontrado.")

    def buscar_servicio(self, codigo):
        codigo = texto_obligatorio(codigo, "Código del servicio")
        for servicio in self.__servicios:
            if servicio.codigo == codigo:
                return servicio
        raise RegistroNoEncontrado(f"Servicio {codigo} no encontrado.")

    def buscar_reserva(self, codigo):
        codigo = texto_obligatorio(codigo, "Código de reserva")
        for reserva in self.__reservas:
            if reserva.codigo == codigo:
                return reserva
        raise RegistroNoEncontrado(f"Reserva {codigo} no encontrada.")

    def crear_reserva(self, codigo, id_cliente, id_servicio, inicio, duracion, detalles):
        if any(r.codigo == codigo for r in self.__reservas):
            raise RegistroDuplicado(f"Ya existe una reserva {codigo}.")
        cliente = self.buscar_cliente(id_cliente)
        servicio = self.buscar_servicio(id_servicio)
        if not servicio.disponible:
            raise ServicioNoDisponible(f"Servicio {servicio.codigo} está inhabilitado.")
        if not isinstance(detalles, dict):
            raise DatosInvalidos("Detalles debe ser un diccionario.")
        # Se construye provisionalmente; errores de validación NO modifican listas.
        nueva = Reserva(codigo, cliente, servicio, inicio, duracion, detalles)
        usadas = 0
        for anterior in self.__reservas:
            if anterior.servicio.codigo != servicio.codigo or anterior.estado == Reserva.CANCELADA:
                continue
            # Las franjas [inicio,fin) se solapan solo si se cruzan realmente.
            if nueva.inicio < anterior.fin and anterior.inicio < nueva.fin:
                usadas += servicio.unidades_solicitadas(anterior.detalles)
        solicitadas = servicio.unidades_solicitadas(nueva.detalles)
        if usadas + solicitadas > servicio.capacidad_simultanea:
            raise ServicioNoDisponible("Sin disponibilidad para el horario y unidades solicitados.")
        self.__reservas.append(nueva)
        return nueva

    def confirmar_reserva(self, codigo):
        reserva = self.buscar_reserva(codigo)
        reserva.confirmar()
        return reserva

    def cancelar_reserva(self, codigo):
        reserva = self.buscar_reserva(codigo)
        reserva.cancelar()
        return reserva

    def procesar_reserva(self, codigo, descuento=0, impuesto=0):
        reserva = self.buscar_reserva(codigo)
        return reserva.procesar(descuento, impuesto)

    def resumen_general(self):
        return f"{len(self.__clientes)} clientes; {len(self.__servicios)} servicios; {len(self.__reservas)} reservas"
