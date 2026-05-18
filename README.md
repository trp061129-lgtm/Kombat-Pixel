# Stickman Arena

**Stickman Arena** é um jogo de luta *multiplayer* em tempo real (estilo *Platform Fighter*), com arquitetura Cliente-Servidor, desenvolvido inteiramente em Python. 
Ao contrário de jogos por turnos, esta aplicação utiliza um motor de física customizado e comunicação via Sockets TCP de alta frequência para permitir que até 4 jogadores partilhem a mesma arena em simultâneo, com combates fluidos a 60 FPS.

O projeto foca-se numa gestão rigorosa de concorrência (*Threads*) e memória partilhada para garantir que o Servidor mantém a **autoridade absoluta** sobre o estado do jogo (física, colisões e dano), enquanto os Clientes executam a renderização visual através da biblioteca PyGame.

### Membros do Grupo
* Rafael Dias - 2024110297
* Tomás Pacheco - 2024111792

---

### Principais Funcionalidades

* **Arquitetura Cliente-Servidor Autoritária:** Um servidor centralizado (*headless*) processa toda a lógica espacial, gravidade e colisões. Os clientes operam como terminais visuais, empacotando *inputs* e desenhando o estado ditado pelo servidor.
* **Motor de Física Fluida e Plataformas:** Implementação de gravidade contínua, saltos em arco (parábolas baseadas em velocidade vertical) e um sistema de **Chão Dinâmico** que permite colisões semi-sólidas (*One-way platforms*) em múltiplos andares.
* **Sistema de Combate e *Knockback*:** Deteção de *hitboxes* baseada na direção e distância. Ataques bem-sucedidos aplicam dano e forças físicas de *Knockback* (empurrão horizontal e projeção vertical) no adversário.
* **Gestão de Partida (*Stocks*):** Sistema competitivo baseado em 3 Vidas (*Stocks*). Inclui *respawn* automático com queda do céu e deteção de condições de Vitória e Derrota.
* **Otimização de Rede e *State Management*:** Agrupamento de comandos num único pacote de ação (`INPUT_OP`) para evitar congestionamento TCP, e filtragem de pacotes (*DTOs*) no servidor para poupar largura de banda.

---

### Arquitetura de Rede e Concorrência (Threads)

O desempenho e a fluidez do **Stickman Arena** assentam numa separação estrita de tarefas. Para garantir que o motor gráfico não "congela" à espera de dados da rede, o sistema tira partido de *Multithreading* e *Locks* (exclusão mútua) para evitar *Race Conditions*.

**Fluxo de Comunicação Contínua:**
1. **Input:** O Cliente capta as teclas premidas pelo jogador e envia um pacote de ação de tamanho fixo para o Servidor.
2. **Processamento:** O Servidor valida o movimento, aplica as leis da física (gravidade e colisões) e regista alterações no Dicionário de Estado Global.
3. **Broadcast:** O Servidor serializa o Estado Global (em formato JSON) e envia esta "fotografia" do mapa para todos os clientes em simultâneo (~50 vezes por segundo).
4. **Renderização:** O Cliente recebe a "fotografia", atualiza o seu Gestor de Estado interno e a Máquina de Estados desenha a *sprite* correta no ecrã.

**Ecossistema de Threads:**
* **No Servidor:**
  * **Thread Principal (`maquina.py`):** Dedicada exclusivamente a manter o `socket.accept()` aberto, aguardando e validando a conexão de novos jogadores.
  * **Threads de Cliente (`processo_cliente.py`):** Criada uma por cada jogador conectado. O seu único trabalho é ficar à escuta (`recv`) dos pacotes de movimento daquele jogador em específico.
  * **Thread Emissora (`broadcast_emissor.py`):** Opera em ciclo contínuo (com *sleeps* de 0.02s). Usa um `threading.Lock()` para ler o Estado Global de forma segura, empacota os dados e emite para todos os *sockets* clientes ativos.

* **No Cliente:**
  * **Thread Principal (`interface.py`):** Gere o ciclo de vida do PyGame, roda a 60 FPS ininterruptos, capta eventos de teclado e desenha as imagens no ecrã com base nos dados mais recentes que tem na memória.
  * **Thread Recetora (`broadcast_receiver.py`):** *Daemon Thread* que opera em pano de fundo à escuta da rede. Quando um novo pacote JSON do servidor chega, valida-o e entrega-o ao `gerenciador_estado.py` protegido por um *Lock*, garantindo uma transição de *frames* perfeitamente segura.

---

### Estrutura do Projeto

O repositório está organizado de forma modular para separar claramente as responsabilidades:

* **`mapa.py`**: Ficheiro central de arquitetura. Define as constantes físicas e dimensões das plataformas, garantindo que o Cliente e o Servidor partilham a mesma "verdade" espacial.
* **`__init__.py`**: Parâmetros de conexão (IP, Porta) e códigos do protocolo de rede.

* **`/servidor/`**:
  * `maquina.py`: Inicializador do servidor.
  * `dados.py`: O "Motor" lógico. Gere o estado global e aplica a física newtoniana e *cooldowns*. Protegido por `threading.Lock()`.
  * `processo_cliente.py`: Instância de processamento individual por *socket* de jogador.
  * `broadcast_emissor.py`: Emissor de pacotes de estado JSON de alta frequência.

* **`/cliente/`**:
  * `interface.py`: Controlador do *Main Loop* e renderização PyGame.
  * `gerenciador_estado.py`: Classe de encapsulamento seguro (*Thread-safe*) dos dados da rede.
  * `broadcast_receiver.py`: Intercetor assíncrono de mensagens do servidor.
  * `stickman.py`: Máquina de Estados visual do personagem (animações *Idle*, *Run*, *Jump*, *Attack*), *hitboxes* visuais e sistema de *Palette Swapping* (cores baseadas no ID).

---

### Instruções de Execução

**1. Inicializar o Servidor:**
O ambiente anfitrião deve iniciar o módulo de serviço executando o comando na raiz do projeto:
`python -m servidor`

**2. Conectar um Cliente:**
Cada jogador deve inicializar o seu módulo executando o seguinte comando noutra instância de terminal (ou noutro PC na mesma rede local):
`python -m cliente`

A inicialização do PyGame decorrerá imediatamente após o *Handshake* TCP.

**Controlos em Jogo:**
* **A / D** ou **Setas (Esquerda / Direita):** Deslocação horizontal.
* **W** ou **Seta (Cima):** Impulso vertical (Salto fluido).
* **ESPAÇO:** Ataque Corpo-a-Corpo (Soco animado).
* **Botão (X) da janela:** Encerramento seguro da ligação via Sockets (`QUIT_OP`).
