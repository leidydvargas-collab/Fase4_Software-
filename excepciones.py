"""Excepciones del dominio de Software FJ (Fase 4)."""

class ErrorSoftwareFJ(Exception):
    """Error funcional controlado por la aplicación."""

class DatosInvalidos(ErrorSoftwareFJ):
    """Los datos suministrados no cumplen las reglas de negocio."""

class RegistroDuplicado(ErrorSoftwareFJ):
    """Ya existe una entidad con el mismo identificador."""

class RegistroNoEncontrado(ErrorSoftwareFJ):
    """No existe el cliente, servicio o reserva solicitado."""

class ServicioNoDisponible(ErrorSoftwareFJ):
    """El servicio no admite más reservas para la franja solicitada."""

class ReservaInvalida(ErrorSoftwareFJ):
    """Los datos de la reserva no cumplen las restricciones."""

class OperacionNoPermitida(ErrorSoftwareFJ):
    """La transición de estado solicitada está prohibida."""

class ErrorCalculo(ErrorSoftwareFJ):
    """No se puede determinar un costo monetario válido."""
