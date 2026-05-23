# ==========================================
# CONFIGURAÇÕES DE REDE E PROTOCOLOS
# ==========================================
COMMAND_SIZE = 9
INT_SIZE = 8

JOIN_OP = "join_game"  # Cliente pede para entrar no jogo
SYNC_OP = "sync_data"  # Servidor envia o mapa atualizado
INPUT_OP = "send_keys" # Cliente envia as teclas que premiu 
QUIT_OP = "quit_game"  # Cliente fecha a janela e sai
STOP_OP = "stop_serv"  # Desligar o servidor

PORT = 35000
SERVER_ADDRESS = "localhost"

# ==========================================
# CONFIGURAÇÕES DA JANELA E GRÁFICOS
# ==========================================
LARGURA_JANELA = 800
ALTURA_JANELA = 600
FPS = 60

# ==========================================
# FÍSICA E MAPA 
# ==========================================
# --- PLATAFORMAS ---
PLATAFORMAS = [
    {"x": 0.10, "y": 0.70, "largura": 0.25, "altura": 0.02}, # Esquerda
    {"x": 0.65, "y": 0.70, "largura": 0.25, "altura": 0.02}, # Direita
    {"x": 0.35, "y": 0.45, "largura": 0.30, "altura": 0.02}  # Central 
]

# --- CHÃO ---
CHAO_Y = 0.85 

# --- DIMENSÕES DO LUTADOR ---
BONECO_LARGURA = 0.035 
BONECO_ALTURA = 0.12