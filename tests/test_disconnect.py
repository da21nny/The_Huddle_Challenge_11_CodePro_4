"""
Pruebas de desconexión — resiliencia del servidor.

Valida: desconexión abrupta, desconexiones múltiples simultáneas,
servidor sigue funcional tras desconexiones, actualización de
lista de usuarios activos.
"""

import socket
import time

from src.server import clients, clients_lock
from tests.conftest import make_client, recv_all


class TestDesconexionAbrupta:
    """Un cliente se desconecta de golpe."""

    def test_servidor_sigue_tras_desconexion(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)

        # Alice se desconecta de golpe
        c1.close()
        time.sleep(0.2)

        # Bob sigue pudiendo enviar y recibir
        c3 = make_client(host, port, "Carol")
        time.sleep(0.1)
        recv_all(c2, timeout=0.1)
        recv_all(c3, timeout=0.1)

        c3.sendall(b"Sigo aqui\n")
        time.sleep(0.1)

        data = recv_all(c2)
        assert "Sigo aqui" in data

        c2.close()
        c3.close()

    def test_notificacion_desconexion(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        recv_all(c2, timeout=0.1)

        # Alice se desconecta
        c1.close()
        time.sleep(0.2)

        data = recv_all(c2)
        assert "Alice" in data and "salido" in data

        c2.close()

    def test_lista_usuarios_actualizada(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        # Verificar que hay 2 clientes
        with clients_lock:
            assert len(clients) == 2

        c1.close()
        time.sleep(0.2)

        # Verificar que Alice fue removida
        with clients_lock:
            nicknames = list(clients.values())
        assert "Alice" not in nicknames
        assert "Bob" in nicknames

        c2.close()


class TestDesconexionesMultiples:
    """Varios clientes se desconectan al mismo tiempo."""

    def test_multiples_desconexiones_simultaneas(self, running_server):
        host, port = running_server
        clientes = [make_client(host, port, f"User{i}") for i in range(5)]
        time.sleep(0.1)

        # Desconectar 3 de golpe
        for c in clientes[:3]:
            c.close()
        time.sleep(0.3)

        # Los 2 restantes deben seguir activos
        with clients_lock:
            assert len(clients) == 2

        # Verificar que pueden seguir comunicándose
        recv_all(clientes[3], timeout=0.1)
        recv_all(clientes[4], timeout=0.1)

        clientes[3].sendall(b"Seguimos vivos\n")
        time.sleep(0.1)

        data = recv_all(clientes[4])
        assert "Seguimos vivos" in data

        clientes[3].close()
        clientes[4].close()

    def test_todos_se_desconectan(self, running_server):
        host, port = running_server
        clientes = [make_client(host, port, f"User{i}") for i in range(3)]
        time.sleep(0.1)

        for c in clientes:
            c.close()
        time.sleep(0.3)

        with clients_lock:
            assert len(clients) == 0

        # El servidor sigue funcionando: se puede conectar alguien nuevo
        new_client = make_client(host, port, "NuevoUser")
        time.sleep(0.1)

        with clients_lock:
            assert len(clients) == 1

        new_client.close()


class TestDesconexionDuranteEnvio:
    """Un cliente se desconecta mientras otro envía mensajes."""

    def test_envio_durante_desconexion(self, running_server):
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        c3 = make_client(host, port, "Carol")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)
        recv_all(c3, timeout=0.1)

        # Bob se desconecta mientras Alice envía
        c2.close()
        time.sleep(0.05)
        c1.sendall(b"Mensaje post-desconexion\n")
        time.sleep(0.2)

        # Carol debe recibir el mensaje sin problemas
        data = recv_all(c3)
        assert "Mensaje post-desconexion" in data

        c1.close()
        c3.close()
