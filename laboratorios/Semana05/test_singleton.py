from singleton import GestorDeConfiguracion, reserva_permitida

def test_rechaza_reserva():
    config = GestorDeConfiguracion.ObtenerObjeto()
    config.modo_mantenimiento = True

    assert reserva_permitida(config) is False

def test_reserva_aceptada():
    config = GestorDeConfiguracion.ObtenerObjeto()
    config.modo_mantenimiento = False    #cambio para que la funcion no de error y pase la prueba

    assert reserva_permitida(config) is True

    #esta prueba falla porque al ejecutarla se mantiene el ultimo estado de la prueba anterior, es decir,
    #en la anterior reserva se puso el modo de mantenimiento en True, y al ejecutar esta prueba no se vuelve a poner en False, 
    #por lo que la prueba falla.