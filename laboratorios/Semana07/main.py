from abc import ABC, abstractmethod

import random

# Personajes
# Factory (solo personaje de jugador)

class Personaje ():

    def __init__(self, nombre, vida, ataque):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque

    def recibirAtaque(self, danio):
        self.vida -= danio
        if self.vida < 0:
            self.vida = 0


class Guerrero(Personaje):

    def __init__(self, nombre, vida, ataque):
        super().__init__(nombre, vida, ataque)


class Soldado(Personaje):

    def __init__(self, nombre, vida, ataque):
        super().__init__(nombre, vida, ataque)


class Dragon(Personaje):

    def __init__(self, nombre, vida, ataque):
        super().__init__(nombre, vida, ataque)


class Alien(Personaje):

    def __init__(self, nombre, vida, ataque):
        super().__init__(nombre, vida, ataque)


class PersonajeFactory():

    @staticmethod
    def crear_personajes(tipo):

        if tipo == "guerrero":
            return Guerrero("Guerrero", 100, 20)
        
        elif tipo == "soldado":
            return Soldado("Soldado", 120, 15)

#Crear mundos (abstract factory)

class EnemigoGuerrero():   

    def crear_enemigo(self):
        return Dragon("Dragon", 100, 15)

class EnemigoSoldado():   

    def crear_enemigo(self):
        return Alien("Alien", 120, 12)

class MundoAbstractFactory(ABC):

    @abstractmethod
    def crear_jugador(self):
        pass

    @abstractmethod
    def crear_enemigo(self):
        pass

class FantasyFactory(MundoAbstractFactory):
       
    def crear_jugador(self):
        return PersonajeFactory.crear_personajes("guerrero")

    def crear_enemigo(self):
        return EnemigoGuerrero().crear_enemigo()
    

class SciFiFactory(MundoAbstractFactory):

    def crear_jugador(self):
        return PersonajeFactory.crear_personajes("soldado")

    def crear_enemigo(self):
        return EnemigoSoldado().crear_enemigo()

#Estrategia de combate (strategy)

class AtaqueNormal():

    def ataque(self, personaje):
        danio = personaje.ataque
        print(f"{personaje.nombre} realiza un ataque normal con daño de {danio}.")

        return danio

class AtaqueFuerte():

    def ataque(self, personaje):
        danio = personaje.ataque * 2
        print(f"{personaje.nombre} realiza un ataque fuerte con daño de {danio}.")
        return danio

class Combate():

    def __init__(self, estrategia):
        self.estrategia = estrategia

    def ataque (self, personaje):
        return self.estrategia.ataque(personaje)

#Configuracion del juego (singleton)
class GameConfig():

    _objeto = None

    def __init__(self):
        GameConfig._objeto = self
        self._dificultad = "Normal"
        self._maximo_de_turnos = 10

    @staticmethod
    def obtener_configuracion():
        if GameConfig._objeto is None:
            GameConfig()

        return GameConfig._objeto

#Juego (facade)

class GameFacade():

    def __init__(self, factory):
        
        self.mundo = factory
        self.jugador = self.mundo.crear_jugador()
        self.enemigo = self.mundo.crear_enemigo()

    def iniciar_juego(self):

        print(f"Eres un {self.jugador.nombre} y tu enemigo es un {self.enemigo.nombre}.")
        print(f"Tienes {self.jugador.vida} puntos de vida y tu enemigo tiene {self.enemigo.vida} puntos de vida.")
        print("¡Que comience la batalla!")
        turno = 0

        while(self.jugador.vida > 0 and self.enemigo.vida > 0  and turno < GameConfig.obtener_configuracion()._maximo_de_turnos):

            turno += 1

            print(f"Turno {turno}:----------------------------")
            print("Estos son tus ataques disponibles: \n1. Ataque Normal \n2. Ataque Fuerte")
            opcion = int(input("Ingresa el número del ataque que deseas realizar: "))

            if opcion == 1:
                estrategia = AtaqueNormal()

            elif opcion == 2:
                estrategia = AtaqueFuerte()

            else: 
                print("Opción no válida. Se realizará un ataque normal por defecto.")
                estrategia = AtaqueNormal()

            danio = Combate(estrategia).ataque(self.jugador)
            self.enemigo.recibirAtaque(danio)

            print(f"Tu enemigo tiene {self.enemigo.vida} puntos de vida restantes.")

            estrategia_enemigo = random.choice([1,2])

            if estrategia_enemigo == 1:
                estrategia_enemigo = AtaqueNormal()

            elif estrategia_enemigo == 2:
                estrategia_enemigo = AtaqueFuerte()

            danio_enemigo = Combate(estrategia_enemigo).ataque(self.enemigo)
            self.jugador.recibirAtaque(danio_enemigo)
            print(f"Tu personaje tiene {self.jugador.vida} puntos de vida restantes.")

        if self.jugador.vida <= 0:
            print(f"Has sido derrotado en el turno {turno}.")

        elif self.enemigo.vida <= 0:
            print(f"¡Felicidades! Has derrotado a tu enemigo. en el turno {turno}.")

        else:
            print(f"El juego ha terminado en empate después de {turno} turnos.")

#iniciar juego

def main():
    print("Bienvenido al juego de combate.")
    print("Estos son los mundos disponibles: \n 1. Fantasía \n 2. Ciencia Ficción")
    factory = int(input("Ingresa el número del mundo que deseas jugar: "))

    if factory == 1:

        game = GameFacade(FantasyFactory())
        print("-----------------MUNDO DE FANTASIA!!!-----------------")

    elif factory == 2:

        game = GameFacade(SciFiFactory())
        print("---------------MUNDO DE CIENCIA FICCIÓN!!!---------------")

    else:
        print("Opción no válida.")
        return

    game.iniciar_juego()

main()