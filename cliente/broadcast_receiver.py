import threading
import json
import cliente

class BroadcastReceiver(threading.Thread):
    def __init__(self, connection, estado_partilhado):  
        super().__init__(daemon=True)
        self.connection = connection
        self.estado_partilhado = estado_partilhado #Estado do jogo partilhado com a interface

    def receive_int(self, n_bytes: int) -> int:
        data = self.connection.recv(n_bytes)
        return int.from_bytes(data, byteorder='big', signed=True)

    def receive_object(self):
        size = self.receive_int(cliente.INT_SIZE)
        data = self.connection.recv(size)
        return json.loads(data.decode('utf-8'))

    def run(self):
        print("Receiver de broadcasts ativo (à escuta)...")
        while True:
            try:
                comando = self.connection.recv(cliente.COMMAND_SIZE).decode('utf-8')
                if comando == cliente.SYNC_OP:
                    
                    # Recebe um dicionário com as coordenadas e as vidas de todos os players
                    pacote = self.receive_object()
                    
                    # Atualiza o dicionário partilhado com as novas posições e vidas
                    self.estado_partilhado.clear()
                    self.estado_partilhado.update(pacote["estado"])
                    
            except Exception as e:
                print(f"Receiver desconectado: {e}")
                break