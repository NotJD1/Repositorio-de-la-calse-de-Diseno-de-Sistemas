import copy

class Computadora:
    def __init__(self):
        self.cpu = None
        self.ram = None
        self.disco = None
        self.gpu = None
        self.wifi = None

    def mostrar (self):
        print("CPU: ", self.cpu)
        print("RAM: " , self.ram)
        print("Disco: ", self.disco)
        print("GPU: ", self.gpu)
        print("Wifi:", self.wifi)

    def clonar(self):
        return copy.deepcopy(self) 

class ComputadoraBuilder:
    def __init__(self):
        self.computadora = Computadora()

    def add_cpu(self, cpu):
        self.computadora.cpu = cpu
        return self

    def add_ram(self, ram):
        self.computadora.ram = ram
        return self

    def add_disco(self, disco):
        self.computadora.disco = disco
        return self

    def add_gpu(self, gpu):
        self.computadora.gpu = gpu
        return self

    def add_wifi(self, wifi):
        self.computadora.wifi = wifi
        return self

    def build(self):
        return self.computadora

#main
def main():
    pc_builder = ComputadoraBuilder()

    #aqui pasa algo...

    pc_gamer = pc_builder.add_ram(4).add_gpu(18)

    #aqui hay código .....

    pc_gamer = pc_builder.add_disco(1).add_cpu(28).add_wifi("5G").build()

    pc_gamer.mostrar()

    pc_work = pc_gamer.clonar()

    pc_work.ram = 16

    pc_work.mostrar()

main()