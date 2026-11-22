"""entidades y reglas de negocio de software fj. los importes se expresan en cop."""
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class ErrorSistema(Exception):
    """base de los errores controlados por la aplicacion."""


class DatoInvalido(ErrorSistema):
    """un dato obligatorio falta o esta fuera de rango."""


class ServicioOcupado(ErrorSistema):
    """otra reserva mantiene ocupado el recurso."""


class ReservaInvalida(ErrorSistema):
    """la operacion solicitada es incompatible con la reserva."""


def texto(valor, campo):
    """valida un texto obligatorio y devuelve su version sin espacios externos."""
    if not isinstance(valor, str) or not valor.strip():
        raise DatoInvalido(f"el campo {campo} es obligatorio.")
    return valor.strip()


def numero(valor, campo, minimo, maximo=None):
    """convierte texto o numeros y conserva la causa de errores de conversion."""
    try:
        resultado = Decimal(str(valor))
    except InvalidOperation as causa:
        raise DatoInvalido(f"{campo} debe ser numerico.") from causa
    if not resultado.is_finite() or resultado < minimo:
        raise DatoInvalido(f"{campo} debe ser finito y al menos {minimo}.")
    if maximo is not None and resultado > maximo:
        raise DatoInvalido(f"{campo} supera el maximo de {maximo}.")
    return resultado


def entero(valor, campo):
    """valida que un valor sea un numero entero positivo y lo convierte a int."""
    valor = numero(valor, campo, 1, 10000)
    if valor != valor.to_integral_value():
        raise DatoInvalido(f"{campo} debe ser entero.")
    return int(valor)


class Entidad(ABC):
    @abstractmethod
    def describir(self):
        """devuelve una descripcion breve de la entidad."""


class Cliente(Entidad):
    def __init__(self, documento, nombre):
        """crea un cliente y valida su documento y nombre."""
        self.__documento = texto(documento, "documento")
        if not self.__documento.isdecimal():
            raise DatoInvalido("el documento debe contener solo digitos.")
        self.__nombre = texto(nombre, "nombre")

    @property
    def documento(self):
        """devuelve el documento del cliente."""
        return self.__documento

    def describir(self):
        """devuelve el nombre del cliente."""
        return self.__nombre


class Servicio(Entidad):
    def __init__(self, nombre, tarifa):
        """crea un servicio y valida su nombre y tarifa."""
        self.nombre = texto(nombre, "nombre del servicio")
        self.tarifa = numero(tarifa, "tarifa", Decimal("0.01"), 100000000)
        self._titular = None

    def ocupar(self, reserva):
        """asigna el servicio a una reserva si esta disponible."""
        if self._titular is not None:
            raise ServicioOcupado(f"{self.nombre} ya esta reservado.")
        self._titular = reserva

    def liberar(self, reserva):
        """libera el servicio si la reserva indicada es quien lo ocupa."""
        if self._titular is not reserva:
            raise ReservaInvalida("la reserva no ocupa este servicio.")
        self._titular = None

    @abstractmethod
    def subtotal(self, horas):
        """calcula el valor propio de cada tipo de servicio."""

    def calcular_costo(self, horas, *, descuento=0, impuesto=0):
        """calcula el costo con descuento e impuesto opcionales."""
        horas = numero(horas, "horas", Decimal("0.01"), 10000)
        rebaja = numero(descuento, "descuento", 0, 100) / 100
        tributo = numero(impuesto, "impuesto", 0, 100) / 100
        total = self.subtotal(horas) * (1 - rebaja) * (1 + tributo)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Sala(Servicio):
    def __init__(self, nombre, tarifa, capacidad):
        """crea una sala con una capacidad validada."""
        super().__init__(nombre, tarifa)
        self.capacidad = entero(capacidad, "capacidad")

    def subtotal(self, horas):
        """calcula el costo de la sala segun la tarifa y las horas."""
        return self.tarifa * horas

    def describir(self):
        """devuelve el nombre de la sala y su capacidad."""
        return f"sala {self.nombre} ({self.capacidad} personas)"


class Equipo(Servicio):
    def __init__(self, nombre, tarifa, unidades):
        """crea un equipo con una cantidad de unidades validada."""
        super().__init__(nombre, tarifa)
        self.unidades = entero(unidades, "unidades")

    def subtotal(self, horas):
        """calcula el costo segun la tarifa, las horas y las unidades."""
        return self.tarifa * horas * self.unidades

    def describir(self):
        """devuelve el nombre del equipo y la cantidad disponible."""
        return f"alquiler de {self.nombre} ({self.unidades} unidades)"


class Asesoria(Servicio):
    def __init__(self, nombre, tarifa, preparacion):
        """crea una asesoria y valida su cargo de preparacion."""
        super().__init__(nombre, tarifa)
        self.preparacion = numero(preparacion, "cargo de preparacion", 0, 100000000)

    def subtotal(self, horas):
        """calcula el costo por horas y suma el cargo de preparacion."""
        return self.tarifa * horas + self.preparacion

    def describir(self):
        """devuelve el nombre de la asesoria."""
        return f"asesoria de {self.nombre}"


class Reserva(Entidad):
    def __init__(self, cliente, servicio, horas):
        """crea una reserva pendiente para un cliente y servicio validos."""
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaInvalida("se requiere un cliente y un servicio validos.")
        self.cliente = cliente
        self.servicio = servicio
        self.horas = numero(horas, "horas", Decimal("0.01"), 10000)
        self.estado = "pendiente"

    def confirmar(self):
        """confirma la reserva y ocupa el servicio."""
        if self.estado != "pendiente":
            raise ReservaInvalida("solo se confirman reservas pendientes.")
        self.servicio.ocupar(self)
        self.estado = "confirmada"

    def cancelar(self):
        """cancela la reserva y libera el servicio si estaba confirmada."""
        if self.estado not in ("pendiente", "confirmada"):
            raise ReservaInvalida(f"no se puede cancelar una reserva {self.estado}.")
        if self.estado == "confirmada":
            self.servicio.liberar(self)
        self.estado = "cancelada"

    def procesar(self, **ajustes):
        """calcula el costo, libera el servicio y marca la reserva procesada."""
        if self.estado != "confirmada":
            raise ReservaInvalida("para procesar, la reserva debe estar confirmada.")
        total = self.servicio.calcular_costo(self.horas, **ajustes)
        self.servicio.liberar(self)
        self.estado = "procesada"
        return total

    def describir(self):
        """devuelve el servicio, el cliente y el estado de la reserva."""
        return f"{self.servicio.describir()} | {self.cliente.describir()} | {self.estado}"


class Sistema:
    """catalogo en memoria. solo incorpora objetos despues de validarlos."""
    def __init__(self):
        """inicializa las listas de clientes, servicios y reservas."""
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, documento, nombre):
        """valida y registra un cliente si el documento no esta repetido."""
        cliente = Cliente(documento, nombre)
        if any(c.documento == cliente.documento for c in self.clientes):
            raise DatoInvalido("el documento ya esta registrado.")
        self.clientes.append(cliente)
        return cliente.describir()

    def agregar_servicio(self, servicio):
        """valida y agrega un servicio al catalogo."""
        if not isinstance(servicio, Servicio):
            raise DatoInvalido("servicio invalido.")
        self.servicios.append(servicio)
        return servicio.describir()

    def reservar(self, cliente, servicio, horas):
        """crea y confirma una reserva para objetos previamente registrados."""
        if cliente not in self.clientes or servicio not in self.servicios:
            raise ReservaInvalida("el cliente y el servicio deben estar registrados.")
        reserva = Reserva(cliente, servicio, horas)
        reserva.confirmar()
        self.reservas.append(reserva)
        return reserva.describir()
