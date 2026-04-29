import servidor
import threading
import time
import json
from typing import Dict

class ThreadBroadcast(threading.Thread):
    def __init__(self, lista_clientes, dados, intervalo: float = 0.02):
        super().__init__(daemon=True)
        self.lista_clientes = lista_clientes
        self.dados = dados
        self.intervalo = intervalo
        self.running = True

    def send_int(self, connection, value: int, n_bytes: int) -> None:
        connection.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def send_object(self, connection, obj):
        data = json.dumps(obj).encode('utf-8')
        size = len(data)
        self.send_int(connection, size, servidor.INT_SIZE)
        connection.send(data)

    def broadcast_object(self, obj: Dict) -> None:
        with self.lista_clientes._lock:
            for address, conn in list(self.lista_clientes._clientes.items()):
                try:
                    # Envia o comando SYNC_OP antes do pacote de dados
                    conn.send(servidor.SYNC_OP.encode('utf-8'))
                    self.send_object(conn, obj)
                except Exception:
                    pass

    def run(self):
        print("ThreadBroadcast ativa a 50 FPS")
        while self.running:
            try:
                time.sleep(self.intervalo)
                estado_atual = {"estado": self.dados.get_estado()}
                self.broadcast_object(estado_atual)
            except Exception as e:
                print(f"Erro no broadcast: {e}")