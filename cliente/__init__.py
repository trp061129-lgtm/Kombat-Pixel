COMMAND_SIZE = 9
INT_SIZE = 8

# Protocolos do Jogo 
JOIN_OP = "join_game"  #Cliente pede para entrar no jogo
SYNC_OP = "sync_data"  #Servidor envia o mapa atualizado
INPUT_OP = "send_keys"  #Cliente envia as teclas que premiu 
QUIT_OP = "quit_game"  #Cliente fecha a janela e sai
STOP_OP = "stop_serv"  #Desligar o servidor

PORT = 35000
SERVER_ADDRESS = "localhost"