import socket
import json
import pygame
import sys
import cliente
from cliente.broadcast_receiver import BroadcastReceiver
from cliente.stickman import StickmanCliente 
from cliente.constantes import LARGURA_JANELA, ALTURA_JANELA, FPS
from cliente import mapa

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

        # Iniciar o Pygame usando o ficheiro de Constantes
        pygame.init()
        fonte_derrota = pygame.font.SysFont("Arial", 72, bold=True)
        ecra = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption(f"Stickman Arena - {self.meu_id}")
        relogio = pygame.time.Clock()

        players_visuais = {}
        rodar = True

        while rodar:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.send_str(self.connection, cliente.QUIT_OP)
                    rodar = False

            # Ler Teclado
            teclas = pygame.key.get_pressed()
            acoes = []
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: acoes.append("esquerda")
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: acoes.append("direita")
            if teclas[pygame.K_UP] or teclas[pygame.K_w]: acoes.append("saltar")
            if teclas[pygame.K_SPACE]: acoes.append("atacar") 
            
            self.send_str(self.connection, cliente.INPUT_OP)
            self.send_object(self.connection, acoes)

            # Renderizar os Gráficos
            ecra.fill((200, 230, 255))
            

            pygame.draw.rect(ecra, (100, 100, 100), (0, ALTURA_JANELA - 20, LARGURA_JANELA, 20))

            
            for plat in mapa.PLATAFORMAS:
                px_x = plat["x"] * LARGURA_JANELA
                px_y = plat["y"] * ALTURA_JANELA
                px_larg = plat["largura"] * LARGURA_JANELA
                px_alt = plat["altura"] * ALTURA_JANELA
                
                # Desenha a plataforma castanha
                pygame.draw.rect(ecra, (139, 69, 19), (px_x, px_y, px_larg, px_alt))
                # Desenha uma linha verde por cima para parecer relva
                pygame.draw.rect(ecra, (34, 139, 34), (px_x, px_y, px_larg, 5))

            for id_jog, dados_jog in self.estado_jogo_atual.items():
                if id_jog not in players_visuais:
                    players_visuais[id_jog] = StickmanCliente(id_jog)
                players_visuais[id_jog].atualizar(dados_jog)
                players_visuais[id_jog].desenhar(ecra)

            if self.meu_id in self.estado_jogo_atual:
                meus_dados = self.estado_jogo_atual[self.meu_id]
                fonte_texto = pygame.font.SysFont("Arial", 72, bold=True)
                
                # 1. DERROTA
                if meus_dados["vidas"] <= 0:
                    texto = fonte_texto.render("DERROTA", True, (255, 0, 0))
                    ecra.blit(texto, (LARGURA_JANELA//2 - texto.get_width()//2, ALTURA_JANELA//2))
                
                # 2. VITÓRIA
                else:
                    # Conta quantos jogadores na arena ainda têm vidas
                    jogadores_vivos = [id_j for id_j, dados_j in self.estado_jogo_atual.items() if dados_j["vidas"] > 0]
                    
                    # Se só sobrar 1
                    if len(jogadores_vivos) == 1 and len(self.estado_jogo_atual) > 1:
                        texto = fonte_texto.render("VITÓRIA!", True, (255, 215, 0)) # Amarelo Dourado
                        ecra.blit(texto, (LARGURA_JANELA//2 - texto.get_width()//2, ALTURA_JANELA//2))

            ids_mortos = [i for i in players_visuais if i not in self.estado_jogo_atual]
            for i in ids_mortos:
                del players_visuais[i]

            for player in players_visuais.values():
                player.desenhar(ecra)

            pygame.display.flip()
            relogio.tick(FPS)

        pygame.quit()
        sys.exit()