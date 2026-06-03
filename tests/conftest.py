"""
Fixtures compartidas para todos los tests.

Este archivo se ejecuta automáticamente antes de cada test.
Prepara el servidor de prueba y funciones auxiliares.
"""

import socket
import threading
import time

import pytest

from src.server import accept_loop, clients, clients_lock, start_server


# -------------------------------------------------------
# Fixture: limpiar la agenda antes y después de cada test
# -------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_clients():
    """Limpia el registro de clientes antes y después de cada test.

    'autouse=True' significa que se ejecuta SOLA, sin necesidad
    de pasarla como parámetro al test.
    """
    # ANTES del test: limpiar
    with clients_lock:
        clients.clear()

    yield  # --- aquí se ejecuta el test ---

    # DESPUÉS del test: cerrar sockets y limpiar
    with clients_lock:
        for sock in list(clients):
            try:
                sock.close()
            except OSError:
                pass
        clients.clear()


# -------------------------------------------------------
# Fixture: levantar un servidor de prueba
# -------------------------------------------------------

@pytest.fixture()
def running_server():
    """Levanta un servidor real en un puerto libre.

    Retorna (host, port) para que los tests se conecten.
    Al terminar el test, cierra el servidor automáticamente.
    """
    # Crear servidor con port=0 (el SO elige un puerto libre)
    server_sock = start_server("127.0.0.1", 0)
    host, port = server_sock.getsockname()

    # Lanzar el loop de aceptar conexiones en un hilo aparte
    thread = threading.Thread(target=accept_loop, args=(server_sock,), daemon=True)
    thread.start()

    yield host, port  # --- entregar al test ---

    # Cerrar el servidor al terminar
    server_sock.close()
    time.sleep(0.1)  # dar tiempo a que los hilos daemon terminen


# -------------------------------------------------------
# Función auxiliar: crear un cliente de prueba
# -------------------------------------------------------

def make_client(host, port, nickname):
    """Crea un socket cliente, se conecta y envía el nickname."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(nickname.encode("utf-8"))
    time.sleep(0.05)  # dar tiempo al servidor a registrar
    return sock


# -------------------------------------------------------
# Función auxiliar: leer todo lo que llegó por el socket
# -------------------------------------------------------

def recv_all(sock, timeout=0.3):
    """Lee todo lo disponible en el socket con un tiempo límite."""
    sock.settimeout(timeout)
    chunks = []
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data.decode("utf-8"))
    except socket.timeout:
        pass  # se agotó el tiempo, ya leímos todo
    return "".join(chunks)
