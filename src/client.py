"""
Cliente CLI básico para el chat TCP.

Uso: python client.py [host] [port]
"""

import socket
import sys
import threading


def receive_messages(sock: socket.socket) -> None:
    """Hilo que imprime mensajes recibidos del servidor."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nDesconectado del servidor.")
                break
            print(data.decode("utf-8"), end="")
        except OSError:
            break


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    nickname = input("Nickname: ").strip() or "anon"
    sock.sendall(nickname.encode("utf-8"))

    listener = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    listener.start()

    print(f"Conectado como {nickname}. Escribe tus mensajes (Ctrl+C para salir):\n")
    try:
        while True:
            line = input()
            sock.sendall((line + "\n").encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo...")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
