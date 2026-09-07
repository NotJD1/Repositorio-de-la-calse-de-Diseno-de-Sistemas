from datetime import date, datetime, time, timedelta
from dominio import Usuario, Estudiante, Capitan, Administrador, Cancha, Reserva

if __name__ == "__main__":

    # Crear usuarios
    cancha_1= Cancha("Disponible", "futbol", "Cancha 1")
    cancha_2= Cancha("Disponible", "Basketball", "Cancha 2")
    estudiante_A = Estudiante("Juan", "123", "E001", "juan@example.com")
    estudiante_B = Estudiante("Maria", "456", "E002", "maria@example.com")
    capitan = Capitan("Alex", "456", "futbol", date(2024, 6, 1), date(2024, 6, 30))
    administrador = Administrador("admin","789", "admin@example.com")

    #lista de reservas
    cancha_1.mirar_reservas()

    #Otras reservas
    reserva_3 = Reserva(date(2026, 9, 8), time(18, 0), time(19, 0), cancha_1, capitan) #Reserva con Capitan
    reserva_4 = Reserva(date(2026, 9, 8), time(19, 0), time(20, 0), cancha_1, estudiante_B) 
    reserva_5 = Reserva(date(2026, 9, 8), time(16, 0), time(17, 0), cancha_1, estudiante_A) 
    cancha_1.agregar_reserva(reserva_3)
    cancha_1.agregar_reserva(reserva_4)
    cancha_1.agregar_reserva(reserva_5)

    #Creacion de reserva exitosa
    print("------------------Creacion de reserva exitosa--------------------")
    print("Estudiante empieza a crear una reserva")
    reserva_1 = Reserva(date(2026, 9, 7), time(19, 0), time(20, 0), cancha_1, estudiante_A)
    if reserva_1.verificar_reserva():
        cancha_1.agregar_reserva(reserva_1)
        print("Reserva creada exitosamente")
    else:
        print("No se pudo crear la reserva debido a un conflicto de horario.")


    #Creacion de reserva fallida por conflicto de horario
    print("------------------Creacion de reserva fallida por conflicto de horario--------------------")
    print("Estudiante empieza a crear una reserva")
    reserva_2 = Reserva(date(2026, 9, 7), time(19, 30), time(20, 0), cancha_1, estudiante_B)
    if reserva_2.verificar_reserva():
        cancha_1.agregar_reserva(reserva_2)
  
    else:
        print("No se pudo crear la reserva debido a un conflicto de horario.")

    #Creacion de reserva fallida por conflicto de horario con Capitan
    print("------------------Creacion de reserva fallida por conflicto de horario con Capitan--------------------")
    print("Estudiante empieza a crear una reserva")
    reserva_6 = Reserva(date(2026, 9, 8), time(18, 0), time(19, 0), cancha_1, estudiante_A)
    if reserva_6.verificar_reserva():
        cancha_1.agregar_reserva(reserva_6)
        
    else:
        print("No se pudo crear la reserva debido a un conflicto de horario.")
       

    #Creacion de reserva hecha por un Capitan
    print("------------------Creacion de reserva hecha por un Capitan--------------------")
    print("Capitan empieza a crear una reserva")
    reserva_6 = Reserva(date(2026, 9, 8), time(16, 0), time(17, 0), cancha_1, capitan)
    cancha_1.agregar_reserva(reserva_6)

    #Cancelacion de reserva
    print("------------------Cancelar reserva--------------------")
    print("Estudiante empieza a cancelar una reserva")
    reserva_1.cancelar_reserva()

    #Cancelacion por No Show
    print("------------------Cancelando reserva por No-Show--------------------")
    print("Estudiante crea una reserva para dentro de poco tiempo")
    fecha_no_show = date(2026, 9, 10)
    hora_inicio = time(18, 0)
    hora_fin = time(19, 0)

    reserva_noShow = Reserva(fecha_no_show, hora_inicio, hora_fin, cancha_2, estudiante_B)
    cancha_2.agregar_reserva(reserva_noShow)

    # Se simula que "ahora" son 30 minutos antes del inicio de la reserva,
    # es decir, dentro de la ventana de 2 horas que activa la regla de No-Show.
    ahora_simulada = datetime.combine(fecha_no_show, hora_inicio) - timedelta(minutes=30)
    print("Estudiante empieza a cancelar una reserva")
    reserva_noShow.cancelar_reserva(ahora=ahora_simulada)
    
        
