class GestorDeConfiguracion:
    _objeto = None

    def __init__(self):
        GestorDeConfiguracion._objeto = self
        self.modo_mantenimiento = False

    @staticmethod
    def ObtenerObjeto():
        if GestorDeConfiguracion._objeto is None:
            GestorDeConfiguracion()

        return GestorDeConfiguracion._objeto

def reserva_permitida(gestor):
    return not gestor.modo_mantenimiento