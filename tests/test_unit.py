import socket
from unittest.mock import MagicMock

from src.server import (
    MAX_MESSAGE_LENGTH,
    broadcast,
    clients,
    clients_lock,
    remove_client,
    check_message,
)

# Pruebas unitarias para check_message
def test_valid_message():
    ok, reason = check_message("Hola mundo")
    assert ok is True
    assert reason == ""

def test_message_at_exact_limit():
    ok, reason = check_message("a" * MAX_MESSAGE_LENGTH)
    assert ok is True

def test_empty_message():
    ok, reason = check_message("")
    assert ok is False
    assert "vacio" in reason

def test_message_only_spaces():
    ok, reason = check_message("   ")
    assert ok is False

def test_none_message():
    ok, reason = check_message(None)
    assert ok is False

def test_message_too_long():
    ok, reason = check_message("a" * (MAX_MESSAGE_LENGTH + 1))
    assert ok is False
    assert "excede" in reason

# Pruebas unitarias para broadcast
def test_broadcast_sends_to_others_not_sender():
    sender = MagicMock(spec=socket.socket)
    receiver1 = MagicMock(spec=socket.socket)
    receiver2 = MagicMock(spec=socket.socket)

    with clients_lock:
        clients[sender] = "Alice"
        clients[receiver1] = "Bob"
        clients[receiver2] = "Carol"

    broadcast("Hola", sender=sender)

    sender.sendall.assert_not_called()
    receiver1.sendall.assert_called_once_with(b"Hola\n")
    receiver2.sendall.assert_called_once_with(b"Hola\n")

def test_broadcast_without_sender():
    receiver = MagicMock(spec=socket.socket)

    with clients_lock:
        clients[receiver] = "Bob"

    broadcast("Aviso del sistema", sender=None)

    receiver.sendall.assert_called_once_with(b"Aviso del sistema\n")

def test_broadcast_broken_socket_no_crash():
    good_socket = MagicMock(spec=socket.socket)
    bad_socket = MagicMock(spec=socket.socket)
    bad_socket.sendall.side_effect = OSError("broken pipe")

    with clients_lock:
        clients[good_socket] = "Good"
        clients[bad_socket] = "Bad"

    broadcast("test", sender=None)
    assert good_socket.sendall.call_count >= 1

# Pruebas unitarias para remove_client
def test_remove_client_from_dict():
    client_socket = MagicMock(spec=socket.socket)
    with clients_lock:
        clients[client_socket] = "TestUser"

    with clients_lock:
        remove_client(client_socket)

    assert client_socket not in clients

def test_close_socket():
    client_socket = MagicMock(spec=socket.socket)
    with clients_lock:
        clients[client_socket] = "TestUser"

    with clients_lock:
        remove_client(client_socket)

    client_socket.close.assert_called_once()

def test_remove_nonexistent_client_no_crash():
    client_socket = MagicMock(spec=socket.socket)
    with clients_lock:
        remove_client(client_socket)
