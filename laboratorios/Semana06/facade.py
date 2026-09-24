class Inventario:
    def verificar(self, producto):
        print(f"Verificando el stock de: {producto}")
        return True

class Pago:

    def procesar(self, monto):
        print(f"Procesando pago: {monto}")
        return True

class Envio:

    def crear_envio(self, producto):
        print(f"Preparando el envío del: {producto}")
        return True

class Notificacion:
    
    def notificar_envio(self, producto):
        print(f"Hola, tu {producto} fue commprado y será enviado pronto.")
        return True

class TiendaFacade():

    def __init__(self):
        self.inventario = Inventario()
        self.pago = Pago()
        self.envio = Envio()
        self.notificacion = Notificacion()

    def comprar(self, producto, precio):

        if not self.inventario.verificar(producto):
            print("No hay stock")
            return 
        
        if not self.pago.procesar(precio):
            print("Falló el pago")
            return

        self.envio.crear_envio(producto)

        print("Compra completada")

        self.notificacion.notificar_envio(producto)


def main():
    
    tienda = TiendaFacade()

    tienda.comprar("Laptop", 1500)

main()