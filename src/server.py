import socket
import threading

MAX_MESSAGE_LENGTH = 500
BUFFER_SIZE = 1024

clients = {}
clients_lock = threading.RLock()

def check_message(message):
    if not message or not message.strip():
        return False, "El mensaje no puede estar vacio."
    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"El mensaje excede los {MAX_MESSAGE_LENGTH} caracteres."
    return True, ""


def broadcast(message, sender=None):
    data = (message + "\n").encode("utf-8")
    with clients_lock:
        for client_sock in list(clients):
            if client_sock is sender:
                continue
            try:
                client_sock.sendall(data)
            except OSError:
                remove_client(client_sock)

def remove_client(client_sock):
    nickname = clients.pop(client_sock, None)
    try:
        client_sock.close()
    except OSError:
        pass
    if nickname:
        broadcast(f"** {nickname} ha salido del chat **")

def handle_client(client_sock, addr):
    buffer = ""
    try:
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

        while True:
            data = client_sock.recv(BUFFER_SIZE)
            if not data:
                break

            buffer += data.decode("utf-8")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                ok, reason = check_message(line)
                if not ok:
                    try:
                        error_msg = f"[ERROR] {reason}\n"
                        client_sock.sendall(error_msg.encode("utf-8"))
                    except OSError:
                        pass
                    continue

                with clients_lock:
                    nick = clients.get(client_sock, nickname)
                broadcast(f"[{nick}]: {line}", sender=client_sock)

    except OSError:
        pass
    finally:
        with clients_lock:
            remove_client(client_sock)

def start_server(host="127.0.0.1", port=0):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen()
    return server_sock

def accept_loop(server_sock):
    while True:
        try:
            client_sock, addr = server_sock.accept()
        except OSError:
            break
        thread = threading.Thread(
            target=handle_client,
            args=(client_sock, addr),
            daemon=True,
        )
        thread.start()

if __name__ == "__main__":
    srv = start_server("127.0.0.1", 5000)
    print("[+] Servidor escuchando en 127.0.0.1:5000")
    try:
        accept_loop(srv)
    except KeyboardInterrupt:
        print("\n[!] Servidor detenido.")
    finally:
        srv.close()
