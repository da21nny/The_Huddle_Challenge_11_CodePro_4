"""
Pruebas unitarias — funciones críticas aisladas.

Cubre: validate_message, broadcast, remove_client.
Usa unittest.mock para aislar dependencias de red.
"""

import socket
from unittest.mock import MagicMock, patch

from src.server import (
    MAX_MSG_LENGTH,
    broadcast,
    clients,
    clients_lock,
    remove_client,
    validate_message,
)


# ===================================================================
# validate_message
# ===================================================================

class TestValidateMessage:
    """Casos positivos y negativos para validate_message."""

    def test_mensaje_valido(self):
        ok, reason = validate_message("Hola mundo")
        assert ok is True
        assert reason == ""

    def test_mensaje_vacio(self):
        ok, reason = validate_message("")
        assert ok is False
        assert "vacío" in reason

    def test_mensaje_solo_espacios(self):
        ok, reason = validate_message("   ")
        assert ok is False
        assert "vacío" in reason

    def test_mensaje_none(self):
        ok, reason = validate_message(None)
        assert ok is False

    def test_mensaje_demasiado_largo(self):
        ok, reason = validate_message("a" * (MAX_MSG_LENGTH + 1))
        assert ok is False
        assert "excede" in reason

    def test_mensaje_en_limite(self):
        ok, reason = validate_message("a" * MAX_MSG_LENGTH)
        assert ok is True

    def test_mensaje_con_caracteres_especiales(self):
        ok, _ = validate_message("¡Hola! 😊 @#$%")
        assert ok is True


# ===================================================================
# broadcast
# ===================================================================

class TestBroadcast:
    """Pruebas de broadcast con sockets mock."""

    def test_broadcast_envia_a_todos_menos_sender(self):
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

    def test_broadcast_sin_sender(self):
        receiver = MagicMock(spec=socket.socket)

        with clients_lock:
            clients[receiver] = "Bob"

        broadcast("Aviso del sistema", sender=None)

        receiver.sendall.assert_called_once_with(b"Aviso del sistema\n")

    def test_broadcast_socket_fallido_no_crashea(self):
        good = MagicMock(spec=socket.socket)
        bad = MagicMock(spec=socket.socket)
        bad.sendall.side_effect = OSError("broken pipe")

        with clients_lock:
            clients[good] = "Good"
            clients[bad] = "Bad"

        # No debe lanzar excepción
        broadcast("test", sender=None)

        # good recibe 2 llamadas: el broadcast original + notificación
        # de desconexión de "Bad" al ser removido por socket roto.
        assert good.sendall.call_count == 2

    def test_broadcast_sin_clientes(self):
        # No debe lanzar excepción con dict vacío
        broadcast("nada", sender=None)


# ===================================================================
# remove_client
# ===================================================================

class TestRemoveClient:
    """Pruebas de remove_client."""

    def test_remueve_cliente_del_registro(self):
        mock_sock = MagicMock(spec=socket.socket)
        with clients_lock:
            clients[mock_sock] = "TestUser"

        with clients_lock:
            remove_client(mock_sock)

        assert mock_sock not in clients

    def test_cierra_socket(self):
        mock_sock = MagicMock(spec=socket.socket)
        with clients_lock:
            clients[mock_sock] = "TestUser"

        with clients_lock:
            remove_client(mock_sock)

        mock_sock.close.assert_called_once()

    def test_remover_cliente_inexistente_no_crashea(self):
        mock_sock = MagicMock(spec=socket.socket)
        with clients_lock:
            remove_client(mock_sock)
        # No debe lanzar excepción
