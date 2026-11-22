import logging
from decimal import Decimal
from pathlib import Path

from modelo import (Asesoria, Cliente, DatoInvalido, Equipo, ErrorSistema,
                    ReservaInvalida, Sala, ServicioOcupado, Sistema)


def simular():
    sistema = Sistema()
    clientes, servicios, reservas = sistema.clientes, sistema.servicios, sistema.reservas

    # las acciones se evaluan en orden. los casos posteriores reutilizan el estado real.
    casos = [
        ("alta de cliente", lambda: sistema.registrar_cliente("101", "ana"), "ana"),
        ("nombre vacio", lambda: sistema.registrar_cliente("102", " "), DatoInvalido),
        ("documento duplicado", lambda: sistema.registrar_cliente("101", "luz"), DatoInvalido),
        ("alta de sala", lambda: sistema.agregar_servicio(Sala("norte", 20000, 8)), "sala norte (8 personas)"),
        ("alta de equipos", lambda: sistema.agregar_servicio(Equipo("portatiles", 6000, 2)), "alquiler de portatiles (2 unidades)"),
        ("alta de asesoria", lambda: sistema.agregar_servicio(Asesoria("redes", 30000, 10000)), "asesoria de redes"),
        ("tarifa ilegible", lambda: sistema.agregar_servicio(Sala("sur", "abc", 5)), DatoInvalido),
        ("unidades faltantes", lambda: sistema.agregar_servicio(Equipo("monitor", 9000, None)), DatoInvalido),
        ("duracion cero", lambda: sistema.reservar(clientes[0], servicios[0], 0), DatoInvalido),
        ("cliente sin registrar", lambda: sistema.reservar(Cliente("999", "leo"), servicios[0], 1), ReservaInvalida),
        ("confirmar sala", lambda: sistema.reservar(clientes[0], servicios[0], 2), "sala norte (8 personas) | ana | confirmada"),
        ("sala ocupada", lambda: sistema.reservar(clientes[0], servicios[0], 1), ServicioOcupado),
        ("cancelar reserva", lambda: reservas[0].cancelar(), None),
        ("repetir cancelacion", lambda: reservas[0].cancelar(), ReservaInvalida),
        ("volver a reservar la sala", lambda: sistema.reservar(clientes[0], servicios[0], 2), "sala norte (8 personas) | ana | confirmada"),
        ("descuento fuera de rango", lambda: reservas[1].procesar(descuento=120), DatoInvalido),
        ("procesar sala con descuento e impuesto", lambda: reservas[1].procesar(descuento=10, impuesto=19), Decimal("42840.00")),
        ("reservar equipos", lambda: sistema.reservar(clientes[0], servicios[1], 3), "alquiler de portatiles (2 unidades) | ana | confirmada"),
        ("procesar dos equipos por tres horas", lambda: reservas[2].procesar(), Decimal("36000.00")),
        ("reservar asesoria", lambda: sistema.reservar(clientes[0], servicios[2], 2), "asesoria de redes | ana | confirmada"),
        ("procesar asesoria con preparacion", lambda: reservas[3].procesar(), Decimal("70000.00")),
        ("verificar registros tras los errores", lambda: (len(clientes), len(servicios), [r.estado for r in reservas]),
         (1, 3, ["cancelada", "procesada", "procesada", "procesada"])),
    ]
    aciertos = 0
    for indice, (nombre, accion, esperado) in enumerate(casos, 1):
        logging.info("inicio %02d | %s", indice, nombre)
        try:
            resultado = accion()
        except ErrorSistema as error:
            # el archivo conserva tambien la causa original si se encadeno la excepcion.
            logging.exception("operacion rechazada: %s", nombre)
            correcto = type(error) is esperado
            detalle = str(error)
        except Exception as error:
            logging.exception("fallo inesperado en %s", nombre)
            correcto, detalle = False, str(error)
        else:
            correcto = resultado == esperado
            detalle = "operacion completada" if resultado is None else str(resultado)
        finally:
            logging.info("fin de la operacion %02d", indice)
        estado = "ok" if correcto else "revisar"
        if correcto:
            aciertos += 1
        mensaje = f"{indice:02d} [{estado}] {nombre} | {detalle}"
        logging.log(logging.INFO if correcto else logging.ERROR, mensaje)
        print(mensaje)
    resumen = f"{aciertos}/{len(casos)} simulaciones verificadas."
    logging.info(resumen)
    print(resumen)
    return aciertos == len(casos)


if __name__ == "__main__":
    ruta_log = Path(__file__).with_name("sistema.log")
    logging.basicConfig(filename=ruta_log, level=logging.INFO, encoding="utf-8",
                        format="%(asctime)s | %(levelname)s | %(message)s")
    raise SystemExit(0 if simular() else 1)
