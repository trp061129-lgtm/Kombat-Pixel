import threading
from typing import Dict, Tuple
import socket

class ListaClientes:
    def __init__(self):
        self._clientes: Dict[Tuple[str, int], socket.socket] = {}
        self._lock = threading.Lock()
        self._nr_clientes = 0



    def adicionar(self, address: Tuple[str, int], connection: socket.socket) -> None:
        with self._lock:
            self._clientes[address] = connection
            self._nr_clientes += 1
            print("Client ", address," added to dictionary!")
            print("Nr. de clientes:",self._nr_clientes)

    def remover(self, addr: Tuple[str, int]) -> None:
        with self._lock:
            if addr in self._clientes:
                del self._clientes[addr]
                self._nr_clientes -= 1

    def obter_lista(self) -> Dict[Tuple[str, int], socket.socket]:
        with self._lock:
            return self._clientes.copy()

    def obter_nr_clientes(self) -> int:
        return self._nr_clientes
