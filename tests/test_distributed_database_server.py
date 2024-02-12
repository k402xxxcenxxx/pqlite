from __future__ import annotations

import socket
import threading

import pytest

from pqlite.server import DistributedDatabaseServer


@pytest.fixture(scope="module")
def server():
    # Setup: start the server in a background thread
    server_instance = DistributedDatabaseServer(
        "localhost", 0
    )  # Use port 0 to allow the OS to pick an available port
    server_thread = threading.Thread(target=server_instance.start, daemon=True)
    server_thread.start()
    yield server_instance
    # No teardown needed due to daemon=True


def test_server_accepts_connections(server):
    """Test that the server accepts connections on the specified port."""
    host, port = (
        server.server_socket.getsockname()
    )  # Retrieve the port assigned by the OS
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        connection_result = sock.connect_ex((host, port))
        assert connection_result == 0, "Server should accept connections"
