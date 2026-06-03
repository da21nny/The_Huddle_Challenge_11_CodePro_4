import time
from tests.conftest import make_client, recv_all
from src.server import clients, clients_lock

# ============================================================================
# PRUEBAS DE DESCONEXION - Manejo de desconexiones inesperadas y errores
# ============================================================================
# Valida que el servidor maneja correctamente la desconexion de clientes
# sin bloquearse o causar errores, manteniendo otros clientes activos.

# --- SECCION: Desconexion Abrupta ---
# Pruebas de desconexion de uno o mas clientes y recuperacion del servidor
def test_server_keeps_running(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    time.sleep(0.1)

    # Alice se desconecta abruptamente
    client1.close()
    time.sleep(0.2)

    # Un nuevo cliente debe poder conectarse
    client3 = make_client(host, port, "Carol")
    time.sleep(0.1)

    recv_all(client2, timeout=0.1)

    # Carol envía un mensaje
    client3.sendall(b"Hola\n")
    time.sleep(0.1)

    bob_data = recv_all(client2)
    assert "[Carol]: Hola" in bob_data

    client2.close()
    client3.close()

def test_others_receive_disconnect_notification(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    time.sleep(0.1)

    recv_all(client2, timeout=0.1)

    # Alice se desconecta abruptamente
    client1.close()
    time.sleep(0.2)

    bob_data = recv_all(client2)
    assert "** Alice ha salido del chat **" in bob_data

    client2.close()

def test_clients_dict_updates(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    time.sleep(0.1)

    with clients_lock:
        assert len(clients) == 2

    # Alice se desconecta
    client1.close()
    time.sleep(0.2)

    with clients_lock:
        assert len(clients) == 1
        names = list(clients.values())
        assert "Bob" in names
        assert "Alice" not in names

    client2.close()

# --- SECCION: Desconexion Multiple ---
# Verifica el comportamiento cuando multiples clientes se desconectan
# y el servidor continua funcionando
def test_three_of_five_disconnect(running_server):
    host, port = running_server
    connections = []
    for i in range(5):
        connections.append(make_client(host, port, f"User{i}"))
    time.sleep(0.1)

    with clients_lock:
        assert len(clients) == 5

    # Desconecta los primeros tres
    for i in range(3):
        connections[i].close()
    time.sleep(0.3)

    with clients_lock:
        assert len(clients) == 2

    recv_all(connections[3], timeout=0.1)
    recv_all(connections[4], timeout=0.1)

    # User3 envía un mensaje
    connections[3].sendall(b"Hola\n")
    time.sleep(0.1)

    user4_data = recv_all(connections[4])
    assert "[User3]: Hola" in user4_data

    connections[3].close()
    connections[4].close()

def test_all_disconnect_server_survives(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    client3 = make_client(host, port, "Carol")
    time.sleep(0.1)

    with clients_lock:
        assert len(clients) == 3

    # Cierra todas las conexiones
    client1.close()
    client2.close()
    client3.close()
    time.sleep(0.3)

    with clients_lock:
        assert len(clients) == 0

    # Nuevo cliente se puede conectar
    new_client = make_client(host, port, "Dave")
    time.sleep(0.1)

    with clients_lock:
        assert len(clients) == 1
        assert list(clients.values()) == ["Dave"]

    new_client.close()

# --- SECCION: Desconexion Durante Envio ---
# Valida que los mensajes se envian correctamente incluso cuando
# otro cliente se desconecta al mismo tiempo
def test_message_while_another_disconnects(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    client3 = make_client(host, port, "Carol")
    time.sleep(0.1)

    recv_all(client3, timeout=0.1)

    # Bob se desconecta
    client2.close()
    
    # Alice envía un mensaje inmediatamente
    client1.sendall(b"Hola Carol\n")
    time.sleep(0.2)

    # Carol debe recibir el mensaje
    carol_data = recv_all(client3)
    assert "[Alice]: Hola Carol" in carol_data

    client1.close()
    client3.close()

