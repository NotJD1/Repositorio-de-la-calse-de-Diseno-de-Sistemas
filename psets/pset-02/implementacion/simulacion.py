import threading
from datetime import date, time, datetime

from main import (
    Estudiante, Capitan, Administrador,
    Cancha, SedeNorteFactory, SedeSurFactory,
    ReservaRecurrenteBuilder, Bloqueo, ReservaFacade,
)


# Preparación: sedes, canchas, usuarios y Facade
fachada = ReservaFacade()

norte_futbol = Cancha("Disponible", "Fútbol", "Fútbol Norte 1", SedeNorteFactory())
norte_basket = Cancha("Disponible", "Básquet", "Básquet Norte 2", SedeNorteFactory())
sur_futbol = Cancha("Disponible", "Fútbol", "Fútbol Sur 1", SedeSurFactory())
sur_basket = Cancha("Disponible", "Básquet", "Básquet Sur 2", SedeSurFactory())

ana = Estudiante("Ana", "pw", 1, "E001", "ana@uni.edu")
luis = Estudiante("Luis", "pw", 2, "E002", "luis@uni.edu")
sofia = Estudiante("Sofía", "pw", 3, "E003", "sofia@uni.edu")
marta = Estudiante("Marta", "pw", 4, "E004", "marta@uni.edu")
pedro = Estudiante("Pedro", "pw", 5, "E005", "pedro@uni.edu")
tomas = Estudiante("Tomás", "pw", 6, "E006", "tomas@uni.edu")
valeria = Estudiante("Valeria", "pw", 7, "E007", "valeria@uni.edu")
andres = Estudiante("Andrés", "pw", 8, "E008", "andres@uni.edu")
jorge = Estudiante("Jorge", "pw", 9, "E009", "jorge@uni.edu")

carlos = Capitan("Carlos", "pw", 10, "Fútbol", date(2026, 9, 1), date(2026, 12, 15))
diana = Capitan("Diana", "pw", 11, "Fútbol", date(2026, 9, 1), date(2026, 12, 15))
elena = Capitan("Elena", "pw", 12, "Básquet", date(2026, 9, 1), date(2026, 12, 15))

admin = Administrador("Roberto", "pw", 99, "admin@uni.edu")


# Escenario 1: una reserva en cada sede
print("----------------------Una reserva en cada sede (validada y notificada en su sede)-----------------------")

momento = datetime(2026, 10, 10, 9, 0)

print("Ana reserva en Campus Norte (Fútbol Norte 1), 14/10 a las 10:00")
reserva_ana = fachada.reservar_cancha(ana, norte_futbol, time(10, 0), date(2026, 10, 14), momento)

print("Luis reserva en Campus Sur (Fútbol Sur 1), 14/10 a las 10:00")
reserva_luis = fachada.reservar_cancha(luis, sur_futbol, time(10, 0), date(2026, 10, 14), momento)


# Escenario 2: fuera del horario permitido de la sede
print("----------------------Reserva rechazada por estar fuera del horario de su sede-----------------------")

print("Sofía intenta reservar en Campus Sur a las 06:00 (Campus Sur abre a las 07:00)")
fachada.reservar_cancha(sofia, sur_futbol, time(6, 0), date(2026, 10, 14), momento)

print("Sofía intenta reservar en Campus Sur a las 23:00 (el bloque terminaría fuera del horario)")
fachada.reservar_cancha(sofia, sur_futbol, time(23, 0), date(2026, 10, 14), momento)


# Escenario 3: reserva recurrente exitosa y otra rechazada
print("----------------------Reserva recurrente exitosa y otra rechazada por conflicto-----------------------")

print("Carlos (capitán) pide 4 semanas, lunes 19/10 a las 18:00, con equipo y notas")
recurrente_carlos = (ReservaRecurrenteBuilder(carlos, norte_futbol, date(2026, 10, 19), time(18, 0)).add_semanas(4).add_equipo_prestado(["balones", "chalecos"]).add_notas("Entrenamiento oficial").construir())
fachada.reservar_recurrente(recurrente_carlos, momento)

print("Diana (capitán) pide 3 semanas desde el lunes 12/10 a las 18:00 en la misma cancha")
recurrente_diana = (ReservaRecurrenteBuilder(diana, norte_futbol, date(2026, 10, 12), time(18, 0)).add_semanas(3).construir())
fachada.reservar_recurrente(recurrente_diana, momento)

print("Comprobación: ninguna semana de Diana quedó registrada")
reservas_diana = [r for r in norte_futbol.lista_reservas if r.titular is diana]
print(f"Reservas de Diana registradas en la cancha: {len(reservas_diana)}")


# Escenario 4: tres cancelaciones con resultados distintos
print("----------------------Tres cancelaciones con resultados distintos-----------------------")

print("Marta (estudiante) reserva el 15/10 a las 15:00 en Básquet Norte 2")
reserva_marta = fachada.reservar_cancha(marta, norte_basket, time(15, 0), date(2026, 10, 15), momento)

print("Elena (capitán) reserva el 20/10 a las 19:00 en Básquet Norte 2")
reserva_elena = fachada.reservar_cancha(elena, norte_basket, time(19, 0), date(2026, 10, 20), momento)

print("Pedro (estudiante) reserva el 21/10 a las 16:00 en Básquet Norte 2")
reserva_pedro = fachada.reservar_cancha(pedro, norte_basket, time(16, 0), date(2026, 10, 21), momento)

print("4a) Marta cancela el 13/10 a las 10:00: faltan más de 2 horas -> a tiempo")
fachada.cancelar_reserva(marta, reserva_marta, datetime(2026, 10, 13, 10, 0))
print(f"Estado de la reserva de Marta: {reserva_marta.estado} | No-shows de Marta: {len(marta.fechas_no_show)}")

print("4b) Elena (capitán) cancela el 20/10 a las 08:00: faltan 11 horas (< 24) -> no-show")
fachada.cancelar_reserva(elena, reserva_elena, datetime(2026, 10, 20, 8, 0))
print(f"Estado de la reserva de Elena: {reserva_elena.estado} | No-shows de Elena: {len(elena.fechas_no_show)}")

print("4c) El administrador anula la reserva de Pedro el 21/10 a las 15:00 (1 hora antes): sin penalidad")
fachada.cancelar_reserva(admin, reserva_pedro, datetime(2026, 10, 21, 15, 0))
print(f"Estado de la reserva de Pedro: {reserva_pedro.estado} | No-shows de Pedro: {len(pedro.fechas_no_show)}")

print("----------------------Tres no-shows en el mismo mes y luego intento de reservar-----------------------")

print("Tomás reserva tres días seguidos a las 10:00 en Básquet Sur 2 (22, 23 y 24 de octubre)")
reservas_tomas = []
for dia in (22, 23, 24):
    reservas_tomas.append(
        fachada.reservar_cancha(tomas, sur_basket, time(10, 0), date(2026, 10, dia), momento))

for reserva, dia in zip(reservas_tomas, (22, 23, 24)):
    print(f"Tomás cancela el {dia}/10 a las 09:00 (1 hora antes) -> no-show")
    fachada.cancelar_reserva(tomas, reserva, datetime(2026, 10, dia, 9, 0))
    print(f"No-shows de Tomás en octubre: {tomas.contar_vetos_mensuales(datetime(2026, 10, dia, 9, 0))}")

print("Tomás intenta reservar el 27/10 estando suspendido")
fachada.reservar_cancha(tomas, sur_basket, time(10, 0), date(2026, 10, 27), datetime(2026, 10, 25, 9, 0))

print("Pasados los 7 días de suspensión (01/11), Tomás vuelve a poder reservar")
fachada.reservar_cancha(tomas, sur_basket, time(10, 0), date(2026, 11, 3), datetime(2026, 11, 1, 9, 0))


# Escenario 6: bloqueo clonado en dos canchas
print("----------------------Bloqueo clonado en dos canchas (una con reserva existente)-----------------------")

print("Reserva existente de Ana: Fútbol Norte 1, 14/10 a las 10:00")
print(f"Estado de la reserva de Ana antes del bloqueo: {reserva_ana.estado}")

print("El administrador define la plantilla del torneo y la aplica en dos canchas el 14/10")
plantilla = Bloqueo("Torneo interfacultades", time(10, 0), time(12, 0), ["red", "balones"])
fachada.bloquear_cancha(admin, plantilla, [norte_futbol, norte_basket],[date(2026, 10, 14)], datetime(2026, 10, 12, 9, 0))

print(f"\nEstado de la reserva de Ana después del bloqueo: {reserva_ana.estado}")
print(f"No-shows de Ana (debe ser 0, el administrador nunca penaliza): {len(ana.fechas_no_show)}")

print("Prototype: modificar el equipo de un clon no afecta a la plantilla")
clon = norte_futbol.lista_bloqueos[0]
clon.equipo.append("chalecos")
print(f"Equipo del clon:      {clon.equipo}")
print(f"Equipo de la plantilla: {plantilla.equipo}")

print("Jorge intenta reservar Fútbol Norte 1 el 14/10 a las 10:00, franja bloqueada")
fachada.reservar_cancha(jorge, norte_futbol, time(10, 0), date(2026, 10, 14), datetime(2026, 10, 12, 10, 0))


# Escenario 7: dos hilos reservando la misma cancha y franja
print("----------------------Dos hilos intentan reservar la misma cancha y franja-----------------------")

barrera = threading.Barrier(2)
resultados = {}


def intentar(usuario):
    barrera.wait()
    resultados[usuario.nombre] = fachada.reservar_cancha(usuario, norte_futbol, time(12, 0), date(2026, 10, 16), datetime(2026, 10, 10, 11, 0))


hilos = [threading.Thread(target=intentar, args=(valeria,)),threading.Thread(target=intentar, args=(andres,))]

print("Valeria y Andrés piden Fútbol Norte 1, 16/10 a las 12:00, al mismo tiempo")
for hilo in hilos:
    hilo.start()
for hilo in hilos:
    hilo.join()

confirmadas = [r for r in norte_futbol.lista_reservas if r.fecha == date(2026, 10, 16) and r.hora_inicio == time(12, 0) and r.estado == "Activa"]

print()
for nombre, reserva in resultados.items():
    print(f"{nombre}: {'CONFIRMADA' if reserva is not None else 'rechazada'}")
print(f"Reservas confirmadas para esa franja: {len(confirmadas)} (debe ser exactamente 1)")

print("\nFin de la simulación.")