"""
Pruebas de integración — servidor real + múltiples clientes.

Valida: conexión de múltiples clientes, broadcast correcto,
mensajes simultáneos sin pérdida ni duplicación, orden de mensajes,
rechazo de mensajes inválidos.
"""

import socket
import threading
import time

from tests.conftest import make_client, recv_all


class TestMultiplesConexiones:
    """Múltiples clientes conectados al servidor."""

    def test_dos_clientes_se_conectan(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")

        # Bob debería recibir notificación de que Alice se unió
        # (depende del timing, pero ambos deben conectarse sin error)
        c1.close()
        c2.close()

    def test_mensaje_llega_a_otros_clientes(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        # Limpiar buffers de notificaciones de conexión
        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)

        # Alice envía un mensaje
        c1.sendall(b"Hola a todos\n")
        time.sleep(0.1)

        # Bob debe recibirlo
        data = recv_all(c2)
        assert "[Alice]: Hola a todos" in data

        # Alice NO debe recibir su propio mensaje
        data_alice = recv_all(c1, timeout=0.1)
        assert "[Alice]: Hola a todos" not in data_alice

        c1.close()
        c2.close()

    def test_broadcast_a_tres_clientes(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        c3 = make_client(host, port, "Carol")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)
        recv_all(c3, timeout=0.1)

        c1.sendall(b"Mensaje de Alice\n")
        time.sleep(0.1)

        data_bob = recv_all(c2)
        data_carol = recv_all(c3)

        assert "[Alice]: Mensaje de Alice" in data_bob
        assert "[Alice]: Mensaje de Alice" in data_carol

        c1.close()
        c2.close()
        c3.close()


class TestMensajesSimultaneos:
    """Varios clientes envían y reciben al mismo tiempo."""

    def test_mensajes_simultaneos_sin_perdida(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)

        n_mensajes = 5

        def enviar(sock, prefix):
            for i in range(n_mensajes):
                sock.sendall(f"{prefix}-{i}\n".encode())
                time.sleep(0.01)

        t1 = threading.Thread(target=enviar, args=(c1, "A"))
        t2 = threading.Thread(target=enviar, args=(c2, "B"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        time.sleep(0.3)

        # c1 debe recibir todos los mensajes de Bob
        data_c1 = recv_all(c1)
        for i in range(n_mensajes):
            assert f"B-{i}" in data_c1

        # c2 debe recibir todos los mensajes de Alice
        data_c2 = recv_all(c2)
        for i in range(n_mensajes):
            assert f"A-{i}" in data_c2

        c1.close()
        c2.close()

    def test_sin_duplicacion(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)

        c1.sendall(b"UNICO\n")
        time.sleep(0.1)

        data = recv_all(c2)
        # El mensaje debe aparecer exactamente una vez
        assert data.count("UNICO") == 1

        c1.close()
        c2.close()

    def test_orden_de_mensajes(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        recv_all(c2, timeout=0.1)

        # Alice envía mensajes numerados en orden
        for i in range(10):
            c1.sendall(f"msg-{i}\n".encode())
            time.sleep(0.01)
        time.sleep(0.2)

        data = recv_all(c2)
        lines = [l for l in data.strip().split("\n") if "msg-" in l]

        # Extraer números y verificar orden
        nums = []
        for line in lines:
            for part in line.split("msg-"):
                if part and part[0].isdigit():
                    nums.append(int(part[0]))

        assert nums == sorted(nums), f"Mensajes fuera de orden: {nums}"

        c1.close()
        c2.close()


class TestMensajesInvalidos:
    """El servidor rechaza entradas inválidas."""

    def test_mensaje_vacio_rechazado(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)

        # Enviar mensaje vacío (solo newline)
        c1.sendall(b"\n")
        time.sleep(0.1)

        data = recv_all(c1)
        assert "[ERROR]" in data

        c1.close()

    def test_mensaje_largo_rechazado(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)

        msg = "x" * 501 + "\n"
        c1.sendall(msg.encode())
        time.sleep(0.1)

        data = recv_all(c1)
        assert "[ERROR]" in data

        c1.close()
