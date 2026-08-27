#Vehículo -> que se mueva -> mover()

#Auto -> se mueve por carretera -> "Conduciendo por carretera"
#Bote -> se mueve por vehiculo -> "Navegando por agua"
#Avión -> se mueve por aire -> "Volando por el cielo"

#Comportamiento
class ComportamientoMover():
    def mover(self):
        raise NotImplementedError

#Tipo de comportamiento
class MoverPorCarretera(ComportamientoMover):
    def mover(self):
        print("Conduciendo por carretera")

class MoverPorAgua(ComportamientoMover):
    def mover(self):
        print("Navegando por agua")

class MoverPorAire(ComportamientoMover):
    def mover(self):
        print("Volando por el cielo")

#CLase padre
class Vehiculo:
    def __init__(self, comportamiento_mover):
        self.comportamiento_mover = comportamiento_mover

    def mover(self):
        self.comportamiento_mover.mover()

#Clase hija
class Auto(Vehiculo):
    def __init__(self):
        mover_carretera = MoverPorCarretera()
        super().__init__(mover_carretera)

class Bote(Vehiculo):
    def __init__(self):
        mover_agua = MoverPorAgua()
        super().__init__(mover_agua)    

class Avion(Vehiculo):
    def __init__(self):
        mover_aire = MoverPorAire()
        super().__init__(mover_aire)

if __name__ == "__main__":
    auto = Auto()
    auto.mover()

    bote = Bote()
    bote.mover()

    avion = Avion()
    avion.mover()