import socket
import servidor
from servidor.dados import Dados
from servidor.lista_clientes import ListaClientes
from servidor.processo_cliente import ProcessaCliente
from servidor.broadcast_emissor import ThreadBroadcast

class Maquina:
    def __init__(self):
        self.dados = Dados()
        self.clientes = ListaClientes() 
        
        self.s = socket.socket()
        self.s.bind(('', servidor.PORT))
        self.s.listen(5)

    def execute(self):
        print(f"À espera de lutadores na porta {servidor.PORT}...")
        
        # O Broadcast envia os dados 50 vezes por segundo (1/0.02)
        self.broadcast = ThreadBroadcast(self.clientes, self.dados, intervalo=0.02)
        self.broadcast.start()

        # Loop de escuta de novos jogadores
        while True:
            connection, address = self.s.accept()
            print("Cliente", address, "conectou-se!")
            
            # Criação de uma thread para tratar de cada jogador
            processa = ProcessaCliente(connection, address, self.dados, self.clientes)
            processa.start()