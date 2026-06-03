"""
Chat server TCP multi-hilo.

Protocolo:
  - Mensajes delimitados por '\\n'.
  - Primer mensaje del cliente = nickname.
  - Broadcast: "[nickname]: mensaje" a todos excepto al emisor.
  - Máximo 500 caracteres por mensaje.
"""

import socket
import threading

MAX_MSG_LENGTH = 500
BUFFER_SIZE = 1024

# Estado global del servidor
clients: dict[socket.socket, str] = {}
clients_lock = threading.RLock()


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------

def validate_message(msg: str) -> tuple[bool, str]:
    """Valida un mensaje de chat. Retorna (ok, razón)."""
    if not msg or not msg.strip():
        return False, "El mensaje no puede estar vacío."
    if len(msg) > MAX_MSG_LENGTH:
        return False, f"El mensaje excede los {MAX_MSG_LENGTH} caracteres."
    return True, ""


# ---------------------------------------------------------------------------
# Broadcast
# ---------------------------------------------------------------------------

def broadcast(message: str, sender: socket.socket | None = None) -> None:
    """Envía *message* a todos los clientes excepto *sender*."""
    data = (message + "\n").encode("utf-8")
    with clients_lock:
        for client_sock in list(clients):
            if client_sock is sender:
                continue
            try:
                client_sock.sendall(data)
            except OSError:
                # El socket ya no sirve; lo removemos silenciosamente.
                remove_client(client_sock)


def remove_client(client_sock: socket.socket) -> None:
    """Elimina un cliente del registro (debe llamarse con clients_lock)."""
    nickname = clients.pop(client_sock, None)
    try:
        client_sock.close()
    except OSError:
        pass
    if nickname:
        broadcast(f"** {nickname} ha salido del chat **")


# ---------------------------------------------------------------------------
# Manejo de cliente
# ---------------------------------------------------------------------------

def handle_client(client_sock: socket.socket, addr: tuple) -> None:
    """Gestiona la conexión de un cliente individual."""
    buffer = ""
    try:
        # Primer mensaje = nickname
        raw = client_sock.recv(BUFFER_SIZE)
        if not raw:
            client_sock.close()
            return
        nickname = raw.decode("utf-8").strip()
        if not nickname:
            nickname = f"anon-{addr[1]}"

        with clients_lock:
            clients[client_sock] = nickname

        broadcast(f"** {nickname} se ha unido al chat **", sender=client_sock)

        # Loop de mensajes
        while True:
            data = client_sock.recv(BUFFER_SIZE)
            if not data:
                break
            buffer += data.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                ok, reason = validate_message(line)
                if not ok:
                    error_msg = f"[ERROR] {reason}\n"
                    try:
                        client_sock.sendall(error_msg.encode("utf-8"))
                    except OSError:
                        pass
                    continue
                with clients_lock:
                    nick = clients.get(client_sock, nickname)
                broadcast(f"[{nick}]: {line}", sender=client_sock)

    except (ConnectionResetError, ConnectionAbortedError, OSError):
        pass
    finally:
        with clients_lock:
            remove_client(client_sock)


# ---------------------------------------------------------------------------
# Servidor principal
# ---------------------------------------------------------------------------

def start_server(host: str = "127.0.0.1", port: int = 0) -> socket.socket:
    """Arranca el servidor y retorna el socket (útil para testing).

    Si *port* es 0 el SO asigna un puerto libre automáticamente.
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()
    return server_sock


def accept_loop(server_sock: socket.socket) -> None:
    """Acepta conexiones entrantes y lanza un hilo por cliente."""
    while True:
        try:
            client_sock, addr = server_sock.accept()
        except OSError:
            break  # El socket se cerró → salimos.
        thread = threading.Thread(
            target=handle_client,
            args=(client_sock, addr),
            daemon=True,
        )
        thread.start()


if __name__ == "__main__":
    srv = start_server("127.0.0.1", 5000)
    print("Servidor escuchando en 127.0.0.1:5000")
    try:
        accept_loop(srv)
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        srv.close()
