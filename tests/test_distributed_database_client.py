from __future__ import annotations

import threading

import pytest

from pqlite.client import DistributedDatabaseClient
from pqlite.server import DistributedDatabaseServer


@pytest.fixture(scope="module")
def server():
    server_instance = DistributedDatabaseServer('localhost', 0)  # Again, let OS pick an available port
    server_thread = threading.Thread(target=server_instance.start, daemon=True)
    server_thread.start()
    yield server_instance.server_socket.getsockname()  # Pass server address for client tests
    # Server thread will be killed with the test process due to daemon=True

def test_client_sends_and_receives_message(server):
    """Test that the client can send a message to the server and receive a response."""
    host, port = server  # Unpack server address
    client = DistributedDatabaseClient(host, port)
    response = client.send_message("Hello, server!")
    assert response == "ACK", "Client should receive an ACK response"
