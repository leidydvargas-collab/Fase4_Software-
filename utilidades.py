"""Validaciones reutilizables y registro de eventos y excepciones."""

from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path
import logging
from excepciones import DatosInvalidos

CENTAVO = Decimal("0.01")


def texto_obligatorio(valor, campo, longitud_maxima=120):
    """Rechaza valores vacíos, no textuales o demasiado extensos."""
    if not isinstance(valor, str) or not valor.strip():
        raise DatosInvalidos(f"{campo}: debe ser un texto no vacío.")
    texto = valor.strip()
    if len(texto) > longitud_maxima:
        raise DatosInvalidos(f"{campo}: excede {longitud_maxima} caracteres.")
    return texto


def numero_decimal(valor, campo, *, permite_cero=False):
    """Convierte un valor a Decimal y encadena errores de conversión."""
    if isinstance(valor, bool):
        raise DatosInvalidos(f"{campo}: no se aceptan valores booleanos.")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise DatosInvalidos(f"{campo}: debe ser un número válido.") from error
    if not numero.is_finite():
        raise DatosInvalidos(f"{campo}: debe ser finito.")
    if numero < 0 or (numero == 0 and not permite_cero):
        operador = "no negativo" if permite_cero else "mayor que cero"
        raise DatosInvalidos(f"{campo}: debe ser {operador}.")
    return numero


def entero_positivo(valor, campo):
    """Valida enteros positivos sin aceptar booleanos ni fracciones."""
    if isinstance(valor, bool):
        raise DatosInvalidos(f"{campo}: debe ser un entero positivo.")
    try:
        if str(valor).strip() != str(int(valor)):
            raise ValueError("Fracción o representación inválida")
        numero = int(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise DatosInvalidos(f"{campo}: debe ser un entero positivo.") from error
    if numero < 1:
        raise DatosInvalidos(f"{campo}: debe ser al menos 1.")
    return numero


def inicio_reserva(valor):
    """Analiza fecha/hora local en formato 'AAAA-MM-DD HH:MM'."""
    if isinstance(valor, datetime):
        if valor.tzinfo is not None:
            raise DatosInvalidos("Inicio: use fecha y hora local sin zona horaria.")
        return valor
    try:
        return datetime.strptime(valor, "%Y-%m-%d %H:%M")
    except (TypeError, ValueError) as error:
        raise DatosInvalidos("Inicio: formato requerido AAAA-MM-DD HH:MM.") from error


def configurar_logger(ruta=None):
    """Crea un archivo de registros; los datos de negocio siguen en RAM."""
    if ruta is None:
        ruta = Path(__file__).resolve().parent / "logs" / "software_fj.log"
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("software_fj")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    # Evita duplicar registros al importar/reiniciar módulos.
    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            h.close()
    handler = logging.FileHandler(ruta, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger, ruta
