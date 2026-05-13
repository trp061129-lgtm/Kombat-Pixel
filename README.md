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

### Estrutura do Projeto

O repositório está organizado de forma modular para separar claramente as responsabilidades de rede, lógica computacional e gráficos:

* **`mapa.py`**: O ficheiro central de arquitetura. Define as constantes físicas, dimensões das plataformas e tamanho normalizado dos lutadores, garantindo que o Cliente e o Servidor partilham a mesma "verdade" espacial.
* **`/config.py`** (ou `constantes.py`): Parâmetros de conexão (IP, Porta) e códigos do protocolo de rede (ex: `JOIN_OP`, `SYNC_OP`, `INPUT_OP`).

* **`/servidor/`**:
  * `maquina.py`: O ponto de entrada principal. Efetua o *bind* da porta TCP e gere a aceitação de novas conexões.
  * `dados.py`: O "Motor" do jogo. Gere o estado global, aplica a física newtoniana (`vel_y`), processa os combates e o *cooldown* de ataques. Protegido por `threading.Lock()`.
  * `processo_cliente.py`: Instância de Thread que recebe e processa as teclas premidas por um cliente específico.
  * `broadcast_emissor.py`: Thread que envia continuamente a "fotografia" do estado do jogo para todos os clientes a 50 *frames* por segundo.

* **`/cliente/`**:
  * `interface.py`: O controlador do *Main Loop*. Trata da captura de teclado e renderização via PyGame.
  * `gerenciador_estado.py`: Classe de encapsulamento que protege os dados recebidos da rede e os fornece de forma segura (*Thread-safe*) ao motor gráfico.
  * `broadcast_receiver.py`: *Daemon Thread* responsável por intercetar os pacotes JSON do servidor e enviá-los para o Gerenciador de Estado.
  * `stickman.py`: Classe responsável pela lógica de desenho vetorial do personagem, braço de ataque dinâmico, barra de HP e interface de Vidas.

---

### Instruções de Execução

**1. Inicializar o Servidor:**
O ambiente anfitrião deve iniciar o módulo de serviço executando o comando na raiz do projeto:
`python -m servidor`

**2. Conectar um Cliente:**
Cada jogador deve inicializar o seu módulo executando o seguinte comando noutra instância de terminal (ou noutro PC na mesma rede):
`python -m cliente`

A inicialização do PyGame decorrerá imediatamente após o *Handshake* TCP.

**Controlos em Jogo:**
* **A / D** ou **Setas (Esquerda / Direita):** Deslocação horizontal.
* **W** ou **Seta (Cima):** Impulso vertical (Salto fluido).
* **ESPAÇO:** Ataque Corpo-a-Corpo (Soco).
* **Botão (X) da janela:** Encerramento seguro da ligação (`QUIT_OP`).

---

### Próximos Passos e Otimizações Planeadas

Graças à base robusta de física e rede, o sistema está pronto para as seguintes expansões:

* **Animações Baseadas em Sprites:** Substituir os retângulos vetoriais do PyGame por *spritesheets* animadas (correr, saltar, atacar, sofrer dano).
* **Diversidade de Ataques e Projéteis:** Implementar novos *inputs* (ex: Ataque Forte vs Ataque Rápido) e entidades independentes no servidor (ex: bolas de fogo).
* **Efeitos Sonoros (Áudio):** Adicionar *feedback* sonoro na interface do cliente (PyGame Mixer) sempre que uma variável de estado (como levar dano ou perder uma vida) for alterada.
