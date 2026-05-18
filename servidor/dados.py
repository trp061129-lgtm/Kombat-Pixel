import threading
from servidor import mapa

class Dados:
    def __init__(self):
        self.estado_global = {}
        self.lock = threading.Lock()
        self.num_jogadores = 0
        self.cores = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]
        
        # --- CONSTANTES FÍSICAS ---
        self.plataformas = mapa.PLATAFORMAS
        self.CHAO_Y = mapa.CHAO_Y # Usa o valor do mapa.py para manter a coerência
        self.VEL_X = 0.0075       # Velocidade horizontal
        self.VEL_Y = 0.03         # salto
        self.GRAVIDADE = 0.0015   # gravidade


    def adicionar_jogador(self, address):
        with self.lock:
            if self.num_jogadores < 4:
                self.num_jogadores += 1
                jogador_id = f"p{self.num_jogadores}"
                
                self.estado_global[jogador_id] = {
                    # O P1 nasce nos 20% do ecrã, o P2 nos 40%, etc.
                    "pos_x": 0.2 * self.num_jogadores, 
                    "pos_y": self.CHAO_Y, 
                    "hp": 100,
                    "cor": self.cores[self.num_jogadores - 1],
                    
                    # Variáveis de Combate e Física
                    "direcao": 1,         # 1 = Direita, -1 = Esquerda
                    "cooldown": 0,        # Tempo até poder dar outro soco
                    "atacando": False,    # Controla o desenho do braço
                    "vel_y": 0,           # Velocidade vertical atual
                    "vidas": 3,            # Stocks do jogador
                    "no_chao": True
                }
                return jogador_id
            return None

    def remover_jogador(self, jogador_id):
        with self.lock:
            if jogador_id in self.estado_global:
                del self.estado_global[jogador_id]

    def mover_jogador(self, jogador_id, acoes):
        with self.lock:
            if jogador_id not in self.estado_global:
                return
                
            jog = self.estado_global[jogador_id]
            
            # --- VERIFICAÇÃO DE ESTADO ---
            # Se o jogador estiver morto, ignora as teclas e corta a função aqui
            if jog["hp"] <= 0:
                return

            # --- MOVIMENTO HORIZONTAL ---
            if "direita" in acoes: 
                jog["pos_x"] += self.VEL_X
                jog["direcao"] = 1
                if jog["pos_x"] > 0.94: jog["pos_x"] = 0.94 # Limite da parede direita 
                
            if "esquerda" in acoes: 
                jog["pos_x"] -= self.VEL_X
                jog["direcao"] = -1
                if jog["pos_x"] < 0.0: jog["pos_x"] = 0.0  # Limite da parede esquerda
                
            # --- FÍSICA DO CHÃO DINÂMICO ---
            chao_atual = self.CHAO_Y  
            
            # Verifica todas as plataformas para ver se o jogador está sobre alguma
            for plat in self.plataformas:
                # Alinhamento horizontal com a plataforma
                if plat["x"] - mapa.BONECO_LARGURA < jog["pos_x"] < plat["x"] + plat["largura"]:
                    
                    # 2. Subtrai a altura do boneco para os pés tocarem no chão
                    chao_plataforma = plat["y"] - mapa.BONECO_ALTURA
                    
                    # 3. Verifica se o boneco já aterrou ou está quase a aterrar
                    if jog["pos_y"] <= chao_plataforma + self.GRAVIDADE:
                        
                        # 4. Esta plataforma torna-se o novo chão
                        if chao_plataforma < chao_atual:
                            chao_atual = chao_plataforma

            # --- FÍSICA FLUIDA ---
            # 1. A Gravidade puxa constantemente o boneco para baixo
            
            jog["vel_y"] += self.GRAVIDADE

            # 2. O Salto (Apenas permitido se estiver no chão)
            no_chao = jog["pos_y"] >= chao_atual
            jog["no_chao"] = no_chao
            if "saltar" in acoes and no_chao:
                jog["vel_y"] = -self.VEL_Y 
                
            # 3. Aplica a velocidade calculada à posição do boneco
            jog["pos_y"] += jog["vel_y"]
            
            # 4. Colisão com o chão 
            if jog["pos_y"] >= chao_atual: 
                jog["pos_y"] = chao_atual
                jog["vel_y"] = 0

            # --- GESTÃO DE COOLDOWNS ---
            if jog["cooldown"] > 0:
                jog["cooldown"] -= 1
                
            # Desliga a animação do soco a meio do cooldown
            if jog["cooldown"] < 15:
                jog["atacando"] = False

            # --- COMBATE ---
            if "atacar" in acoes and jog["cooldown"] == 0:
                jog["cooldown"] = 25   # Bloqueia novos ataques por 25 frames
                jog["atacando"] = True # Sinaliza o cliente para desenhar o soco
                
                alcance = 0.08 # 8% do ecrã de alcance do braço
                
                for outro_id, outro_jog in self.estado_global.items():
                    # Ignora se for o próprio jogador ou alguém já morto
                    if outro_id != jogador_id and outro_jog["vidas"] > 0: 
                        
                        dist_x = outro_jog["pos_x"] - jog["pos_x"]
                        dist_y = abs(outro_jog["pos_y"] - jog["pos_y"])
                        
                        # Se acertou no adversário 
                        if (jog["direcao"] == 1 and 0 < dist_x < alcance) or \
                           (jog["direcao"] == -1 and -alcance < dist_x < 0):
                            
                            if dist_y < 0.15:
                                outro_jog["hp"] -= 10 # Aplica o Dano
                                
                                # --- SISTEMA DE MORTE E RESPAWN ---
                                if outro_jog["hp"] <= 0: 
                                    outro_jog["vidas"] -= 1 
                                    
                                    if outro_jog["vidas"] > 0:
                                        # Respawn Automático
                                        outro_jog["hp"] = 100       
                                        outro_jog["pos_x"] = 0.5    # Centro do ecrã
                                        outro_jog["pos_y"] = 0.2    # Alto do céu
                                        outro_jog["vel_y"] = 0      # Reseta a inércia da queda
                                    else:
                                        # Morte Definitiva
                                        outro_jog["hp"] = 0
                                
                                # --- KNOCKBACK ---
                                forca_knockback_x = 0.05 # KNOCKBACK horizontal
                                forca_knockback_y = 0.04 # KNOCKBACK vertical
                                
                                # Aplica a força na direção do soco
                                if jog["direcao"] == 1: 
                                    outro_jog["pos_x"] += forca_knockback_x
                                else:                   
                                    outro_jog["pos_x"] -= forca_knockback_x
                                    
                                # Lança o adversário ao ar
                                outro_jog["pos_y"] -= forca_knockback_y
                                    
                                # Limites da Parede 
                                if outro_jog["pos_x"] > 0.94: outro_jog["pos_x"] = 0.94
                                if outro_jog["pos_x"] < 0.0: outro_jog["pos_x"] = 0.0

    def get_estado(self):
        with self.lock:
            estado_para_enviar = {}
            for id_jog, dados_jog in self.estado_global.items():
                estado_para_enviar[id_jog] = {
                    "pos_x": dados_jog["pos_x"],
                    "pos_y": dados_jog["pos_y"],
                    "hp": dados_jog["hp"],
                    "cor": dados_jog["cor"],
                    "direcao": dados_jog["direcao"],
                    "atacando": dados_jog["atacando"],
                    "vidas": dados_jog["vidas"],
                    "no_chao": dados_jog["no_chao"]
                }
            return estado_para_enviar