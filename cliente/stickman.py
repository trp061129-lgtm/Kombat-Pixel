import pygame
import os


from cliente import LARGURA_JANELA, ALTURA_JANELA, BONECO_LARGURA, BONECO_ALTURA

class StickmanCliente:
    def __init__(self, id_jogador):
        self.id = id_jogador
        self.hp = 100
        self.vidas = 3
        
       
        self.largura = LARGURA_JANELA * BONECO_LARGURA
        self.altura = ALTURA_JANELA * BONECO_ALTURA
        
        # Histórico de posições
        self.pos_x_real = 0
        self.pos_y_real = 0
        self.pos_x_anterior = 0
        self.pos_y_anterior = 0 
        self.rect = pygame.Rect(0, 0, self.largura, self.altura)
        self.no_chao = True

        # --- DETEÇÃO DA COR POR ID (Palette Swapping) ---
        if self.id == "p1":   self.minha_cor = (255, 50, 50)    # Vermelho
        elif self.id == "p2": self.minha_cor = (50, 128, 255)   # Azul original
        elif self.id == "p3": self.minha_cor = (50, 255, 50)    # Verde
        else:                 self.minha_cor = (255, 255, 50)   # Amarelo

        # --- DICIONÁRIOS DE ANIMAÇÕES ---
        self.animacoes_direita = {"idle": [], "run": [], "jump": [], "attack": []}
        self.animacoes_esquerda = {"idle": [], "run": [], "jump": [], "attack": []}

        # Nomes exatos das tuas imagens
        sprites = {
            "idle": ["idle1.png"],
            "run": ["run1.png", "run2.png", "run3.png", "run4.png"],
            "jump": ["jump2.png"], 
            "attack": ["atk1.png", "atk2.png","atk3.png", "atk4.png"]
        }

        # Caminho absoluto para a pasta 'assets'
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        pasta_assets = os.path.join(pasta_atual, "assets")

        # Carregar, Redimensionar Proporcionalmente e Pintar
        for estado, lista_nomes in sprites.items():
            for nome in lista_nomes:
                try:
                    caminho_completo = os.path.join(pasta_assets, nome)
                    img = pygame.image.load(caminho_completo).convert_alpha()
                    
                    # --- ESCALA PROPORCIONAL ---
                    orig_largura, orig_altura = img.get_size()
                    
                    # A altura fica igual à altura da hitbox
                    nova_altura = int(self.altura)
                    # A largura usa Regra de 3 Simples para não deformar
                    nova_largura = int(orig_largura * (nova_altura / orig_altura))
                    
                    img = pygame.transform.scale(img, (nova_largura, nova_altura))
                    
                    # Pinta a imagem se não for o jogador 2 (Azul)
                    if self.id != "p2":
                        img = self._colorir_sprite(img, self.minha_cor)
                    
                    self.animacoes_direita[estado].append(img)
                    self.animacoes_esquerda[estado].append(pygame.transform.flip(img, True, False))
                except Exception as e:
                    print(f"Aviso: Não encontrei a imagem em: {caminho_completo}")

        # Controladores de Estado e Tempo
        self.estado_atual = "idle" 
        self.frame_atual = 0
        self.temporizador = 0
        self.fps_animacao = 5 # Troca de frame a cada 5 frames do jogo

    # --- FUNÇÃO AUXILIAR DE PINTURA ---
    def _colorir_sprite(self, surface, nova_cor):
        """Substitui o preenchimento azul pela cor do jogador, mantendo o contorno preto intacto."""
        img_colorida = surface.copy()
        largura, altura = img_colorida.get_size()
        
        for x in range(largura):
            for y in range(altura):
                r, g, b, a = img_colorida.get_at((x, y))
                # Se não for transparente E não for uma linha escura (contorno)
                if a > 0 and not (r < 40 and g < 40 and b < 40):
                    img_colorida.set_at((x, y), (nova_cor[0], nova_cor[1], nova_cor[2], a))
                    
        return img_colorida

    def atualizar(self, dados_servidor):
        self.hp = dados_servidor["hp"]
        self.vidas = dados_servidor["vidas"]
        self.direcao = dados_servidor["direcao"]
        self.atacando = dados_servidor["atacando"]
        self.no_chao = dados_servidor.get("no_chao", True) 

        self.pos_x_anterior = self.pos_x_real
        self.pos_y_anterior = self.pos_y_real

        self.pos_x_real = dados_servidor["pos_x"] * LARGURA_JANELA
        self.pos_y_real = dados_servidor["pos_y"] * ALTURA_JANELA
        
        self.rect.topleft = (self.pos_x_real, self.pos_y_real)

    def desenhar(self, ecra):
        if self.vidas <= 0:
            return

        # --- 1. MÁQUINA DE ESTADOS ---
        novo_estado = "idle"
        
        if self.atacando:
            novo_estado = "attack"
        elif not self.no_chao: 
            novo_estado = "jump"
        elif abs(self.pos_x_real - self.pos_x_anterior) > 0.1: 
            novo_estado = "run"

        # Reinicia a animação se o estado mudou
        if novo_estado != self.estado_atual:
            self.estado_atual = novo_estado
            self.frame_atual = 0
            self.temporizador = 0

        # --- 2. ESCOLHER A LISTA CERTA ---
        if self.direcao == 1:
            lista_imagens = self.animacoes_direita[self.estado_atual]
        else:
            lista_imagens = self.animacoes_esquerda[self.estado_atual]

        # --- 3. REPRODUZIR O "FILME" ---
        if len(lista_imagens) > 0:
            self.temporizador += 1
            if self.temporizador >= self.fps_animacao:
                self.temporizador = 0
                self.frame_atual = (self.frame_atual + 1) % len(lista_imagens)
            
            # --- ALINHAMENTO INTELIGENTE PELOS PÉS ---
            imagem_atual = lista_imagens[self.frame_atual]
            img_rect = imagem_atual.get_rect()
            
            # Alinha o meio da base da imagem com o meio da base da Hitbox
            img_rect.midbottom = self.rect.midbottom
            
            ecra.blit(imagem_atual, img_rect)
        else:
            # Plano B: Usa um retângulo da cor oficial se faltarem imagens
            pygame.draw.rect(ecra, self.minha_cor, self.rect)

        # --- 4. INTERFACE (Vidas e HP) ---
        raio = 4
        espacamento = 12
        for i in range(self.vidas):
            x_bolinha = self.pos_x_real + (i * espacamento)
            y_bolinha = self.pos_y_real - 25 
            pygame.draw.circle(ecra, (255, 50, 50), (int(x_bolinha), int(y_bolinha)), raio)

        if self.hp <= 0:
            return

        # Barra de Vida
        barra_largura = self.largura
        barra_altura = 5
        pygame.draw.rect(ecra, (255, 0, 0), (self.pos_x_real, self.pos_y_real - 15, barra_largura, barra_altura))
        largura_vida_atual = max(0, (self.hp / 100) * barra_largura)
        pygame.draw.rect(ecra, (0, 255, 0), (self.pos_x_real, self.pos_y_real - 15, largura_vida_atual, barra_altura))