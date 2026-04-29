import socket
import json
import pygame
import sys
import cliente
from cliente.broadcast_receiver import BroadcastReceiver
from cliente.stickman import StickmanCliente 

class Interface:
    def __init__(self):
        self.connection = socket.socket()
        self.estado_jogo_atual = {} 
        self.meu_id = None

    def receive_str(self, connect, n_bytes: int) -> str:
        data = connect.recv(n_bytes)
        return data.decode()

    def send_str(self, connect, value: str) -> None:
        connect.send(value.encode())

    def send_int(self, connect: socket.socket, value: int, n_bytes: int) -> None:
        connect.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def receive_int(self, connect: socket.socket, n_bytes: int) -> int:
        data = connect.recv(n_bytes)
        return int.from_bytes(data, byteorder='big', signed=True)

    def send_object(self, connection, obj):
        data = json.dumps(obj).encode('utf-8')
        size = len(data)
        self.send_int(connection, size, cliente.INT_SIZE)
        connection.send(data)

    def receive_object(self, connection):
        size = self.receive_int(connection, cliente.INT_SIZE)
        data = connection.recv(size)
        return json.loads(data.decode('utf-8'))
    # ------------------------------------------------------------------

    def execute(self):
        print("A ligar ao Servidor do Jogo...")
        try:
            self.connection.connect((cliente.SERVER_ADDRESS, cliente.PORT))
        except Exception as e:
            print(f"Erro ao ligar: {e}")
            return

        # Pedido de Entrada
        self.send_str(self.connection, cliente.JOIN_OP)
        dados_boas_vindas = self.receive_object(self.connection)
        self.meu_id = dados_boas_vindas["id"]
        print(f"Conectado com sucesso! Sou o jogador: {self.meu_id}")

        # Iniciar a thread receiver
        receiver = BroadcastReceiver(self.connection, self.estado_jogo_atual)
        receiver.start()

        # Iniciar o Pygame
        pygame.init()
        ecra = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(f"Stickman Arena - {self.meu_id}")
        relogio = pygame.time.Clock()

        players_visuais = {} # Guarda as classes gráficas dos jogadores
        rodar = True

        while rodar:
            #Eventos do Sistema
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.send_str(self.connection, cliente.QUIT_OP)
                    rodar = False

            #Ler Teclado
            teclas = pygame.key.get_pressed()
            acoes = []
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: acoes.append("esquerda")
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: acoes.append("direita")
            if teclas[pygame.K_UP] or teclas[pygame.K_w]: acoes.append("saltar")

            #Enviar Comandos ao Servidor (MOVE_OP)
            self.send_str(self.connection, cliente.MOVE_OP)
            self.send_object(self.connection, acoes)

            #Renderizar os Gráficos
            ecra.fill((200, 230, 255)) # Fundo Azul Céu
            pygame.draw.rect(ecra, (100, 100, 100), (0, 600, 800, 50)) # Chão

            # Sincronizar personagens do ecrã com o dicionário que a Thread Receiver atualizou
            for id_jog, dados_jog in self.estado_jogo_atual.items():
                if id_jog not in players_visuais:
                    players_visuais[id_jog] = StickmanCliente(id_jog)
                
                players_visuais[id_jog].atualizar(dados_jog)

            # Apagar players que já saíram
            ids_mortos = [i for i in players_visuais if i not in self.estado_jogo_atual]
            for i in ids_mortos:
                del players_visuais[i]

            # Desenhar todos na lista
            for player in players_visuais.values():
                player.desenhar(ecra)

            pygame.display.flip()
            relogio.tick(60) # Mantém 60 frames por segundo

        pygame.quit()
        sys.exit()