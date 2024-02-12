from __future__ import annotations

import threading

import pytest

from pqlite.client import DistributedDatabaseClient
from pqlite.server import DistributedDatabaseServer


@pytest.fixture(scope="module")
def server():
    server_instance = DistributedDatabaseServer("localhost", 0)
    server_thread = threading.Thread(target=server_instance.start, daemon=True)
    server_thread.start()
    yield server_instance.server_socket.getsockname()


def test_client_sends_and_receives_message(server):
    host, port = server
    client = DistributedDatabaseClient(host, port)
    response = client.send_message("Hello, server!")
    assert response == "ACK", "Client should receive an ACK response"
