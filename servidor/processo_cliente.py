import threading
import servidor
import json

class ProcessaCliente(threading.Thread):
    def __init__(self, connection, address, dados, lista_clientes):
        super().__init__()
        self.connection = connection
        self.address = address
        self.dados = dados
        self.lista_clientes = lista_clientes
        self.meu_id = None

    def receive_str(self, n_bytes: int) -> str:
        return self.connection.recv(n_bytes).decode('utf-8')
        
    def receive_int(self, n_bytes: int) -> int:
        return int.from_bytes(self.connection.recv(n_bytes), byteorder='big')
        
    def send_int(self, value: int, n_bytes: int):
        self.connection.sendall(value.to_bytes(n_bytes, byteorder='big'))
        
    def send_str(self, value: str):
        self.connection.sendall(value.encode('utf-8'))
        
    def send_object(self, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_int(len(data), servidor.INT_SIZE)
        self.connection.sendall(data)
        
    def receive_object(self):
        size = self.receive_int(servidor.INT_SIZE)
        data = self.connection.recv(size)
        return json.loads(data.decode('utf-8'))
    # -------------------------------------------------------------

    def run(self):
        print(self.address, "Thread iniciada (Jogador)")
        self.lista_clientes.adicionar(self.address, self.connection)
        
        ativo = True
        while ativo:
            try:
                request_type = self.receive_str(servidor.COMMAND_SIZE)
                
                if request_type == servidor.JOIN_OP:
                    self.meu_id = self.dados.adicionar_jogador(self.address)
                    # Responde ao cliente com o ID que lhe foi atribuído
                    self.send_object({"id": self.meu_id})
                    print(f"[{self.address}] Registado como {self.meu_id}")

                elif request_type == servidor.MOVE_OP:
                    # Recebe a lista de teclas premidas (ex: ["direita", "saltar"])
                    acoes = self.receive_object()
                    if self.meu_id:
                        self.dados.mover_jogador(self.meu_id, acoes)

                elif request_type == servidor.QUIT_OP or not request_type:
                    ativo = False
                    
            except Exception as e:
                print(f"[{self.address}] Desconectado: {e}")
                ativo = False

        # Limpeza quando o jogador fecha a janela do jogo
        if self.meu_id:
            self.dados.remover_jogador(self.meu_id)
        self.lista_clientes.remover(self.address)
        self.connection.close()
        print(self.address, "Thread terminada")