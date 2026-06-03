"""
Integration tests — real server + multiple clients.

These tests stand up a real server and connect real clients
over TCP network. They verify that the chat works end-to-end.

Covers: multiple connections, broadcast, simultaneous messages,
no loss or duplication, order, and rejection of invalid messages.
"""

import threading
import time

from tests.conftest import make_client, recv_all


# ===================================================================
# Multiple connections
# ===================================================================

class TestMultipleConnections:
    """Multiple clients connecting to the server."""

    def test_two_clients_connect(self, running_server):
        """Two clients can connect without errors."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        # If we reach here without exceptions, both connected OK
        c1.close()
        c2.close()

    def test_message_reaches_other_client(self, running_server):
        """A message from Alice reaches Bob, but not Alice."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        # Clear connection notifications
        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)

        # Alice sends a message
        c1.sendall(b"Hola a todos\n")
        time.sleep(0.1)

        # Bob should receive it
        data = recv_all(c2)
        assert "[Alice]: Hola a todos" in data

        # Alice should NOT receive her own message
        data_alice = recv_all(c1, timeout=0.1)
        assert "[Alice]: Hola a todos" not in data_alice

        c1.close()
        c2.close()

    def test_broadcast_to_three_clients(self, running_server):
        """A message from Alice reaches both Bob and Carol."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        c3 = make_client(host, port, "Carol")
        time.sleep(0.1)

        # Clear mailboxes
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


# ===================================================================
# Simultaneous messages
# ===================================================================

class TestSimultaneousMessages:
    """Multiple clients sending and receiving at the same time."""

    def test_simultaneous_messages_without_loss(self, running_server):
        """5 messages from each side, none are lost."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        # Clear mailboxes
        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)

        n_messages = 5

        def send_messages(sock, prefix):
            """Sends numbered messages."""
            for i in range(n_messages):
                sock.sendall(f"{prefix}-{i}\n".encode())
                time.sleep(0.01)

        # Launch sends in parallel
        t1 = threading.Thread(target=send_messages, args=(c1, "A"))
        t2 = threading.Thread(target=send_messages, args=(c2, "B"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        time.sleep(0.3)

        # Alice should receive ALL messages from Bob
        data_c1 = recv_all(c1)
        for i in range(n_messages):
            assert f"B-{i}" in data_c1

        # Bob should receive ALL messages from Alice
        data_c2 = recv_all(c2)
        for i in range(n_messages):
            assert f"A-{i}" in data_c2

        c1.close()
        c2.close()

    def test_no_duplication(self, running_server):
        """A message sent once arrives exactly once."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)
        recv_all(c2, timeout=0.1)

        c1.sendall(b"UNICO\n")
        time.sleep(0.1)

        data = recv_all(c2)
        # Message should appear exactly ONCE
        assert data.count("UNICO") == 1

        c1.close()
        c2.close()

    def test_message_order(self, running_server):
        """Messages arrive in the order they were sent."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        c2 = make_client(host, port, "Bob")
        time.sleep(0.1)

        recv_all(c2, timeout=0.1)

        # Alice sends 10 numbered messages in order
        for i in range(10):
            c1.sendall(f"msg-{i}\n".encode())
            time.sleep(0.01)
        time.sleep(0.2)

        data = recv_all(c2)
        lines = [line for line in data.strip().split("\n") if "msg-" in line]

        # Extract numbers and verify they are in order
        nums = []
        for line in lines:
            for part in line.split("msg-"):
                if part and part[0].isdigit():
                    nums.append(int(part[0]))

        assert nums == sorted(nums), f"Messages out of order: {nums}"

        c1.close()
        c2.close()


# ===================================================================
# Invalid messages
# ===================================================================

class TestInvalidMessages:
    """The server rejects invalid messages."""

    def test_empty_message_rejected(self, running_server):
        """An empty message (only \\n) returns [ERROR]."""
        host, port = running_server
        c1 = make_client(host, port, "Alice")
        time.sleep(0.1)

        recv_all(c1, timeout=0.1)

        # Send only a newline (empty message)
        c1.sendall(b"\n")
        time.sleep(0.1)

        data = recv_all(c1)
        assert "[ERROR]" in data

        c1.close()

    def test_long_message_rejected(self, running_server):
        """A message longer than 500 characters returns [ERROR]."""
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
