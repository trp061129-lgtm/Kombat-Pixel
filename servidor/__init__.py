COMMAND_SIZE = 9
INT_SIZE = 8

# Protocolos do Jogo 
JOIN_OP = "join_game"  #Cliente pede para entrar no jogo
SYNC_OP = "sync_data"  #Servidor envia o mapa atualizado
MOVE_OP = "send_keys"  #Cliente envia as teclas que premiu de movimento
QUIT_OP = "quit_game"  #Cliente fecha a janela e sai
ATK_OP  = "atk_punch"  #Cliente envia as teclas que premiu de ataque
STOP_OP = "stop_serv"  #Desligar o servidor

PORT = 35000
SERVER_ADDRESS = "localhost"