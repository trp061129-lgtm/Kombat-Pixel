import threading

class GerenciadorEstado:
    def __init__(self):
        self.estado_atual = {}
        self.lock = threading.Lock() 

    def atualizar_estado(self, novo_estado):
        """Recebe o pacote do servidor e substitui o estado antigo pelo novo."""
        with self.lock:
            self.estado_atual.clear()
            self.estado_atual.update(novo_estado)

    def obter_estado(self):
        """Entrega uma cópia segura do estado para o Pygame desenhar."""
        with self.lock:
            return self.estado_atual.copy()