from __future__ import annotations

import threading

import pytest

from pqlite.client import DistributedDatabaseClient
from pqlite.server import DistributedDatabaseServer


@pytest.fixture(scope="module")
def server():
    server_instance = DistributedDatabaseServer("localhost", 0, "test.db")
    server_thread = threading.Thread(target=server_instance.start, daemon=True)
    server_thread.start()
    yield server_instance.host, server_instance.port


def test_client_sends_and_receives_message(server):
    host, port = server
    client = DistributedDatabaseClient(host, port)
    response = client.send_message(
        "db_ops:SELECT name FROM sqlite_master WHERE type='table'"
    )
    assert (
        response == "Success: []"
    ), "Client should receive an empty list response"
    response = client.send_message(
        "db_ops:CREATE TABLE movie(title, year, score)"
    )
    assert (
        response == "Success: -1"
    ), "Client should receive a create success response"
    response = client.send_message("db_ops:BAD COMMAND")
    assert (
        response == 'Error: near "BAD": syntax error'
    ), "Client should receive an error response"
