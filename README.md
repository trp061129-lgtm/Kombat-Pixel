# Stickman Arena

**Stickman Arena** é um jogo de luta multiplayer em tempo real, com arquitetura Cliente-Servidor, desenvolvido inteiramente em Python. 
Ao contrário de jogos por turnos, esta aplicação utiliza um motor de física e comunicação via Sockets TCP de alta frequência para permitir que vários jogadores partilhem a mesma arena em simultâneo de forma fluida.

O projeto foca-se numa gestão rigorosa de concorrência (Threads) e memória partilhada para garantir que o Servidor mantém a autoridade sobre o estado do jogo, enquanto os Clientes executam a renderização da ação a 60 FPS através da biblioteca PyGame.

### Membros do Grupo
* Rafael Dias - 2024110297
* Tomás Pacheco - 2024111792

---

### Principais Funcionalidades

* **Arquitetura Cliente-Servidor Autoritária:** Um servidor centralizado (headless) que processa toda a lógica espacial, gravidade e colisões. Os clientes operam como terminais de renderização passiva, submetendo comandos (*inputs*) e desenhando o estado ditado pelo servidor.
* **Multiplayer em Tempo Real (Até 4 Jogadores):** Capacidade de suportar múltiplas conexões em simultâneo através de concorrência baseada em *Multithreading*.
* **Sincronização Assíncrona:** Separação total entre as rotinas de I/O de rede e a renderização gráfica, prevenindo o bloqueio do motor de jogo em cenários de latência.
* **Física e Gravidade:** Implementação de um motor lógico de saltos, delimitação de mapa e movimento contínuo executado exclusivamente no lado do servidor.
* **Interface Gráfica PyGame:** Renderização de personagens (`Stickman`), barras de vida (HP) e cores dinâmicas atribuídas a cada jogador.

---

### Estrutura do Projeto

O repositório está organizado de forma modular para separar claramente as responsabilidades de comunicação em rede e da lógica computacional/visual:

* **`/config.py`** (ou `__init__.py`): Ficheiro global de configuração contendo os parâmetros de conexão (IP, Porta) e as constantes de protocolo de rede (ex: `JOIN_OP`, `SYNC_OP`, `MOVE_OP`).

* **`/servidor/`**: Contém a lógica de processamento central.
  * `maquina.py`: O ponto de entrada principal. Efetua o *bind* da porta TCP e gere a aceitação de novas conexões.
  * `dados.py`: O módulo de gestão do estado global da aplicação. Armazena as coordenadas espaciais (X,Y) e os atributos de todos os jogadores conectados. O acesso aos dados é protegido por exclusão mútua (`threading.Lock()`) para prevenir *Race Conditions*.
  * `processo_cliente.py`: Instância de Thread dedicada à receção e processamento de pacotes TCP de um cliente específico.
  * `broadcast_emissor.py`: Thread dedicada à transmissão contínua do estado da memória global para todos os nós clientes conectados, operando a 50 frames por segundo.

* **`/cliente/`**: A aplicação do utilizador final.
  * `interface.py`: O controlador do ciclo principal (*Main Loop*). Trata dos eventos do sistema operático, captura de teclado e renderização via PyGame.
  * `broadcast_receiver.py`: Rotina secundária em *background* responsável por intercetar os pacotes de estado enviados pelo servidor e atualizar a estrutura de dados partilhada no cliente.
  * `stickman.py`: Classe responsável pela lógica de desenho vetorial do personagem e interface associada.

---

### Arquitetura de Threads e Concorrência

O desempenho deste sistema assenta na paralelização de tarefas através de três tipos principais de *Threads*, garantindo que as chamadas de rede não bloqueiam a execução lógica:

1. **`ProcessaCliente` (Servidor):**
   * **Função:** Gere o ciclo de sessão de um jogador específico. Deserializa os comandos de movimento enviados pela rede e invoca os métodos de alteração de estado no módulo central de forma unicamente serializada.
   * **Iniciação:** Lançada em `maquina.py`, mediante o retorno de um novo *socket* pela função `.accept()`. Limitado a 4 instâncias simultâneas.

2. **`ThreadBroadcast` (Servidor):**
   * **Função:** Opera de forma assíncrona face aos *inputs* dos jogadores. É responsável por aceder rotineiramente ao estado da arena (a cada 0.02 segundos), serializar o dicionário em JSON e emitir o pacote em *broadcast* unicast para todos os *sockets* clientes ativos.
   * **Iniciação:** Lançada em `maquina.py` durante o processo de inicialização do servidor.

3. **`BroadcastReceiver` (Cliente):**
   * **Função:** *Daemon Thread* cuja finalidade é processar o fluxo de I/O de entrada. Ao realizar a leitura não-bloqueante na perspetiva da *Interface*, extrai a carga útil (*payload*) dos pacotes JSON do servidor e substitui os dados na memória do PyGame com as coordenadas mais recentes.
   * **Iniciação:** Lançada em `interface.py`, após o processo de *Handshake* e validação de ID.

---

### Instruções de Execução

**1. Inicializar o Servidor:**
O ambiente anfitrião deve iniciar o módulo de serviço executando o comando na raiz do projeto:
`python -m servidor`

**2. Conectar um Cliente:**
Cada jogador deve inicializar o seu módulo executando o seguinte comando noutra instância de terminal:
`python -m cliente`
A inicialização do PyGame decorrerá imediatamente após o estabelecimento da ligação TCP.

**Controlos em Jogo:**
* **Setas (Esquerda / Direita) ou Teclas A e D:** Deslocação horizontal.
* **Seta (Cima) ou Tecla W:** Impulso vertical (Salto).
* **Botão (X) da janela:** Transmite uma *flag* de terminação (`QUIT_OP`) permitindo o encerramento seguro da *socket* (graceful disconnect).

---

### Próximos Passos e Otimizações Planeadas

A infraestrutura de rede atual suporta expansão para sistemas mais complexos de simulação:

* **Sistema de Colisões e Combate:** Integração de *Hitboxes* processadas no lado do servidor mediante o comando de ataque (`ATK_OP`), resultando na dedução validada de pontos de vida.
* **Sistema de Animações Baseado em Sprites:** Mapeamento de matrizes visuais de acordo com o vetor de movimento do personagem, substituindo o *render* de primitivas gráficas atuais.
* **Topologia Espacial (Plataformas):** Adição de um sistema de polígonos estáticos ao dicionário do servidor para permitir o cálculo de colisões eixo-y em múltiplas elevações.
