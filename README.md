# Stickman Arena

**Stickman Arena** é um jogo de luta multiplayer em tempo real, com arquitetura Cliente-Servidor, desenvolvido inteiramente em Python. 
Ao contrário de jogos por turnos, esta aplicação utiliza um motor de física simples e comunicação via Sockets TCP de alta frequência para permitir que vários jogadores partilhem a mesma arena em simultâneo de forma fluida.

O projeto foca-se numa gestão rigorosa de concorrência (Threads) e memória partilhada para garantir que o Servidor mantém a autoridade sobre o estado do jogo enquanto os Clientes renderizam a ação a 60 FPS através da biblioteca PyGame.

### Membros do Grupo
* Rafael Dias - Número
* Tomás Pacheco - Número

---

### Principais Funcionalidades

* **Arquitetura Cliente-Servidor Autoritária:** Um servidor centralizado (headless) que processa toda a matemática, gravidade e colisões. Os clientes atuam apenas como "terminais burros", enviando *inputs* (teclas) e desenhando o que o servidor lhes diz.
* **Multiplayer em Tempo Real (Até 4 Jogadores):** Capacidade de suportar múltiplas conexões em simultâneo através de *Multithreading*.
* **Sincronização Assíncrona:** Separação total entre a leitura de rede e a renderização gráfica, impedindo que o jogo "congele" em caso de latência na internet.
* **Física e Gravidade:** Implementação de um motor lógico de saltos, limites de mapa (chão) e movimento contínuo no lado do servidor.
* **Interface Gráfica PyGame:** Renderização de personagens (`Stickman`), barras de vida (HP) e cores dinâmicas atribuídas a cada jogador.

---

### Estrutura do Projeto

O repositório está organizado de forma modular para separar claramente as responsabilidades da rede e da lógica visual:

* **`/config.py`** (ou `__init__.py`): Ficheiro global de configuração (IP, Porta, e protocolos do jogo como `JOIN_OP`, `SYNC_OP`, `MOVE_OP`).

* **`/servidor/`**: Contém toda a lógica de processamento central.
  * `maquina.py`: O ponto de entrada do servidor. Fica à escuta na porta TCP e aceita novas conexões.
  * `dados.py`: O "Cofre" do jogo. Guarda as posições (X,Y) e o HP de todos os jogadores. Protegido por `threading.Lock()` para evitar colisões de memória (*Race Conditions*).
  * `processo_cliente.py`: A Thread dedicada a ouvir os comandos (teclas) de um jogador específico.
  * `broadcast_emissor.py`: O "Câmara" do servidor. Uma Thread dedicada a enviar o estado do mapa para todos os clientes a 50 frames por segundo.

* **`/cliente/`**: A aplicação do jogador.
  * `interface.py`: O motor do jogo local. Trata do ciclo de vida do PyGame, eventos de teclado e renderização do cenário.
  * `broadcast_receiver.py`: A "Antena" do cliente. Uma Thread em *background* que ouve as atualizações do servidor e as injeta na memória partilhada do PyGame.
  * `stickman.py`: Classe visual responsável por desenhar o boneco e a barra de vida nas coordenadas corretas.

---

### Funcionalidades das Threads (Concorrência)

O verdadeiro motor deste jogo assenta na sua arquitetura de três tipos principais de *Threads*, garantindo que a comunicação nunca é bloqueante:

1. **`ProcessaCliente` (Servidor):**
   * **Função:** Atua como um Assistente Pessoal para cada jogador. Lê os comandos de movimento enviados pela rede e atualiza a base de dados central de forma segura.
   * **Iniciada em:** `maquina.py`, sempre que a função `.accept()` deteta uma nova conexão TCP. Podem existir até 4 a correr em simultâneo.

2. **`ThreadBroadcast` (Servidor):**
   * **Função:** Opera de forma independente dos *inputs* dos jogadores. O seu único papel é tirar uma "fotografia" ao estado atual da arena a cada 0.02 segundos e enviá-la para todos os clientes ativos.
   * **Iniciada em:** `maquina.py`, sendo lançada apenas uma vez no arranque do servidor.

3. **`BroadcastReceiver` (Cliente):**
   * **Função:** É uma *Daemon Thread* que liberta o motor gráfico (PyGame) de ter de esperar por mensagens da internet. Lê os pacotes JSON de posições enviados pelo servidor e atualiza o dicionário de renderização gráfica em tempo real.
   * **Iniciada em:** `interface.py`, logo após o "aperto de mão" inicial com o servidor ser concluído com sucesso.

---

### Como Jogar

**1. Arrancar o Servidor:**
Primeiro, o administrador deve ligar a arena executando o ficheiro principal do servidor no terminal:
`python -m servidor`

**2. Entrar na Arena:**
Cada jogador abre um terminal novo e executa:
`python -m cliente`
A janela do PyGame abrir-se-á imediatamente com a cor atribuída ao seu jogador.

**Controlos em Jogo:**
* **Setas (Esquerda / Direita) ou Teclas A e D:** Mover o personagem horizontalmente.
* **Seta (Cima) ou Tecla W:** Saltar.
* **Botão (X) da janela:** O cliente envia automaticamente um sinal de desconexão limpa (`QUIT_OP`) e o personagem desaparece do ecrã dos restantes jogadores.

---

### Próximos Passos e Futuras Implementações

O projeto já possui uma base de rede incrivelmente robusta. O futuro foca-se na expansão das mecânicas de *Gameplay*:

* **Sistema de Combate:** Implementação da leitura da tecla de Ataque (Soco) e do protocolo `ATK_OP`, com deteção de colisão de *Hitboxes* calculada no servidor para subtrair Vida (HP).
* **Animações Gráficas:** Substituir os retângulos sólidos de cor por *Sprites* (imagens) de personagens a correr e a saltar.
* **Menus Iniciais:** Um ecrã de início no PyGame antes de entrar na arena, permitindo inserir um "Nome/Nickname" em vez de usar os IDs genéricos (`p1`, `p2`).
* **Design de Níveis (Plataformas):** Adicionar uma estrutura de plataformas ao dicionário do Servidor, permitindo aos jogadores saltar entre diferentes alturas na arena.
