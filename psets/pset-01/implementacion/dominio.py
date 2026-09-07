from datetime import date, time, timedelta, datetime


# Comportamiento de prioridad
class ComportamientoPrioridad:
    def prioridad(self, hora_inicio):
        raise NotImplementedError


class ConPrioridad(ComportamientoPrioridad):
    def prioridad(self, hora_inicio):
        return hora_inicio < time(18, 0)


class SinPrioridad(ComportamientoPrioridad):
    def prioridad(self, hora_inicio):
        return False


# Clase base
class Usuario:
    def __init__(self, nombre, contrasena, comportamiento_prioridad):
        self.nombre = nombre
        self.contrasena = contrasena
        self.comportamiento_prioridad = comportamiento_prioridad
        self.id_usuario = id(self)  



# Herencia
class Estudiante(Usuario):
    def __init__(self,  nombre, contrasena, codigo_estudiante, mail):
        self.codigo_estudiante = codigo_estudiante
        self.mail = mail
        sin_prioridad = SinPrioridad()  # Instancia de SinPrioridad para el estudiante
        super().__init__(nombre, contrasena, sin_prioridad)  


class Capitan(Usuario):
    def __init__(self, nombre, contrasena, deporte, fecha_inicial, fecha_final):
        self.deporte = deporte
        self.fecha_inicial = fecha_inicial
        self.fecha_final = fecha_final
        con_prioridad = ConPrioridad()  # Instancia de ConPrioridad para el capitán
        super().__init__(nombre, contrasena, con_prioridad)


class Administrador(Usuario):
    def __init__(self, nombre, contrasena, mail):
        self.mail = mail
        prioridad = SinPrioridad()
        super().__init__(nombre, contrasena, prioridad)

    def gestionar_cancha(self, cancha, estado):
        cancha.estado = estado
        print(f"Estado de {cancha.lugar} actualizado a {estado}.")

    def resolver_conflicto(self, reserva, accion, nueva_hora_inicio=None, nueva_hora_fin=None):
        if accion == "c":
            return reserva.cancelar_reserva()
        if accion == "m":
            if nueva_hora_inicio is None or nueva_hora_fin is None:
                print("Debe indicar las nuevas horas de la reserva.")
                return False
            if (
                reserva.fecha < date.today()
                or nueva_hora_inicio < reserva.cancha.disponibilidad[0]
                or nueva_hora_fin > reserva.cancha.disponibilidad[1]
                or nueva_hora_inicio >= nueva_hora_fin
            ):
                print("No se puede modificar la reserva con ese horario.")
                return False

            for reserva_existente in reserva.cancha.lista_reservas:
                if reserva_existente is reserva:
                    continue
                se_cruzan = (
                    reserva.fecha == reserva_existente.fecha
                    and nueva_hora_inicio < reserva_existente.hora_fin
                    and nueva_hora_fin > reserva_existente.hora_inicio
                )
                if se_cruzan:
                    print("No se puede modificar la reserva debido a un conflicto de horario.")
                    return False

            reserva.hora_inicio = nueva_hora_inicio
            reserva.hora_fin = nueva_hora_fin
            print("Reserva modificada exitosamente.")
            return True

        print("Acción de conflicto no válida.")
        return False



class Cancha:
    def __init__(self, estado, deporte, lugar):
        self.estado = estado
        self.deporte = deporte
        self.lugar = lugar
        self.disponibilidad = (time(16, 0), time(22, 0))
        self.lista_reservas = []  # La cancha contiene sus reservas

    def verificar_disponibilidad(self, fecha, hora_inicio, hora_fin):
        if self.estado != "Disponible":
            return False

        if fecha < date.today():
            return False

        if hora_inicio < self.disponibilidad[0]:
            return False

        if hora_fin > self.disponibilidad[1]:
            return False

        if hora_inicio >= hora_fin:
            return False

        for reserva in self.lista_reservas:
            if reserva.fecha == fecha:
                se_cruzan = (hora_inicio < reserva.hora_fin and hora_fin > reserva.hora_inicio)

                if se_cruzan:
                    return False

        return True

    def agregar_reserva(self, reserva):
        if (self.estado != "Disponible" or reserva.fecha < date.today() or reserva.hora_inicio < self.disponibilidad[0] or reserva.hora_fin > self.disponibilidad[1] or reserva.hora_inicio >= reserva.hora_fin):
            print("No se puede agregar la reserva debido a que no hay disponibilidad.")
            return False

        disponible = self.verificar_disponibilidad(reserva.fecha, reserva.hora_inicio, reserva.hora_fin)

        if disponible:
            self.lista_reservas.append(reserva)
            print("Reserva agregada exitosamente.")
            return True

        if not reserva.usuario.comportamiento_prioridad.prioridad(reserva.hora_inicio):
            print("No se puede agregar la reserva debido a que no hay disponibilidad.")
            return False

        reservas_en_conflicto = []
        for reserva_existente in self.lista_reservas:
            se_cruzan = (
                reserva.fecha == reserva_existente.fecha
                and reserva.hora_inicio < reserva_existente.hora_fin
                and reserva.hora_fin > reserva_existente.hora_inicio
            )
            if se_cruzan:
                reservas_en_conflicto.append(reserva_existente)

        if not reservas_en_conflicto:
            print("No se puede agregar la reserva debido a que no hay disponibilidad.")
            return False

        for reserva_existente in reservas_en_conflicto:
            if not isinstance(reserva_existente.usuario, Estudiante):
                print("Reserva rechazada: no se puede cancelar una reserva de un capitán.")
                return False

        for reserva_existente in reservas_en_conflicto:
            self.lista_reservas.remove(reserva_existente)

        self.lista_reservas.append(reserva)
        print("Reserva anterior cancelada. Reserva del capitán creada.")
        return True

    def mirar_reservas(self):
        if len(self.lista_reservas) == 0:
            print("No hay reservas para esta cancha. Puedes crear una nueva reserva.")

        elif len(self.lista_reservas) >= 1:
            print(f"Reservas para la cancha {self.lugar}:")
            for i, reserva in enumerate(self.lista_reservas):
                print(f"{i+1}. Fecha: {reserva.fecha}, Hora: {reserva.hora_inicio} - {reserva.hora_fin}, Usuario: {reserva.usuario.nombre}")


class Reserva:
    def __init__(self, fecha, hora_inicio, hora_fin, cancha, usuario):
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.cancha = cancha
        self.usuario = usuario
        self.estado = "Activa"

    def verificar_reserva(self):
        return self.cancha.verificar_disponibilidad(
            self.fecha,
            self.hora_inicio,
            self.hora_fin
        )

    def cancelar_reserva(self, ahora=None):
        if self not in self.cancha.lista_reservas:
            print("La reserva no está activa en esta cancha.")
            return False

        ahora = ahora or datetime.now()
        momento_inicio = datetime.combine(self.fecha, self.hora_inicio)
        if ahora > momento_inicio - timedelta(hours=2):
            print("Reserva cancelada como No-Show")
            self.estado = "No-Show"
        else:
            self.estado = "Cancelada"
            print("Reserva cancelada con éxito")

        self.cancha.lista_reservas.remove(self)
        return True
