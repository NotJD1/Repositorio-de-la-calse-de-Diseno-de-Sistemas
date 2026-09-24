from abc import ABC, abstractmethod

class EstrategiaDescuento(ABC):

    @abstractmethod
    def aplicar_descuento(self, precio_base):
        pass

class SinDescuento(EstrategiaDescuento):

    def aplicar_descuento(self, precio_base):
        return precio_base

class DescuentoVIP(EstrategiaDescuento):

    def aplicar_descuento(self, precio_base):
        return precio_base * 0.80

class DescuentoEstudiante(EstrategiaDescuento):

    def aplicar_descuento(self, precio_base):
        return precio_base * 0.95

class DescuentoEmpleado(EstrategiaDescuento):

    def aplicar_descuento(self, precio_base):
        return precio_base * 0.75

class Compra:

    def __init__(self , EstrategiaDescuento):
       self.estrategia_descuento = EstrategiaDescuento

    def calcular_total (self, precio):
       return self.estrategia_descuento.aplicar_descuento(precio)

def main():

    sin_descuento = SinDescuento()
    vip_descuento = DescuentoVIP()
    estudiante_descuento = DescuentoEstudiante()
    empleado_descuento = DescuentoEmpleado()

    compra_1 = Compra(sin_descuento)
    print(compra_1.calcular_total(100))

    compra_2 = Compra(vip_descuento)
    print(compra_2.calcular_total(1000))

    compra_3 = Compra(estudiante_descuento)
    print(compra_3.calcular_total(10))

    compra_4 = Compra(empleado_descuento)
    print(compra_4.calcular_total(1000))


main()