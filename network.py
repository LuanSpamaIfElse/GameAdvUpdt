# network.py
import socket
import threading
import json
import time

class Network:
    """
    Classe base para manipulação de rede, lidando com o envio e recebimento de dados.
    """
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_id = None
        self.game_state = {}

    def _receive_data(self, connection):
        """Loop para receber dados continuamente de uma conexão."""
        buffer = ""
        while True:
            try:
                # Recebe dados em pedaços para lidar com mensagens grandes ou fragmentadas
                data_chunk = connection.recv(4096).decode('utf-8')
                if not data_chunk:
                    break  # Conexão fechada
                buffer += data_chunk

                # Processa mensagens completas de JSON (delimitadas por nova linha)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    try:
                        state = json.loads(message)
                        if "player_id" in state and self.player_id is None:
                            self.player_id = state["player_id"]
                            print(f"ID de jogador recebido do servidor: {self.player_id}")
                        elif "game_state" in state:
                            self.game_state = state["game_state"]
                    except json.JSONDecodeError:
                        print(f"Erro ao decodificar JSON: {message}")
            except ConnectionResetError:
                print("Conexão com o servidor perdida.")
                break
            except Exception as e:
                print(f"Erro ao receber dados: {e}")
                break
        connection.close()

    def send_data(self, data):
        """Envia dados para a conexão."""
        try:
            # Envia dados em formato JSON com um delimitador de nova linha
            self.socket.sendall((json.dumps(data) + '\n').encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError):
            print("Não foi possível enviar dados. A conexão pode ter sido perdida.")
        except Exception as e:
            print(f"Erro ao enviar dados: {e}")

class Server(Network):
    """
    Classe do Servidor (Host). Escuta por conexões e retransmite o estado do jogo.
    """
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = {}  # {connection: player_id}
        self.player_states = {} # {player_id: state}
        self.next_player_id = 0
        self.lock = threading.Lock()
        
        # O Host é sempre o jogador 0
        self.player_id = self.get_new_player_id()

    def get_new_player_id(self):
        player_id = self.next_player_id
        self.next_player_id += 1
        return player_id

    def _handle_client(self, connection, player_id):
        """Lida com a comunicação de um cliente específico."""
        print(f"Cliente {player_id} conectado de {connection.getpeername()}")
        # Envia ao novo cliente seu ID de jogador
        connection.sendall((json.dumps({"player_id": player_id}) + '\n').encode('utf-8'))
        
        buffer = ""
        while True:
            try:
                data_chunk = connection.recv(4096).decode('utf-8')
                if not data_chunk:
                    break
                buffer += data_chunk

                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    try:
                        player_data = json.loads(message)
                        with self.lock:
                            self.player_states[player_id] = player_data
                    except json.JSONDecodeError:
                        print(f"Erro ao decodificar JSON do cliente {player_id}: {message}")

            except (ConnectionResetError, ConnectionAbortedError):
                break
        
        # Limpeza quando o cliente desconecta
        print(f"Cliente {player_id} desconectado.")
        with self.lock:
            del self.clients[connection]
            if player_id in self.player_states:
                del self.player_states[player_id]
        connection.close()

    def _broadcast_state(self):
        """Envia o estado completo do jogo para todos os clientes."""
        while True:
            with self.lock:
                if not self.clients:
                    time.sleep(0.016) # Dorme um pouco se não houver clientes
                    continue
                
                # Prepara o estado do jogo para ser enviado
                message = json.dumps({"game_state": self.player_states}) + '\n'
                
                # Cria uma cópia da lista de clientes para evitar problemas de concorrência
                clients_copy = list(self.clients.keys())

            for conn in clients_copy:
                try:
                    conn.sendall(message.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError):
                    print("Erro ao transmitir para um cliente. Ele pode ter desconectado.")
            time.sleep(1 / 60) # Transmite aproximadamente a 60 FPS

    def start(self):
        """Inicia o servidor e os threads de comunicação."""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen()
            print(f"Servidor escutando em {self.host}:{self.port}")

            # Thread para transmitir o estado do jogo
            broadcast_thread = threading.Thread(target=self._broadcast_state, daemon=True)
            broadcast_thread.start()
            
            # Thread para aceitar novas conexões
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()

        except OSError as e:
            print(f"Erro ao iniciar o servidor: {e}. A porta pode já estar em uso.")
            # Você pode querer sair ou notificar o usuário aqui
            return False
        return True

    def _accept_connections(self):
        """Loop para aceitar novas conexões de clientes."""
        while True:
            try:
                connection, address = self.socket.accept()
                with self.lock:
                    player_id = self.get_new_player_id()
                    self.clients[connection] = player_id
                
                client_thread = threading.Thread(target=self._handle_client, args=(connection, player_id), daemon=True)
                client_thread.start()
            except Exception as e:
                print(f"Erro ao aceitar conexões: {e}")
                break

    def update_local_player_state(self, state):
        """O Host usa isso para atualizar seu próprio estado na lista."""
        with self.lock:
            self.player_states[self.player_id] = state

class Client(Network):
    """
    Classe do Cliente. Conecta-se a um servidor e envia/recebe o estado do jogo.
    """
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def connect(self):
        """Tenta conectar ao servidor."""
        try:
            self.socket.connect((self.host, self.port))
            # Inicia um thread para receber dados do servidor
            receive_thread = threading.Thread(target=self._receive_data, args=(self.socket,), daemon=True)
            receive_thread.start()
            print(f"Conectado ao servidor em {self.host}:{self.port}")
            return True
        except (ConnectionRefusedError, socket.gaierror, socket.timeout) as e:
            print(f"Falha ao conectar ao servidor: {e}")
            return False

    def send_data(self, data):
        """Envia os dados do jogador local para o servidor."""
        super().send_data(data)