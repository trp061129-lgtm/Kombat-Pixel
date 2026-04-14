import pygame

class StickmanCliente:
    def __init__(self, id_jogador):
        self.id = id_jogador
        self.pos_x = 0
        self.pos_y = 0
        self.cor = (255, 255, 255)
        self.hp = 100
        self.rect = pygame.Rect(0, 0, 50, 100) # 

    def atualizar(self, dados_servidor):
        """
        Recebe o dicionário do servidor e atualiza os atributos locais.
        """
        self.pos_x = dados_servidor["pos_x"]
        self.pos_y = dados_servidor["pos_y"]
        self.cor = dados_servidor["cor"]
        self.hp = dados_servidor["hp"]
        
        #Corpo do personagem
        self.rect.topleft = (self.pos_x, self.pos_y)

    def desenhar(self, ecra):
        """
        Desenha o lutador no ecrã do jogo.
        """
        #Desenha o personagem
        pygame.draw.rect(ecra, self.cor, self.rect)
        
        #Desenha a Barra de Vida
        #Fundo vermelho (Vida perdida)
        pygame.draw.rect(ecra, (255, 0, 0), (self.pos_x, self.pos_y - 15, 50, 5))
        #Frente verde (Vida atual)
        pygame.draw.rect(ecra, (0, 255, 0), (self.pos_x, self.pos_y - 15, max(0, self.hp / 2), 5))