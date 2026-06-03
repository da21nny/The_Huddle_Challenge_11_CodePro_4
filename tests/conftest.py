"""
Fixtures compartidas para todos los tests.
"""

import socket
import threading
import time

import pytest

from src.server import accept_loop, clients, clients_lock, start_server


@pytest.fixture(autouse=True)
def _clear_clients():
    """Limpia el registro global de clientes antes y después de cada test."""
    with clients_lock:
        clients.clear()
    yield
    with clients_lock:
        for sock in list(clients):
            try:
                sock.close()
            except OSError:
                pass
        clients.clear()


@pytest.fixture()
def running_server():
    """Levanta un servidor en un puerto libre y lo cierra al terminar.

    Retorna (host, port) para que los tests se conecten.
    """
    server_sock = start_server("127.0.0.1", 0)
    host, port = server_sock.getsockname()

    thread = threading.Thread(target=accept_loop, args=(server_sock,), daemon=True)
    thread.start()

    yield host, port

    server_sock.close()
    # Dar tiempo a que los hilos daemon terminen
    time.sleep(0.1)


def make_client(host: str, port: int, nickname: str) -> socket.socket:
    """Crea un socket cliente, se conecta y envía el nickname."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(nickname.encode("utf-8"))
    time.sleep(0.05)  # Dar tiempo al servidor a registrar
    return sock


def recv_all(sock: socket.socket, timeout: float = 0.3) -> str:
    """Lee todo lo disponible en el socket con un timeout."""
    sock.settimeout(timeout)
    chunks = []
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data.decode("utf-8"))
    except socket.timeout:
        pass
    return "".join(chunks)
