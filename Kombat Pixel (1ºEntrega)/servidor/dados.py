import threading

class Dados:
    def __init__(self):
        self.estado_global = {}
        self.lock = threading.Lock()
        self.num_jogadores = 0
        self.cores = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]

    def adicionar_jogador(self, address):
        with self.lock:
            if self.num_jogadores < 4:
                self.num_jogadores += 1
                jogador_id = f"p{self.num_jogadores}"
                
                self.estado_global[jogador_id] = {
                    "pos_x": 100 * self.num_jogadores, #Para nascer em posições de 100 em 100
                    "pos_y": 500, #Para nascer no chão
                    "hp": 100,
                    "cor": self.cores[self.num_jogadores - 1]
                }
                return jogador_id
            return None

    def remover_jogador(self, jogador_id):
        with self.lock:
            if jogador_id in self.estado_global:
                del self.estado_global[jogador_id]

    def mover_jogador(self, jogador_id, acoes):
        with self.lock:
            if jogador_id in self.estado_global:
                vel = 6
                jog = self.estado_global[jogador_id]
                
                if "direita" in acoes: 
                    jog["pos_x"] += vel
                if "esquerda" in acoes: 
                    jog["pos_x"] -= vel
                if "saltar" in acoes and jog["pos_y"] >= 500: 
                    for i in range(10):
                        jog["pos_y"] -= vel
                elif jog["pos_y"] < 500: 
                    jog["pos_y"] += vel
                
                if jog["pos_y"] > 500: 
                    jog["pos_y"] = 500

    def get_estado(self):
        with self.lock:
            return self.estado_global.copy()