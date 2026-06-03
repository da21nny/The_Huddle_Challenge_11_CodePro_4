import threading
import time

from tests.conftest import make_client, recv_all

# ============================================================================
# PRUEBAS DE INTEGRACION - Validar interaccion entre multiples componentes
# ============================================================================
# Las pruebas de integracion verifican que diferentes modulos funcionan
# correctamente juntos: servidor, clientes, mensajes y comunicacion.

# --- SECCION: Multiples Conexiones ---
# Valida que varios clientes pueden conectarse y comunicarse simultaneamente
def test_two_clients_connect(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    client1.close()
    client2.close()

def test_message_reaches_other_client(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    time.sleep(0.1)

    recv_all(client1, timeout=0.1)
    recv_all(client2, timeout=0.1)

    # Alice envía un mensaje
    client1.sendall(b"Hola a todos\n")
    time.sleep(0.1)

    # Bob recibe el mensaje
    data = recv_all(client2)
    assert "[Alice]: Hola a todos" in data

    client1.close()
    client2.close()

def test_broadcast_to_three_clients(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    client3 = make_client(host, port, "Carol")
    time.sleep(0.1)

    recv_all(client1, timeout=0.1)
    recv_all(client2, timeout=0.1)
    recv_all(client3, timeout=0.1)

    # Alice envía un mensaje
    client1.sendall(b"Hola a todos\n")
    time.sleep(0.1)

    # Bob y Carol reciben el mensaje
    assert "[Alice]: Hola a todos" in recv_all(client2)
    assert "[Alice]: Hola a todos" in recv_all(client3)

    client1.close()
    client2.close()
    client3.close()

# --- SECCION: Mensajes Simultaneos ---
# Verifica que los mensajes se reciben correctamente cuando se envian en paralelo
# y que se mantiene el orden de llegada
def test_simultaneous_messages_without_loss(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    time.sleep(0.1)

    recv_all(client1, timeout=0.1)
    recv_all(client2, timeout=0.1)

    # Función para enviar mensajes en paralelo
    def send_messages(sock, prefix):
        for i in range(5):
            sock.sendall(f"{prefix}-{i}\n".encode())
            time.sleep(0.01)

    thread1 = threading.Thread(target=send_messages, args=(client1, "A"))
    thread2 = threading.Thread(target=send_messages, args=(client2, "B"))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    time.sleep(0.3)

    # Verifica que se recibieron todos los mensajes
    data_client1 = recv_all(client1)
    data_client2 = recv_all(client2)
    
    for i in range(5):
        assert f"B-{i}" in data_client1
        assert f"A-{i}" in data_client2

    client1.close()
    client2.close()

def test_message_order(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    client2 = make_client(host, port, "Bob")
    time.sleep(0.1)

    recv_all(client2, timeout=0.1)

    # Alice envía 10 mensajes numerados
    for i in range(10):
        client1.sendall(f"msg-{i}\n".encode())
        time.sleep(0.01)
    time.sleep(0.2)

    data = recv_all(client2)
    lines = [line for line in data.strip().split("\n") if "msg-" in line]

    # Extrae los números y verifica que están en orden
    numbers = []
    for line in lines:
        for part in line.split("msg-"):
            if part and part[0].isdigit():
                numbers.append(int(part[0]))

    assert numbers == sorted(numbers)

    client1.close()
    client2.close()

# --- SECCION: Validacion de Mensajes ---
# Verifica que el servidor rechaza mensajes invalidos (vacios o muy largos)
# como parte de la integracion del sistema de validacion
def test_empty_message_rejected(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    time.sleep(0.1)

    recv_all(client1, timeout=0.1)

    # Envía un mensaje vacío
    client1.sendall(b"\n")
    time.sleep(0.1)

    # Debe recibir un error
    data = recv_all(client1)
    assert "[ERROR]" in data

    client1.close()

def test_long_message_rejected(running_server):
    host, port = running_server
    client1 = make_client(host, port, "Alice")
    time.sleep(0.1)

    recv_all(client1, timeout=0.1)

    # Envía un mensaje muy largo
    message = "x" * 501 + "\n"
    client1.sendall(message.encode())
    time.sleep(0.1)

    # Debe recibir un error
    data = recv_all(client1)
    assert "[ERROR]" in data

    client1.close()

