"""
Integration tests for client disconnects (abrupt, multiple, during send).
"""

import time
from tests.conftest import make_client, recv_all
from src.server import clients, clients_lock


class TestAbruptDisconnect:
    """Tests simulating a client disconnecting abruptly."""

    def test_server_keeps_running(self, running_server):
        """The server should continue to run even if a client leaves abruptly."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        # Alice disconnects abruptly
        c1.close()
        time.sleep(0.2)

        # A new client should still be able to connect and send messages
        c3 = make_client(host, port, "Carol")
        time.sleep(0.1)

        # Clear Bob's connection notifications
        recv_all(c2, timeout=0.1)

        c3.sendall(b"Hello from Carol\n")
        time.sleep(0.1)

        bob_mailbox = recv_all(c2)
        assert "[Carol]: Hello from Carol" in bob_mailbox

        c2.close()
        c3.close()

    def test_others_receive_disconnect_notification(self, running_server):
        """Other active clients should receive a message when someone disconnects."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        # Clear Bob's connection notifications
        recv_all(c2, timeout=0.1)

        # Alice disconnects abruptly
        c1.close()
        time.sleep(0.2)

        bob_mailbox = recv_all(c2)
        assert "** Alice ha salido del chat **" in bob_mailbox

        c2.close()

    def test_clients_dict_updates(self, running_server):
        """The active clients dictionary on the server should update correctly."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        with clients_lock:
            assert len(clients) == 2

        # Alice disconnects abruptly
        c1.close()
        time.sleep(0.2)

        with clients_lock:
            assert len(clients) == 1
            # Bob should be the only client left
            active_names = list(clients.values())
            assert "Bob" in active_names
            assert "Alice" not in active_names

        c2.close()


class TestMultipleDisconnects:
    """Tests simulating multiple clients disconnecting simultaneously."""

    def test_three_of_five_disconnect(self, running_server):
        """If 3 of 5 clients disconnect, the remaining 2 should still be able to chat."""
        host, port = running_server
        connections = []
        for i in range(5):
            connections.append(make_client(host, port, f"User{i}"))
        time.sleep(0.1)

        with clients_lock:
            assert len(clients) == 5

        # Disconnect first three clients abruptly
        for i in range(3):
            connections[i].close()
        time.sleep(0.3)

        with clients_lock:
            assert len(clients) == 2

        # Clear active clients' mailboxes
        recv_all(connections[3], timeout=0.1)
        recv_all(connections[4], timeout=0.1)

        # User3 sends a message to User4
        connections[3].sendall(b"Still here!\n")
        time.sleep(0.1)

        user4_mailbox = recv_all(connections[4])
        assert "[User3]: Still here!" in user4_mailbox

        connections[3].close()
        connections[4].close()

    def test_all_disconnect_server_survives(self, running_server):
        """The server should handle everyone leaving and accept new clients."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        c3 = make_client(host, port, "Carol")
        time.sleep(0.1)

        with clients_lock:
            assert len(clients) == 3

        # Close all active connections
        c1.close()
        c2.close()
        c3.close()
        time.sleep(0.3)

        with clients_lock:
            assert len(clients) == 0

        # Try connecting a new client
        c_new = make_client(host, port, "Dave")
        time.sleep(0.1)

        with clients_lock:
            assert len(clients) == 1
            assert list(clients.values()) == ["Dave"]

        c_new.close()


class TestDisconnectDuringSend:
    """Tests simulating client disconnection during message broadcasts."""

    def test_message_sent_while_another_disconnects(self, running_server):
        """Messages sent while a client disconnects should broadcast normally to others."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        c3 = make_client(host, port, "Carol")
        time.sleep(0.1)

        # Clear Carol's mailbox
        recv_all(c3, timeout=0.1)

        # Bob disconnects abruptly
        c2.close()
        
        # Alice sends a message immediately
        c1.sendall(b"Hello Carol!\n")
        time.sleep(0.2)

        # Carol should receive the message without issues
        carol_mailbox = recv_all(c3)
        assert "[Alice]: Hello Carol!" in carol_mailbox

        c1.close()
        c3.close()
