"""
Unit tests — isolated functions using mocks.

We test the server functions WITHOUT starting a real server.
We use MagicMock to simulate sockets.

Covers: check_message, broadcast, remove_client.
"""

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


# ===================================================================
# Tests for check_message
# ===================================================================

class TestCheckMessage:
    """Positive and negative cases for check_message."""

    # --- Positive cases (happy path) ---

    def test_valid_message(self):
        """A normal message should be accepted."""
        ok, reason = check_message("Hola mundo")
        assert ok is True
        assert reason == ""

    def test_message_exactly_at_limit(self):
        """A message with exactly 500 characters is valid."""
        ok, reason = check_message("a" * MAX_MESSAGE_LENGTH)
        assert ok is True

    def test_message_with_special_characters(self):
        """Emojis and symbols are allowed."""
        ok, _ = check_message("¡Hola! 😊 @#$%")
        assert ok is True

    # --- Negative cases ---

    def test_empty_message(self):
        """An empty message should be rejected."""
        ok, reason = check_message("")
        assert ok is False
        assert "vacio" in reason

    def test_message_only_spaces(self):
        """A message of only spaces counts as empty."""
        ok, reason = check_message("   ")
        assert ok is False

    def test_message_is_none(self):
        """Passing None should also be rejected."""
        ok, reason = check_message(None)
        assert ok is False

    def test_message_too_long(self):
        """A message longer than 500 characters is rejected."""
        ok, reason = check_message("a" * (MAX_MESSAGE_LENGTH + 1))
        assert ok is False
        assert "excede" in reason


# ===================================================================
# Tests for broadcast
# ===================================================================

class TestBroadcast:
    """Tests for broadcast using mock sockets."""

    def test_send_to_all_except_sender(self):
        """The sender should not receive their own message."""
        sender = MagicMock(spec=socket.socket)
        receiver1 = MagicMock(spec=socket.socket)
        receiver2 = MagicMock(spec=socket.socket)

        with clients_lock:
            clients[sender] = "Alice"
            clients[receiver1] = "Bob"
            clients[receiver2] = "Carol"

        broadcast("Hola", sender=sender)

        # Sender does not receive
        sender.sendall.assert_not_called()
        # Others do receive
        receiver1.sendall.assert_called_once_with(b"Hola\n")
        receiver2.sendall.assert_called_once_with(b"Hola\n")

    def test_broadcast_without_sender_sends_to_all(self):
        """If there is no sender, everyone receives the message."""
        receiver = MagicMock(spec=socket.socket)

        with clients_lock:
            clients[receiver] = "Bob"

        broadcast("Aviso del sistema", sender=None)

        receiver.sendall.assert_called_once_with(b"Aviso del sistema\n")

    def test_broken_socket_does_not_crash(self):
        """If a socket fails, broadcast should not crash."""
        good = MagicMock(spec=socket.socket)
        bad = MagicMock(spec=socket.socket)
        bad.sendall.side_effect = OSError("broken pipe")

        with clients_lock:
            clients[good] = "Good"
            clients[bad] = "Bad"

        # This should not raise an exception
        broadcast("test", sender=None)

        # 'good' receives 2 calls: the original broadcast +
        # the notification that 'Bad' left the chat
        assert good.sendall.call_count == 2

    def test_broadcast_without_clients(self):
        """Should not crash with empty clients list."""
        broadcast("nada", sender=None)  # does not raise exception


# ===================================================================
# Tests for remove_client
# ===================================================================

class TestRemoveClient:
    """Tests for remove_client."""

    def test_remove_from_clients_dict(self):
        """The client should be removed from the active clients dict."""
        mock_sock = MagicMock(spec=socket.socket)
        with clients_lock:
            clients[mock_sock] = "TestUser"

        with clients_lock:
            remove_client(mock_sock)

        assert mock_sock not in clients

    def test_close_socket(self):
        """The socket connection should be closed."""
        mock_sock = MagicMock(spec=socket.socket)
        with clients_lock:
            clients[mock_sock] = "TestUser"

        with clients_lock:
            remove_client(mock_sock)

        mock_sock.close.assert_called_once()

    def test_nonexistent_client_does_not_crash(self):
        """Removing a client that does not exist should not raise an error."""
        mock_sock = MagicMock(spec=socket.socket)
        with clients_lock:
            remove_client(mock_sock)
        # If we get here, no exception was raised ✓
