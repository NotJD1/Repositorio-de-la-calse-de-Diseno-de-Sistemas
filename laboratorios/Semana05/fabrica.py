#Clases
class Estudiante():

    def __init__(self, nombre):
        self.nombre = nombre

class EquipoOficial():

    def __init__(self, nombre):
        self.nombre = nombre

#Tipos reservas
class ReservaPrioridad():

    def __init__ (self, cancha, fecha, hora_inicio, hora_fin, solicitante):

        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante

    def confirmar(self):
        return "Reseerva confirmada para " + self.solicitante.nombre


class ReservaRegular():

    def __init__ (self, cancha, fecha, hora_inicio, hora_fin, solicitante):

        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante

    def confirmar(self):
        return "Reseerva confirmada para " + self.solicitante.nombre



#Creadores de reservas

class CreadorReserva():

    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        raise NotImplementedError

class CreadorReservaRegular(CreadorReserva):

    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaRegular(cancha, fecha, hora_inicio, hora_fin, solicitante)

class CreadorReservaPrioridad(CreadorReserva):

    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaPrioridad(cancha, fecha, hora_inicio, hora_fin, solicitante)

class FabricaReserva():

    @staticmethod
    def elegir_creador(solicitante):

        if isinstance(solicitante, Estudiante):
            return CreadorReservaRegular()
        elif isinstance(solicitante, EquipoOficial):
            return CreadorReservaPrioridad()

def reservar_desde_web(cancha, fecha, hora_inicio, hora_fin, solicitante):

   creador = FabricaReserva.elegir_creador(solicitante)
   reserva = creador.crear_reserva(cancha, fecha, hora_inicio, hora_fin, solicitante)

   return reserva

   
#Main

def main():
    reserva_1 = reservar_desde_web("Cancha futbol", "2026-09-17", "18:00", "20:00", Estudiante("Juan"))
    reserva_2 = reservar_desde_web("Cancha futbol", "2026-09-17", "18:00", "20:00", EquipoOficial("Juan Capitan"))

    print(reserva_1.confirmar())
    print(reserva_2.confirmar())

def reservar_desde_hall():
        pass

if __name__ == "__main__":
    main()