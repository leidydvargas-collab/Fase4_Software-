"""Servicio abstracto + sala, alquiler de equipos y asesoría especializada."""

from abc import abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from modelos import Entidad
from excepciones import DatosInvalidos, ErrorCalculo
from utilidades import numero_decimal, entero_positivo, texto_obligatorio, CENTAVO


class Servicio(Entidad):
    """Clase abstracta con estructura común y cálculo monetario seguro."""

    def __init__(self, codigo, nombre, tarifa_hora, disponible=True):
        super().__init__(codigo)
        self.__nombre = texto_obligatorio(nombre, "Nombre del servicio")
        self.__tarifa_hora = numero_decimal(tarifa_hora, "Tarifa por hora")
        if not isinstance(disponible, bool):
            raise DatosInvalidos("Disponible debe ser verdadero o falso.")
        self.__disponible = disponible

    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa_hora(self):
        return self.__tarifa_hora

    @property
    def disponible(self):
        return self.__disponible

    def cambiar_disponibilidad(self, disponible):
        if not isinstance(disponible, bool):
            raise DatosInvalidos("Disponible debe ser verdadero o falso.")
        self.__disponible = disponible

    @property
    @abstractmethod
    def capacidad_simultanea(self):
        """Máximo de recursos reservables durante una misma franja."""

    @abstractmethod
    def unidades_solicitadas(self, detalles):
        """Cantidad de recursos utilizada por una reserva."""

    @abstractmethod
    def validar_parametros(self, duracion, detalles):
        """Cada subtipo valida sus propias reglas de negocio."""

    @abstractmethod
    def calcular_costo(self, duracion, detalles, descuento=0, impuesto=0):
        """Polimorfismo + formas opcionales de cálculo de costos."""

    @abstractmethod
    def describir(self):
        """Descripción particular de cada servicio."""

    def resumen(self):
        return self.describir()

    def _ajustar_precio(self, base, descuento=0, impuesto=0):
        """Simula sobrecarga: costo(base), costo(base,desc), costo(base,desc,imp)."""
        base = numero_decimal(base, "Costo base", permite_cero=True)
        descuento = numero_decimal(descuento, "Descuento (%)", permite_cero=True)
        impuesto = numero_decimal(impuesto, "Impuesto (%)", permite_cero=True)
        if descuento > 100 or impuesto > 100:
            raise DatosInvalidos("Descuento e impuesto deben estar entre 0 y 100%.")
        try:
            neto = base * (Decimal("1") - descuento / 100)
            total = neto * (Decimal("1") + impuesto / 100)
            return total.quantize(CENTAVO, rounding=ROUND_HALF_UP)
        except Exception as error:
            raise ErrorCalculo("No fue posible calcular el costo final.") from error


class ReservaSala(Servicio):
    """Espacio físico: una reserva simultánea y aforo limitado."""

    def __init__(self, codigo, nombre, tarifa_hora, aforo, disponible=True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        self.aforo = entero_positivo(aforo, "Aforo de sala")

    @property
    def capacidad_simultanea(self):
        return 1

    def unidades_solicitadas(self, detalles):
        return 1

    def validar_parametros(self, duracion, detalles):
        numero_decimal(duracion, "Duración")
        participantes = entero_positivo(detalles.get("participantes"), "Participantes")
        if participantes > self.aforo:
            raise DatosInvalidos(f"Participantes: la sala admite máximo {self.aforo}.")
        return {"participantes": participantes}

    def calcular_costo(self, duracion, detalles, descuento=0, impuesto=0):
        self.validar_parametros(duracion, detalles)
        return self._ajustar_precio(self.tarifa_hora * numero_decimal(duracion, "Duración"),
                                    descuento, impuesto)

    def describir(self):
        return f"Sala {self.codigo} – {self.nombre}, aforo={self.aforo}, $/h={self.tarifa_hora}"


class AlquilerEquipo(Servicio):
    """Equipo alquilable: capacidad concurrente en unidades."""

    def __init__(self, codigo, nombre, tarifa_hora, existencias, disponible=True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        self.existencias = entero_positivo(existencias, "Existencias")

    @property
    def capacidad_simultanea(self):
        return self.existencias

    def unidades_solicitadas(self, detalles):
        return entero_positivo(detalles.get("unidades"), "Unidades")

    def validar_parametros(self, duracion, detalles):
        numero_decimal(duracion, "Duración")
        unidades = self.unidades_solicitadas(detalles)
        if unidades > self.existencias:
            raise DatosInvalidos(f"Unidades: inventario máximo de {self.existencias}.")
        return {"unidades": unidades}

    def calcular_costo(self, duracion, detalles, descuento=0, impuesto=0):
        detalle = self.validar_parametros(duracion, detalles)
        base = self.tarifa_hora * numero_decimal(duracion, "Duración") * detalle["unidades"]
        return self._ajustar_precio(base, descuento, impuesto)

    def describir(self):
        return f"Equipo {self.codigo} – {self.nombre}, existencias={self.existencias}, $/h={self.tarifa_hora}"


class AsesoriaEspecializada(Servicio):
    """Servicio humano: una asesoría por franja; duración máxima de 4 horas."""

    def __init__(self, codigo, nombre, tarifa_hora, especialidad, disponible=True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        self.especialidad = texto_obligatorio(especialidad, "Especialidad")

    @property
    def capacidad_simultanea(self):
        return 1

    def unidades_solicitadas(self, detalles):
        return 1

    def validar_parametros(self, duracion, detalles):
        horas = numero_decimal(duracion, "Duración")
        if horas > 4:
            raise DatosInvalidos("Asesoría: duración máxima de 4 horas por sesión.")
        tema = texto_obligatorio(detalles.get("tema"), "Tema", 120)
        modalidad = texto_obligatorio(detalles.get("modalidad"), "Modalidad").lower()
        if modalidad not in ("virtual", "presencial"):
            raise DatosInvalidos("Modalidad: solo virtual o presencial.")
        return {"tema": tema, "modalidad": modalidad}

    def calcular_costo(self, duracion, detalles, descuento=0, impuesto=0):
        self.validar_parametros(duracion, detalles)
        return self._ajustar_precio(self.tarifa_hora * numero_decimal(duracion, "Duración"),
                                    descuento, impuesto)

    def describir(self):
        return f"Asesoría {self.codigo} – {self.nombre}, especialidad={self.especialidad}, $/h={self.tarifa_hora}"
