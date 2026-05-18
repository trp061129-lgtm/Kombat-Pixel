import pygame
from cliente.constantes import LARGURA_JANELA, ALTURA_JANELA
from cliente import mapa

class StickmanCliente:
    def __init__(self, id_jogador):
        self.id = id_jogador
        self.cor = (255, 255, 255)
        self.hp = 100
        
        self.largura = LARGURA_JANELA * mapa.BONECO_LARGURA
        self.altura = ALTURA_JANELA * mapa.BONECO_ALTURA
        
        self.pos_x_real = 0
        self.pos_y_real = 0
        self.rect = pygame.Rect(0, 0, self.largura, self.altura)

    def atualizar(self, dados_servidor):
        self.cor = dados_servidor["cor"]
        self.hp = dados_servidor["hp"]
        self.vidas = dados_servidor["vidas"]

        # Recebe os novos dados para saber desenhar o soco
        self.direcao = dados_servidor["direcao"]
        self.atacando = dados_servidor["atacando"]

        # Transforma de (0.0 - 1.0) para Pixeis Reais
        self.pos_x_real = dados_servidor["pos_x"] * LARGURA_JANELA
        self.pos_y_real = dados_servidor["pos_y"] * ALTURA_JANELA
        
        self.rect.topleft = (self.pos_x_real, self.pos_y_real)

    def desenhar(self, ecra):
        if self.vidas <= 0:
            return

        # Desenha o personagem
        pygame.draw.rect(ecra, self.cor, self.rect)

        # --- DESENHA AS VIDAS RESTANTES ---
        # Desenha pequenos círculos vermelhos a representar os "Stocks" (Vidas)
        raio = 4
        espacamento = 12
        for i in range(self.vidas):
            x_bolinha = self.pos_x_real + (i * espacamento)
            y_bolinha = self.pos_y_real - 25 # Fica um pouco acima da barra de vida
            pygame.draw.circle(ecra, (255, 50, 50), (int(x_bolinha), int(y_bolinha)), raio)

        if self.hp <= 0:
            return
        # Desenha o personagem
        pygame.draw.rect(ecra, self.cor, self.rect)
        
        if self.atacando:
            comp_braco = 30 # Tamanho do braço em píxeis
            # Se vira à direita, desenha à direita. Se vira à esquerda, desenha atrás do x.
            if self.direcao == 1:
                braco_rect = pygame.Rect(self.pos_x_real + self.largura, self.pos_y_real + 20, comp_braco, 15)
            else:
                braco_rect = pygame.Rect(self.pos_x_real - comp_braco, self.pos_y_real + 20, comp_braco, 15)
                
            pygame.draw.rect(ecra, (0, 0, 0), braco_rect) # Desenha um braço preto


        # Desenha a Barra de Vida
        barra_largura = self.largura
        barra_altura = 5
        
        # Fundo vermelho
        pygame.draw.rect(ecra, (255, 0, 0), (self.pos_x_real, self.pos_y_real - 15, barra_largura, barra_altura))
        
        # Frente verde dinâmica (A matemática converte a HP de 0-100 para a largura certa da barra)
        largura_vida_atual = max(0, (self.hp / 100) * barra_largura)
        pygame.draw.rect(ecra, (0, 255, 0), (self.pos_x_real, self.pos_y_real - 15, largura_vida_atual, barra_altura))