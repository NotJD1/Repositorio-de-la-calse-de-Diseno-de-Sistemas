"""

from datetime import date, time, timedelta, datetime
import copy
import threading

#Singleton
class ValoresImportantes:
    _valores = None

    def __init__(self):
        
        ValoresImportantes._valores = self
        self.limite_prioridad = time(18, 0)
        self.noshow_estudiantes = 120
        self.noshow_capitanes = 1440
        self.noshow_administradores = None
        self.vetos_maximos = 3
        self.dias_penalizacion = 7
        self.canchas_disponibles = []

    @staticmethod
    def get_valores():
        if ValoresImportantes._valores is None:
            ValoresImportantes()

        return ValoresImportantes._valores

#Strategy
class EstrategiaPrioridad:
    def prioridad(self, hora_inicio):
        raise NotImplementedError

class ConPrioridad(EstrategiaPrioridad):
    def prioridad(self, hora_inicio):

        if hora_inicio <= ValoresImportantes.get_valores().limite_prioridad:
            return True
        return False


class SinPrioridad(EstrategiaPrioridad):
    def prioridad(self, hora_inicio):
  
            return False

class EstrategiaNoshow:

    def noshow(self, reserva, momento_cancelacion):
        raise NotImplementedError

class NoShowRegular(EstrategiaNoshow):

    def noshow(self, reserva, momento_cancelacion):

        inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
        ventana = timedelta(minutes=ValoresImportantes.get_valores().noshow_estudiantes)
        return inicio - momento_cancelacion < ventana


class NoShowCapitan(EstrategiaNoshow):

    def noshow(self, reserva, momento_cancelacion):
        inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
        ventana = timedelta(minutes=ValoresImportantes.get_valores().noshow_capitanes)
        return inicio - momento_cancelacion < ventana

class AnulacionAdministrador(EstrategiaNoshow):

    def noshow(self, hora_inicio, reserva, dia_actual):
        return False

#clases
class Usuario:

    def __init__(self, nombre, contrasena, ID):
        self.nombre = nombre
        self.contrasena = contrasena
        self.ID = ID
        self.fechas_no_show = []
        self.suspension = None

    def contar_vetos_mensuales(self, fecha):
        contador = 0
        for fecha_no_show in self.fechas_no_show:
            if fecha_no_show.month == fecha.month and fecha_no_show.year == fecha.year:
                contador += 1
        return contador

    def penalizacion(self):
        if self.suspension is not None:
            print(f"El usuario {self.nombre} está suspendido hasta {self.suspension}.")
        else:
            print(f"El usuario {self.nombre} no tiene penalización activa.")

    def registrar_veto(self, momento_cancelacion):

        self.fechas_no_show.append(momento_cancelacion)

        if self.contar_vetos_mensuales(momento_cancelacion) >= ValoresImportantes.get_valores().vetos_maximos:
            self.suspension = momento_cancelacion + timedelta(days=ValoresImportantes.get_valores().dias_penalizacion)
            self.penalizacion()

    def esta_suspendido(self, momento):
        if self.suspension is None:
            return False
        return momento < self.suspension

    def cancelar_reserva(self, reserva, notificador, momento):

        if reserva.titular is not self:
            print(f"{self.nombre} no puede cancelar una reserva que no es suya.")
            return None

        if reserva.estado != "Activa":
            print(f"La reserva no se puede cancelar: ya está en estado {reserva.estado}.")
            return reserva.estado

        estado = reserva.cancelar_reserva(momento)
        notificador.enviar_notificacion(self, f"Tu reserva quedó en estado: {estado}.")
        return estado

class Estudiante(Usuario):

    def __init__ (self, nombre, contrasena, ID, codigo_estudiante, mail):
        
        super().__init__(nombre, contrasena, ID)
        
        self.codigo_estudiante = codigo_estudiante
        self.mail = mail


class Capitan(Usuario):

    def __init__(self, nombre, contrasena, ID, deporte, fecha_inicial, fecha_final):
        
        super().__init__(nombre, contrasena, ID)
        
        self.deporte = deporte
        self.fecha_inicial = fecha_inicial
        self.fecha_final = fecha_final


class Administrador(Usuario):

    def __init__(self, nombre, contrasena, ID, mail):
        
        super().__init__(nombre, contrasena, ID)
        
        self.mail = mail
        self.cancelacion = AnulacionAdministrador()


    def anular_reserva(self, reserva, notificador, momento):

        if reserva.estado != "Activa":
            print(f"La reserva no se puede anular: ya está en estado {reserva.estado}.")
            return reserva.estado

        estado = reserva.cancelar_reserva(momento, self.cancelacion)
        print(f"El administrador {self.nombre} anuló la reserva de {reserva.titular.nombre}. No se aplica penalidad.")
        notificador.enviar_notificacion(reserva.titular, "Tu reserva fue anulada por el administrador.")
        return estado

    def cancelar_reserva(self, reserva, notificador, momento):
        return self.anular_reserva(reserva, notificador, momento)

    def aplicar_bloqueo(self, plantilla, cancha, fecha, momento):

        bloqueo = plantilla.clonar(cancha, fecha)

        for reserva in cancha.lista_reservas:
            if (reserva.estado == "Activa"
                    and reserva.fecha == fecha
                    and reserva.hora_inicio < bloqueo.hora_fin
                    and reserva.hora_fin > bloqueo.hora_inicio):
                self.anular_reserva(reserva, cancha.notificador, momento)

        cancha.agregar_bloqueo(bloqueo)
        print(f"Bloqueo '{bloqueo.motivo}' aplicado en {cancha.lugar} el {fecha}.")
        return bloqueo

#cancha
class Cancha:

    def __init__(self, estado, deporte, lugar, sede):
        self.deporte = deporte
        self.estado = estado
        self.lugar = lugar
        self.validador = sede.crear_validador()
        self.lista_reservas = []
        self.lista_bloqueos = []
        self.notificador = sede.crear_notificador()

    def verificar_disponibilidad (self, reserva):

        if self.hay_bloqueo(reserva):
            print("El horario no es disponible: la cancha está bloqueada")
            return False

        for reserva_existente in self.lista_reservas:
            
            if reserva_existente.estado == "Activa" and reserva.hora_inicio < reserva_existente.hora_fin and reserva.hora_fin > reserva_existente.hora_inicio and reserva.fecha == reserva_existente.fecha:
                    
                print( "El horario no es disponible")
                return False

        print("El horario es disponible")
        return True

    def agregar_reserva(self, reserva):

        if self.hay_bloqueo(reserva):
            print("No se pudo agregar la reserva: la franja está bloqueada por un evento.")
            return False

        if self.verificar_disponibilidad(reserva):
            self.lista_reservas.append(reserva)
            print("Reserva agregada exitosamente.")
            return True

        if reserva.prioridad.prioridad(reserva.hora_inicio):
            print("El usuario tiene prioridad para reservar.")

            for reserva_existente in self.lista_reservas:

                if (reserva_existente.estado == "Activa" and reserva_existente.fecha == reserva.fecha and reserva_existente.hora_inicio == reserva.hora_inicio and not reserva_existente.prioridad.prioridad(reserva_existente.hora_inicio)):

                    reserva_existente.estado = "Cancelada"
                    print(f"La reserva de {reserva_existente.titular.nombre} fue desplazada por prioridad. No se aplica penalidad.")
                    self.notificador.enviar_notificacion(reserva_existente.titular,"Tu reserva fue cancelada porque un equipo oficial tiene prioridad en esa franja.")

                    self.lista_reservas.append(reserva)
                    print("Reserva agregada exitosamente.")
                    return True

            print("No se encontró una reserva que se pueda desplazar.")
            return False

        print("No se pudo agregar la reserva debido a un conflicto de horario.")
        return False

    def mostrar_reservas(self):

        if len(self.lista_reservas) == 0:
            print("No hay reservas para esta cancha.")
            return

        i= 0
        print("-----------------Reservas de la cancha------------------")
        for reserva_nueva in self.lista_reservas:
            
            print( f"{i + 1}. Titular: {reserva_nueva.titular.nombre}, Hora de inicio: {reserva_nueva.hora_inicio}, Hora de fin: {reserva_nueva.hora_fin}, Estado: {reserva_nueva.estado}")
            i+=1

    def agregar_bloqueo(self, bloqueo):
            self.lista_bloqueos.append(bloqueo)

    def hay_bloqueo(self, reserva):

        for bloqueo in self.lista_bloqueos:

            if (bloqueo.fecha == reserva.fecha
                    and reserva.hora_inicio < bloqueo.hora_fin
                    and reserva.hora_fin > bloqueo.hora_inicio):
                return True

        return False



#reserva
class Reserva:

    def __init__(self, titular, hora_inicio, cancha, fecha, prioridad, politica_cancelacion):

        self.titular = titular
        self.hora_inicio = hora_inicio
        minutos = self.hora_inicio.hour * 60 + self.hora_inicio.minute + 60
        self.hora_fin = time((minutos // 60) % 24, minutos % 60)
        self.fecha = fecha
        self.cancha = cancha
        self.prioridad = prioridad
        self.politica_cancelacion = politica_cancelacion
        self.estado = "Activa"

    def cancelar_reserva(self, momento):

        if self.estado != "Activa":
            print(f"La reserva no se puede cancelar: ya está en estado {self.estado}.")
            return self.estado

        if self.politica_cancelacion.noshow(self, momento):
            self.estado = "No Show"
            print(f"Reserva de {self.titular.nombre} cancelada tarde: se registra como No Show.")
            self.titular.registrar_veto(momento)
        else:
            self.estado = "Cancelada"
            print(f"Reserva de {self.titular.nombre} cancelada a tiempo, sin penalidad.")

        return self.estado
    
class ReservaRecurrente:

    def __init__(self, solicitante, cancha, fecha_inicio, hora_inicio, semanas, equipo_prestado, notas, reservas):
        self.solicitante = solicitante
        self.cancha = cancha
        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_inicio
        self.semanas = semanas
        self.equipo_prestado = equipo_prestado
        self.notas = notas
        self.reservas = reservas


class ReservaRecurrenteBuilder:

    MIN_SEMANAS = 2
    MAX_SEMANAS = 8

    def __init__(self, solicitante, cancha, fecha_inicio, hora_inicio):
        self.solicitante = solicitante
        self.cancha = cancha
        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_inicio
        self.semanas = self.MIN_SEMANAS
        self.equipo_prestado = None
        self.notas = None

    def add_semanas(self, semanas):
        if not (self.MIN_SEMANAS <= semanas <= self.MAX_SEMANAS):
            raise ValueError(f"Las semanas deben estar entre {self.MIN_SEMANAS} y {self.MAX_SEMANAS}.")
        self.semanas = semanas
        return self

    def add_equipo_prestado(self, equipo):
        self.equipo_prestado = list(equipo)
        return self

    def add_notas(self, notas):
        self.notas = notas
        return self

    def construir(self):
        if not isinstance(self.solicitante, Capitan):
            raise ValueError("Solo un capitán puede hacer una reserva recurrente.")

        reservas = []
        for n in range(self.semanas):
            fecha = self.fecha_inicio + timedelta(weeks=n)
            reservas.append(
                ReservasFactory().crear_reserva(self.solicitante, self.hora_inicio, self.cancha, fecha)
            )

        return ReservaRecurrente(self.solicitante, self.cancha, self.fecha_inicio, self.hora_inicio, self.semanas, self.equipo_prestado, self.notas, reservas)

class ReservaRegular(Reserva):

    def __init__(self, titular, hora_inicio, cancha, fecha):
        super().__init__(titular, hora_inicio, cancha, fecha, SinPrioridad(), NoShowRegular())


class ReservaEquipo(Reserva):

    def __init__(self, titular, hora_inicio, cancha, fecha):
        super().__init__(titular, hora_inicio, cancha, fecha, ConPrioridad(), NoShowCapitan())
        
#Factory
class ReservasFactory:

    def crear_reserva(self, usuario, hora_inicio, cancha, fecha):

        if isinstance(usuario, Estudiante):
            return ReservaRegular(usuario, hora_inicio, cancha, fecha)

        if isinstance(usuario, Capitan):
            return ReservaEquipo(usuario, hora_inicio, cancha, fecha)

        raise ValueError("Tipo de usuario no válido para crear una reserva")

#Abstract Factory
class ValidadorHorario:

    def horario_valido(self, reserva):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")


class Notificador:

    def enviar_notificacion(self, destinatario, mensaje):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")


class ValidadorHorarioNorte(ValidadorHorario):

    APERTURA = time(6, 0)
    CIERRE = time(22, 0)

    def horario_valido(self, reserva):
        return (self.APERTURA <= reserva.hora_inicio < reserva.hora_fin <= self.CIERRE)


class ValidadorHorarioSur(ValidadorHorario):

    APERTURA = time(7, 0)
    CIERRE = time(23, 0)

    def horario_valido(self, reserva):
        return (self.APERTURA <= reserva.hora_inicio < reserva.hora_fin <= self.CIERRE)


class NotificadorNorte(Notificador):

    def enviar_notificacion(self, destinatario, mensaje):
        print(f"[Correo institucional] Para {destinatario.nombre}: {mensaje}")


class NotificadorSur(Notificador):

    def enviar_notificacion(self, destinatario, mensaje):
        print(f"[Mensaje de texto] Para {destinatario.nombre}: {mensaje}")


class SedeFactory:

    def crear_validador(self):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")

    def crear_notificador(self):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")


class SedeNorteFactory(SedeFactory):

    def crear_validador(self):
        return ValidadorHorarioNorte()

    def crear_notificador(self):
        return NotificadorNorte()


class SedeSurFactory(SedeFactory):

    def crear_validador(self):
        return ValidadorHorarioSur()

    def crear_notificador(self):
        return NotificadorSur()

#Protorype
class Bloqueo:

    def __init__(self, motivo, hora_inicio, hora_fin, equipo):
        self.motivo = motivo
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.equipo = list(equipo)
        self.cancha = None
        self.fecha = None

    def clonar(self, cancha, fecha):
        clon = copy.deepcopy(self)
        clon.cancha = cancha
        clon.fecha = fecha
        return clon

#facade
class ReservaFacade:
    def __init__(self):
        self.fabrica_reservas = ReservasFactory()
        self.candado = threading.Lock()


    def reservar_cancha(self, usuario, cancha, hora_inicio, fecha, momento):

        if usuario.esta_suspendido(momento):
            print(f"Reserva rechazada: {usuario.nombre} está suspendido hasta {usuario.suspension}.")
            return None

        reserva = self.fabrica_reservas.crear_reserva(usuario, hora_inicio, cancha, fecha)

        if not cancha.validador.horario_valido(reserva):
            print(f"Reserva rechazada: {hora_inicio} está fuera del horario permitido de la sede de {cancha.lugar}.")
            return None

        with self.candado:
            confirmada = cancha.agregar_reserva(reserva)

        if not confirmada:
            print(f"Reserva rechazada: la cancha {cancha.lugar} no está disponible.")
            return None

        cancha.notificador.enviar_notificacion(usuario, "Tu reserva fue confirmada.")
        return reserva

    def reservar_recurrente(self, recurrente, momento):

        solicitante = recurrente.solicitante
        cancha = recurrente.cancha

        if solicitante.esta_suspendido(momento):
            print(f"Reserva recurrente rechazada: {solicitante.nombre} está suspendido hasta {solicitante.suspension}.")
            return None

        for reserva in recurrente.reservas:
            if not cancha.validador.horario_valido(reserva):
                print(f"Reserva recurrente rechazada: {reserva.hora_inicio} está fuera del horario permitido de la sede de {cancha.lugar}.")
                return None

        with self.candado:

            for numero, reserva in enumerate(recurrente.reservas, start=1):
                print(f"Verificando semana {numero} ({reserva.fecha}):")
                if not cancha.verificar_disponibilidad(reserva):
                    print(f"Reserva recurrente rechazada: conflicto en la semana {numero} ({reserva.fecha}). No se registró ninguna semana.")
                    return None

            for reserva in recurrente.reservas:
                cancha.agregar_reserva(reserva)

        cancha.notificador.enviar_notificacion(
            solicitante,
            f"Tu reserva recurrente de {recurrente.semanas} semanas fue confirmada."
        )
        return recurrente

    def cancelar_reserva(self, solicitante, reserva, momento):

        with self.candado:
            return solicitante.cancelar_reserva(reserva, reserva.cancha.notificador, momento)

    def bloquear_cancha(self, administrador, plantilla, canchas, fechas, momento):

        with self.candado:
            for cancha in canchas:
                for fecha in fechas:
                    administrador.aplicar_bloqueo(plantilla, cancha, fecha, momento)

"""

from datetime import date, time, timedelta, datetime
import copy
import threading
 
 

# Singleton
class ValoresImportantes:
    _valores = None
 
    def __init__(self):
        ValoresImportantes._valores = self
        self.limite_prioridad = time(18, 0)
        self.noshow_estudiantes = 120      # minutos
        self.noshow_capitanes = 1440       # minutos
        self.vetos_maximos = 3
        self.dias_penalizacion = 7
 
    @staticmethod
    def get_valores():
        if ValoresImportantes._valores is None:
            ValoresImportantes()
        return ValoresImportantes._valores
 
 

# Strategy: prioridad
class EstrategiaPrioridad:
 
    def prioridad(self, hora_inicio):
        raise NotImplementedError
 
 
class ConPrioridad(EstrategiaPrioridad):
 
    def prioridad(self, hora_inicio):
        return hora_inicio <= ValoresImportantes.get_valores().limite_prioridad
 
 
class SinPrioridad(EstrategiaPrioridad):
 
    def prioridad(self, hora_inicio):
        return False
 
 
# Strategy
class EstrategiaNoshow:
 
    def noshow(self, reserva, momento_cancelacion):
        raise NotImplementedError
 
 
class NoShowRegular(EstrategiaNoshow):
 
    def noshow(self, reserva, momento_cancelacion):
        inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
        ventana = timedelta(minutes=ValoresImportantes.get_valores().noshow_estudiantes)
        return inicio - momento_cancelacion < ventana
 
 
class NoShowCapitan(EstrategiaNoshow):
 
    def noshow(self, reserva, momento_cancelacion):
        inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
        ventana = timedelta(minutes=ValoresImportantes.get_valores().noshow_capitanes)
        return inicio - momento_cancelacion < ventana
 
 
class AnulacionAdministrador(EstrategiaNoshow):
 
    def noshow(self, reserva, momento_cancelacion):
        return False
 
 

# Usuarios
class Usuario:
 
    def __init__(self, nombre, contrasena, ID):
        self.nombre = nombre
        self.contrasena = contrasena
        self.ID = ID
        self.fechas_no_show = []
        self.suspension = None
 
    def contar_vetos_mensuales(self, fecha):
        contador = 0
        for fecha_no_show in self.fechas_no_show:
            if fecha_no_show.month == fecha.month and fecha_no_show.year == fecha.year:
                contador += 1
        return contador
 
    def penalizacion(self):
        if self.suspension is not None:
            print(f"El usuario {self.nombre} está suspendido hasta {self.suspension}.")
        else:
            print(f"El usuario {self.nombre} no tiene penalización activa.")
 
    def registrar_veto(self, momento_cancelacion):
        valores = ValoresImportantes.get_valores()
        self.fechas_no_show.append(momento_cancelacion)
 
        if self.contar_vetos_mensuales(momento_cancelacion) >= valores.vetos_maximos:
            self.suspension = momento_cancelacion + timedelta(days=valores.dias_penalizacion)
            self.penalizacion()
 
    def esta_suspendido(self, momento):
        if self.suspension is None:
            return False
        return momento < self.suspension
 
    def cancelar_reserva(self, reserva, momento):
        """Devuelve el estado final, o None si no se pudo cancelar."""
 
        if reserva.titular is not self:
            print(f"{self.nombre} no puede cancelar una reserva que no es suya.")
            return None
 
        if reserva.estado != "Activa":
            print(f"La reserva no se puede cancelar: ya está en estado {reserva.estado}.")
            return None
 
        return reserva.cancelar_reserva(momento)
 
 
class Estudiante(Usuario):
 
    def __init__(self, nombre, contrasena, ID, codigo_estudiante, mail):
        super().__init__(nombre, contrasena, ID)
        self.codigo_estudiante = codigo_estudiante
        self.mail = mail
 
 
class Capitan(Usuario):
 
    def __init__(self, nombre, contrasena, ID, deporte, fecha_inicial, fecha_final):
        super().__init__(nombre, contrasena, ID)
        self.deporte = deporte
        self.fecha_inicial = fecha_inicial
        self.fecha_final = fecha_final
 
 
class Administrador(Usuario):
 
    def __init__(self, nombre, contrasena, ID, mail):
        super().__init__(nombre, contrasena, ID)
        self.mail = mail
        self.cancelacion = AnulacionAdministrador()
 
    def anular_reserva(self, reserva, momento):
        """Devuelve el estado final, o None si la reserva ya no estaba activa."""
 
        if reserva.estado != "Activa":
            print(f"La reserva no se puede anular: ya está en estado {reserva.estado}.")
            return None
 
        estado = reserva.cancelar_reserva(momento, self.cancelacion)
        print(f"El administrador {self.nombre} anuló la reserva de {reserva.titular.nombre}. No se aplica penalidad.")
        return estado
 
    def cancelar_reserva(self, reserva, momento):
        return self.anular_reserva(reserva, momento)
 
    def aplicar_bloqueo(self, plantilla, cancha, fecha, momento):
        """Clona la plantilla en una cancha y fecha. Devuelve (bloqueo, reservas_anuladas)."""
 
        bloqueo = plantilla.clonar(cancha, fecha)
        anuladas = []
 
        for reserva in cancha.lista_reservas:
            if (reserva.estado == "Activa" and reserva.fecha == fecha and reserva.hora_inicio < bloqueo.hora_fin and reserva.hora_fin > bloqueo.hora_inicio):
 
                if self.anular_reserva(reserva, momento) is not None:
                    anuladas.append(reserva)
 
        cancha.agregar_bloqueo(bloqueo)
        print(f"Bloqueo '{bloqueo.motivo}' aplicado en {cancha.lugar} el {fecha}.")
        return bloqueo, anuladas
 
 
# Cancha
class Cancha:
 
    def __init__(self, estado, deporte, lugar, sede):
        self.deporte = deporte
        self.estado = estado
        self.lugar = lugar
        self.validador = sede.crear_validador()
        self.notificador = sede.crear_notificador()
        self.lista_reservas = []
        self.lista_bloqueos = []
 
    def hay_bloqueo(self, reserva):
        for bloqueo in self.lista_bloqueos:
            if (bloqueo.fecha == reserva.fecha and reserva.hora_inicio < bloqueo.hora_fin and reserva.hora_fin > bloqueo.hora_inicio):
                return True
        return False
 
    def verificar_disponibilidad(self, reserva):
 
        if self.hay_bloqueo(reserva):
            print("El horario no es disponible: la cancha está bloqueada")
            return False
 
        for reserva_existente in self.lista_reservas:
            if (reserva_existente.estado == "Activa" and reserva.fecha == reserva_existente.fecha and reserva.hora_inicio < reserva_existente.hora_fin and reserva.hora_fin > reserva_existente.hora_inicio):
 
                print("El horario no es disponible")
                return False
 
        print("El horario es disponible")
        return True
 
    def guardar_reserva(self, reserva):
        self.lista_reservas.append(reserva)
        print("Reserva agregada exitosamente.")
 
    def agregar_reserva(self, reserva):
 
        if self.hay_bloqueo(reserva):
            print("No se pudo agregar la reserva: la franja está bloqueada por un evento.")
            return False
 
        if self.verificar_disponibilidad(reserva):
            self.guardar_reserva(reserva)
            return True
 
        if reserva.prioridad.prioridad(reserva.hora_inicio):
            print("El usuario tiene prioridad para reservar.")
 
            for reserva_existente in self.lista_reservas:
 
                if (reserva_existente.estado == "Activa" and reserva_existente.fecha == reserva.fecha and reserva_existente.hora_inicio == reserva.hora_inicio and not reserva_existente.prioridad.prioridad(reserva_existente.hora_inicio)):
 
                    reserva_existente.estado = "Cancelada"
                    print(f"La reserva de {reserva_existente.titular.nombre} fue desplazada por prioridad. No se aplica penalidad.")
                    self.notificador.enviar_notificacion(reserva_existente.titular,"Tu reserva fue cancelada porque un equipo oficial tiene prioridad en esa franja.")
 
                    self.guardar_reserva(reserva)
                    return True
 
            print("No se encontró una reserva que se pueda desplazar.")
            return False
 
        print("No se pudo agregar la reserva debido a un conflicto de horario.")
        return False
 
    def agregar_bloqueo(self, bloqueo):
        self.lista_bloqueos.append(bloqueo)
 
    def mostrar_reservas(self):
 
        if len(self.lista_reservas) == 0:
            print("No hay reservas para esta cancha.")
            return
 
        print("-----------------Reservas de la cancha------------------")
        for i, reserva in enumerate(self.lista_reservas, start=1):
            print(f"{i}. Titular: {reserva.titular.nombre}, Fecha: {reserva.fecha}, "
                  f"Hora de inicio: {reserva.hora_inicio}, Hora de fin: {reserva.hora_fin}, "
                  f"Estado: {reserva.estado}")
 
 
# Reservas
class Reserva:
 
    def __init__(self, titular, hora_inicio, cancha, fecha, prioridad, politica_cancelacion):
        self.titular = titular
        self.hora_inicio = hora_inicio
        minutos = self.hora_inicio.hour * 60 + self.hora_inicio.minute + 60
        self.hora_fin = time((minutos // 60) % 24, minutos % 60)
        self.fecha = fecha
        self.cancha = cancha
        self.prioridad = prioridad
        self.politica_cancelacion = politica_cancelacion
        self.estado = "Activa"
 
    def cancelar_reserva(self, momento, politica=None):
 
        politica = politica or self.politica_cancelacion
 
        if self.estado != "Activa":
            print(f"La reserva no se puede cancelar: ya está en estado {self.estado}.")
            return self.estado
 
        if politica.noshow(self, momento):
            self.estado = "No Show"
            print(f"Reserva de {self.titular.nombre} cancelada tarde: se registra como No Show.")
            self.titular.registrar_veto(momento)
        else:
            self.estado = "Cancelada"
            print(f"Reserva de {self.titular.nombre} cancelada sin penalidad.")
 
        return self.estado
 
 
class ReservaRegular(Reserva):
 
    def __init__(self, titular, hora_inicio, cancha, fecha):
        super().__init__(titular, hora_inicio, cancha, fecha, SinPrioridad(), NoShowRegular())
 
 
class ReservaEquipo(Reserva):
 
    def __init__(self, titular, hora_inicio, cancha, fecha):
        super().__init__(titular, hora_inicio, cancha, fecha, ConPrioridad(), NoShowCapitan())
 
 
# Factory Method
class ReservasFactory:
 
    def crear_reserva(self, usuario, hora_inicio, cancha, fecha):
 
        if isinstance(usuario, Estudiante):
            return ReservaRegular(usuario, hora_inicio, cancha, fecha)
 
        if isinstance(usuario, Capitan):
            return ReservaEquipo(usuario, hora_inicio, cancha, fecha)
 
        raise ValueError("Tipo de usuario no válido para crear una reserva")
 
 
# Builder: reserva recurrente
class ReservaRecurrente:
 
    def __init__(self, solicitante, cancha, fecha_inicio, hora_inicio, semanas, equipo_prestado, notas, reservas):
        self.solicitante = solicitante
        self.cancha = cancha
        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_inicio
        self.semanas = semanas
        self.equipo_prestado = equipo_prestado
        self.notas = notas
        self.reservas = reservas
 
 
class ReservaRecurrenteBuilder:
 
    MIN_SEMANAS = 2
    MAX_SEMANAS = 8
 
    def __init__(self, solicitante, cancha, fecha_inicio, hora_inicio):
        self.solicitante = solicitante
        self.cancha = cancha
        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_inicio
        self.semanas = self.MIN_SEMANAS
        self.equipo_prestado = None
        self.notas = None
 
    def add_semanas(self, semanas):
        if not (self.MIN_SEMANAS <= semanas <= self.MAX_SEMANAS):
            raise ValueError(f"Las semanas deben estar entre {self.MIN_SEMANAS} y {self.MAX_SEMANAS}.")
        self.semanas = semanas
        return self
 
    def add_equipo_prestado(self, equipo):
        self.equipo_prestado = list(equipo)
        return self
 
    def add_notas(self, notas):
        self.notas = notas
        return self
 
    def construir(self):
        if not isinstance(self.solicitante, Capitan):
            raise ValueError("Solo un capitán puede hacer una reserva recurrente.")
 
        fabrica = ReservasFactory()
        reservas = []
        for n in range(self.semanas):
            fecha = self.fecha_inicio + timedelta(weeks=n)
            reservas.append(fabrica.crear_reserva(self.solicitante, self.hora_inicio, self.cancha, fecha))
 
        return ReservaRecurrente(self.solicitante, self.cancha, self.fecha_inicio, self.hora_inicio, self.semanas, self.equipo_prestado, self.notas, reservas)
 
 
# Abstract Factory: familia por sede (validador + notificador)
class ValidadorHorario:
 
    def horario_valido(self, reserva):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")
 
 
class Notificador:
 
    def enviar_notificacion(self, destinatario, mensaje):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")
 
 
class ValidadorHorarioNorte(ValidadorHorario):
 
    APERTURA = time(6, 0)
    CIERRE = time(22, 0)
 
    def horario_valido(self, reserva):
        return self.APERTURA <= reserva.hora_inicio < reserva.hora_fin <= self.CIERRE
 
 
class ValidadorHorarioSur(ValidadorHorario):
 
    APERTURA = time(7, 0)
    CIERRE = time(23, 0)
 
    def horario_valido(self, reserva):
        return self.APERTURA <= reserva.hora_inicio < reserva.hora_fin <= self.CIERRE
 
 
class NotificadorNorte(Notificador):
 
    def enviar_notificacion(self, destinatario, mensaje):
        print(f"[Correo institucional] Para {destinatario.nombre}: {mensaje}")
 
 
class NotificadorSur(Notificador):
 
    def enviar_notificacion(self, destinatario, mensaje):
        print(f"[Mensaje de texto] Para {destinatario.nombre}: {mensaje}")
 
 
class SedeFactory:
 
    def crear_validador(self):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")
 
    def crear_notificador(self):
        raise NotImplementedError("Este método debe ser implementado por las subclases.")
 
 
class SedeNorteFactory(SedeFactory):
 
    def crear_validador(self):
        return ValidadorHorarioNorte()
 
    def crear_notificador(self):
        return NotificadorNorte()
 
 
class SedeSurFactory(SedeFactory):
 
    def crear_validador(self):
        return ValidadorHorarioSur()
 
    def crear_notificador(self):
        return NotificadorSur()
 
 
# Prototype: bloqueo
class Bloqueo:
 
    def __init__(self, motivo, hora_inicio, hora_fin, equipo):
        self.motivo = motivo
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.equipo = list(equipo)
        self.cancha = None
        self.fecha = None
 
    def clonar(self, cancha, fecha):
        clon = copy.deepcopy(self)
        clon.cancha = cancha
        clon.fecha = fecha
        return clon
 
 
# Facade
class ReservaFacade:
 
    def __init__(self):
        self.fabrica_reservas = ReservasFactory()
        self.candado = threading.Lock()
 
    def reservar_cancha(self, usuario, cancha, hora_inicio, fecha, momento):
 
        if usuario.esta_suspendido(momento):
            print(f"Reserva rechazada: {usuario.nombre} está suspendido hasta {usuario.suspension}.")
            return None
 
        reserva = self.fabrica_reservas.crear_reserva(usuario, hora_inicio, cancha, fecha)
 
        if not cancha.validador.horario_valido(reserva):
            print(f"Reserva rechazada: {hora_inicio} está fuera del horario permitido de la sede de {cancha.lugar}.")
            return None
 
        with self.candado:
            confirmada = cancha.agregar_reserva(reserva)
 
        if not confirmada:
            print(f"Reserva rechazada: la cancha {cancha.lugar} no está disponible.")
            return None
 
        cancha.notificador.enviar_notificacion(usuario, "Tu reserva fue confirmada.")
        return reserva
 
    def reservar_recurrente(self, recurrente, momento):
 
        solicitante = recurrente.solicitante
        cancha = recurrente.cancha
 
        if solicitante.esta_suspendido(momento):
            print(f"Reserva recurrente rechazada: {solicitante.nombre} está suspendido hasta {solicitante.suspension}.")
            return None
 
        for reserva in recurrente.reservas:
            if not cancha.validador.horario_valido(reserva):
                print(f"Reserva recurrente rechazada: {reserva.hora_inicio} está fuera del horario permitido de la sede de {cancha.lugar}.")
                return None
 
        with self.candado:
 
            for numero, reserva in enumerate(recurrente.reservas, start=1):
                print(f"Verificando semana {numero} ({reserva.fecha}):")
                if not cancha.verificar_disponibilidad(reserva):
                    print(f"Reserva recurrente rechazada: conflicto en la semana {numero} ({reserva.fecha}). No se registró ninguna semana.")
                    return None
 
            for reserva in recurrente.reservas:
                cancha.guardar_reserva(reserva)
 
        cancha.notificador.enviar_notificacion(
            solicitante,
            f"Tu reserva recurrente de {recurrente.semanas} semanas fue confirmada.")
        return recurrente
 
    def cancelar_reserva(self, solicitante, reserva, momento):
 
        with self.candado:
            estado = solicitante.cancelar_reserva(reserva, momento)
 
        if estado is not None:
            reserva.cancha.notificador.enviar_notificacion(
                reserva.titular,
                f"Tu reserva del {reserva.fecha} a las {reserva.hora_inicio} fue cancelada por {solicitante.nombre}. Estado: {estado}.")
        return estado
 
    def bloquear_cancha(self, administrador, plantilla, canchas, fechas, momento):
 
        with self.candado:
            for cancha in canchas:
                for fecha in fechas:
                    _, anuladas = administrador.aplicar_bloqueo(plantilla, cancha, fecha, momento)
 
                    for reserva in anuladas:
                        cancha.notificador.enviar_notificacion(
                            reserva.titular,
                            f"Tu reserva del {reserva.fecha} a las {reserva.hora_inicio} fue anulada por el bloqueo '{plantilla.motivo}'.")