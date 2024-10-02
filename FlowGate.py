import socket
import threading

ART = """ \033[94m
▄████  █    ████▄   ▄ ▄     ▄▀  ██     ▄▄▄▄▀ ▄███▄   
█▀   ▀ █    █   █  █   █  ▄▀    █ █ ▀▀▀ █    █▀   ▀  
█▀▀    █    █   █ █ ▄   █ █ ▀▄  █▄▄█    █    ██▄▄    
█      ███▄ ▀████ █  █  █ █   █ █  █   █     █▄   ▄▀ 
 █         ▀       █ █ █   ███     █  ▀      ▀███▀   
  ▀                 ▀ ▀           █                  
                                 ▀                   
\033[0m"""
COLOR = {"RED" : "[\033[91m-\033[0m]","GREEN" : "[\033[92m+\033[0m]","YELLOW" : "[\033[93mx\033[0m]"}

class TCPProxy:
    """Classe principal que gerencia a criação e execução do proxy TCP."""

    def __init__(self, local_host: str, local_port: int, remote_host: str, remote_port: int):
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port

    def start(self):
        """Inicia o proxy para escutar conexões de clientes e redirecionar o tráfego."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.local_host, self.local_port))
            server.listen(5)
            print(f"{COLOR["GREEN"]} Proxy escutando em {self.local_host}:{self.local_port} "
                  f"e redirecionando para {self.remote_host}:{self.remote_port}")

            while True:
                client_socket, addr = server.accept()
                print(f"[*] Conexão recebida de {addr[0]}:{addr[1]}")
                ClientHandler(client_socket, self.remote_host, self.remote_port).start()


class ClientHandler(threading.Thread):
    """Lida com o redirecionamento de tráfego entre o cliente e o servidor remoto."""

    def __init__(self, client_socket: socket.socket, remote_host: str, remote_port: int):
        super().__init__()
        self.client_socket = client_socket
        self.remote_host = remote_host
        self.remote_port = remote_port

    def run(self):
        """Estabelece a conexão com o servidor remoto e inicia o redirecionamento de tráfego."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as remote_socket:
                remote_socket.connect((self.remote_host, self.remote_port))
                print(f"[*] Conectado ao servidor remoto {self.remote_host}:{self.remote_port}")

                # Criação de threads para redirecionamento de tráfego
                forward_threads = [
                    TrafficForwarder(self.client_socket, remote_socket),
                    TrafficForwarder(remote_socket, self.client_socket)
                ]
                for thread in forward_threads:
                    thread.start()

                for thread in forward_threads:
                    thread.join()
        except Exception as e:
            print(f"[*] Erro ao conectar com o servidor remoto: {e}")
        finally:
            self.client_socket.close()


class TrafficForwarder(threading.Thread):
    """Redireciona o tráfego de dados entre o cliente e o servidor."""

    def __init__(self, source_socket: socket.socket, destination_socket: socket.socket):
        super().__init__()
        self.source_socket = source_socket
        self.destination_socket = destination_socket

    def run(self):
        """Executa a transferência de dados entre o source e destination sockets."""
        try:
            while data := self.source_socket.recv(4096):
                print(f"[*] Redirecionando {len(data)} bytes: {data}")
                self.destination_socket.sendall(data)
        except Exception as e:
            print(f"[*] Erro ao redirecionar dados: {e}")
        finally:
            self.source_socket.close()
            self.destination_socket.close()


if __name__ == "__main__":
    print(ART)
    # Parâmetros de configuração do Proxy
    LOCAL_HOST = "127.0.0.1"
    LOCAL_PORT = 9999
    REMOTE_HOST = "www.example.com"
    REMOTE_PORT = 80

    # Instancia e inicia o proxy TCP
    proxy = TCPProxy(LOCAL_HOST, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT)
    proxy.start()
