"""Simulación automática de 21 operaciones; manejo de excepciones y logs.

Ejecute: python app.py
Solo se conservan datos de negocio en memoria. Los archivos son logs.
"""

from gestor import GestorSoftwareFJ
from modelos import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from excepciones import ErrorSoftwareFJ
from utilidades import configurar_logger


def ejecutar_escenario():
    gestor = GestorSoftwareFJ()
    logger, ruta_log = configurar_logger()
    exitos = 0
    controlados = 0
    numero = 0

    def paso(nombre, accion):
        nonlocal numero, exitos, controlados
        numero += 1
        print(f"\n[{numero:02d}] {nombre}")
        try:
            resultado = accion()
        except ErrorSoftwareFJ as error:
            # try/except: el error esperado se controla y queda registrado.
            controlados += 1
            print(f"  ERROR CONTROLADO: {error.__class__.__name__}: {error}")
            # No se registran nombres, correos ni datos privados en los logs.
            logger.warning("Operación %02d rechazada: %s", numero, error.__class__.__name__)
        except Exception:
            # Protección adicional ante fallos inesperados de programación.
            controlados += 1
            print("  ERROR INESPERADO: consulte el log técnico.")
            logger.exception("Operación %02d: error inesperado", numero)
        else:
            # try/except/else: se ejecuta solo si no hubo excepción.
            exitos += 1
            vista = resultado.resumen() if hasattr(resultado, "resumen") else resultado
            print(f"  OK: {vista}")
            logger.info("Operación %02d completada: %s", numero, nombre)
        finally:
            # try/except/finally: siempre llega aquí, haya error o no.
            print("  Continuidad: la aplicación sigue funcionando.")

    print("=" * 70)
    print("SOFTWARE FJ - FASE 4 | SIMULACIÓN DE EXCEPCIONES Y POO")
    print("=" * 70)

    paso("Registrar cliente correcto", lambda: gestor.registrar_cliente(
        Cliente("100001", "Ana Muñoz", "ana@ejemplo.com")))
    paso("Rechazar correo inválido", lambda: gestor.registrar_cliente(
        Cliente("100002", "Luis", "correo-sin-arroba")))
    paso("Registrar segundo cliente", lambda: gestor.registrar_cliente(
        Cliente("100003", "Carlos Ruiz", "carlos@ejemplo.com")))
    paso("Rechazar identificación duplicada", lambda: gestor.registrar_cliente(
        Cliente("100001", "Otro Cliente", "otro@ejemplo.com")))
    paso("Crear servicio de sala", lambda: gestor.registrar_servicio(
        ReservaSala("SALA-01", "Sala de estudio", 40000, 6)))
    paso("Crear alquiler de equipos", lambda: gestor.registrar_servicio(
        AlquilerEquipo("EQU-01", "Proyector", 15000, 3)))
    paso("Crear asesoría especializada", lambda: gestor.registrar_servicio(
        AsesoriaEspecializada("ASE-01", "Asesoría Python", 85000, "Programación")))
    paso("Rechazar tarifa negativa", lambda: gestor.registrar_servicio(
        ReservaSala("SALA-XX", "Sala inválida", -2000, 5)))
    paso("Crear reserva de sala válida", lambda: gestor.crear_reserva(
        "R-01", "100001", "SALA-01", "2030-05-15 09:00", 2, {"participantes": 4}))
    paso("Confirmar reserva R-01", lambda: gestor.confirmar_reserva("R-01"))
    paso("Procesar con 10% descuento y 19% impuesto", lambda: gestor.procesar_reserva(
        "R-01", 10, 19))
    paso("Rechazar solapamiento de la sala", lambda: gestor.crear_reserva(
        "R-02", "100003", "SALA-01", "2030-05-15 10:00", 1, {"participantes": 2}))
    paso("Rechazar alquiler superior a existencias", lambda: gestor.crear_reserva(
        "R-03", "100003", "EQU-01", "2030-05-15 09:00", 2, {"unidades": 5}))
    paso("Crear alquiler de 2 equipos", lambda: gestor.crear_reserva(
        "R-04", "100003", "EQU-01", "2030-05-15 09:00", 2, {"unidades": 2}))
    paso("Rechazar exceso concurrente de equipos", lambda: gestor.crear_reserva(
        "R-05", "100001", "EQU-01", "2030-05-15 10:00", 2, {"unidades": 2}))
    paso("Cancelar alquiler R-04", lambda: gestor.cancelar_reserva("R-04"))
    paso("Rechazar procesar una reserva cancelada", lambda: gestor.procesar_reserva("R-04"))
    paso("Rechazar fecha mal escrita (excepción encadenada)", lambda: gestor.crear_reserva(
        "R-06", "100001", "ASE-01", "15/05/2030", 1, {"tema": "POO", "modalidad": "virtual"}))
    paso("Crear asesoría válida", lambda: gestor.crear_reserva(
        "R-07", "100001", "ASE-01", "2030-05-15 14:00", 1.5,
        {"tema": "Herencia", "modalidad": "virtual"}))
    paso("Confirmar asesoría R-07", lambda: gestor.confirmar_reserva("R-07"))
    paso("Procesar asesoría sin impuesto ni descuento", lambda: gestor.procesar_reserva("R-07"))

    print("\n" + "=" * 70)
    print(f"RESUMEN: {numero} operaciones, {exitos} exitosas y {controlados} errores controlados.")
    print(f"GESTOR: {gestor.resumen_general()}")
    print(f"LOG: {ruta_log}")
    print("RESULTADO: el programa alcanzó el final sin interrumpirse.")
    return gestor


if __name__ == "__main__":
    ejecutar_escenario()
  
