"""Entidad abstracta y Cliente encapsulado: identificadores, nombre y correo."""

from abc import ABC, abstractmethod
import re
from excepciones import DatosInvalidos
from utilidades import texto_obligatorio


class Entidad(ABC):
    """Define un contrato compartido por las entidades del sistema."""

    def __init__(self, codigo):
        self.__codigo = texto_obligatorio(codigo, "Código", 30)

    @property
    def codigo(self):
        return self.__codigo

    @abstractmethod
    def resumen(self):
        """Cada entidad debe ofrecer una representación pública."""


class Cliente(Entidad):
    """Entidad con datos personales protegidos mediante name mangling."""

    def __init__(self, identificacion, nombre, correo):
        super().__init__(identificacion)
        if not re.fullmatch(r"[0-9]{4,15}", self.codigo):
            raise DatosInvalidos("Identificación: use de 4 a 15 dígitos.")
        self.__nombre = texto_obligatorio(nombre, "Nombre", 90)
        correo = texto_obligatorio(correo, "Correo", 160).lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
            raise DatosInvalidos("Correo: formato incorrecto.")
        self.__correo = correo

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    def resumen(self):
        # Se evita mostrar correo en logs; resumen es para consola autorizada.
        return f"Cliente {self.codigo} – {self.__nombre} ({self.__correo})"
      
