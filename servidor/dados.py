import threading
from servidor import (
    PLATAFORMAS, CHAO_Y, BONECO_LARGURA, BONECO_ALTURA, 
    VEL_X, VEL_Y, GRAVIDADE
)

class Dados:
    def __init__(self):
        self.estado_global = {}
        self.lock = threading.Lock()
        self.num_jogadores = 0
        self.cores = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]
        
        # --- CONSTANTES FÍSICAS ---
        self.plataformas = PLATAFORMAS
        self.CHAO_Y = CHAO_Y 
        self.VEL_X = VEL_X       
        self.VEL_Y = VEL_Y         
        self.GRAVIDADE = GRAVIDADE   


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
                    "vidas": 3,           # Vidas do jogador
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
            if jog["hp"] <= 0:
                return

            # --- MOVIMENTO HORIZONTAL ---
            if "direita" in acoes: 
                jog["pos_x"] += self.VEL_X
                jog["direcao"] = 1
                if jog["pos_x"] > 0.94: jog["pos_x"] = 0.94 
                
            if "esquerda" in acoes: 
                jog["pos_x"] -= self.VEL_X
                jog["direcao"] = -1
                if jog["pos_x"] < 0.0: jog["pos_x"] = 0.0  
                
            # --- FÍSICA DO CHÃO DINÂMICO ---
            chao_atual = self.CHAO_Y  
            
            for plat in self.plataformas:
                # Alinhamento horizontal com a plataforma 
                if plat["x"] - BONECO_LARGURA < jog["pos_x"] < plat["x"] + plat["largura"]:
                    
                    # Subtrai a altura do boneco
                    chao_plataforma = plat["y"] - BONECO_ALTURA
                    
                    # Verifica se o boneco já aterrou
                    if jog["pos_y"] <= chao_plataforma + self.GRAVIDADE:
                        
                        # Esta plataforma torna-se o novo chão
                        if chao_plataforma < chao_atual:
                            chao_atual = chao_plataforma

            # --- FÍSICA FLUIDA ---
            # A Gravidade
            jog["vel_y"] += self.GRAVIDADE

            # O Salto
            no_chao = jog["pos_y"] >= chao_atual
            jog["no_chao"] = no_chao
            if "saltar" in acoes and no_chao:
                jog["vel_y"] = -self.VEL_Y 
                
            # Aplica velocidade à posição
            jog["pos_y"] += jog["vel_y"]
            
            # Colisão com o chão 
            if jog["pos_y"] >= chao_atual: 
                jog["pos_y"] = chao_atual
                jog["vel_y"] = 0

            # --- GESTÃO DE COOLDOWNS ---
            if jog["cooldown"] > 0:
                jog["cooldown"] -= 1
                
            if jog["cooldown"] < 15:
                jog["atacando"] = False

            # --- COMBATE ---
            if "atacar" in acoes and jog["cooldown"] == 0:
                jog["cooldown"] = 25   
                jog["atacando"] = True 
                
                alcance = 0.08 
                
                for outro_id, outro_jog in self.estado_global.items():
                    if outro_id != jogador_id and outro_jog["vidas"] > 0: 
                        
                        dist_x = outro_jog["pos_x"] - jog["pos_x"]
                        dist_y = abs(outro_jog["pos_y"] - jog["pos_y"])
                        
                        if (jog["direcao"] == 1 and 0 < dist_x < alcance) or \
                           (jog["direcao"] == -1 and -alcance < dist_x < 0):
                            
                            if dist_y < 0.15:
                                outro_jog["hp"] -= 10 
                                
                                # --- SISTEMA DE MORTE E RESPAWN ---
                                if outro_jog["hp"] <= 0: 
                                    outro_jog["vidas"] -= 1 
                                    
                                    if outro_jog["vidas"] > 0:
                                        outro_jog["hp"] = 100       
                                        outro_jog["pos_x"] = 0.5    
                                        outro_jog["pos_y"] = 0.2    
                                        outro_jog["vel_y"] = 0      
                                    else:
                                        outro_jog["hp"] = 0
                                
                                # --- KNOCKBACK ---
                                forca_knockback_x = 0.05 
                                forca_knockback_y = 0.04 
                                
                                if jog["direcao"] == 1: 
                                    outro_jog["pos_x"] += forca_knockback_x
                                else:                   
                                    outro_jog["pos_x"] -= forca_knockback_x
                                    
                                outro_jog["pos_y"] -= forca_knockback_y
                                    
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