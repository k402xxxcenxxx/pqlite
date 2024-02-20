from __future__ import annotations
from random import choice

import socket
import threading

import pytest

from pqlite.server import DistributedDatabaseServer
from pqlite.client import DistributedDatabaseClient


@pytest.fixture(scope="module")
def testing_pairs():

    def testing_pair(id):
        server_instance = DistributedDatabaseServer("localhost", 0, f"test_{id}.db")
        server_thread = threading.Thread(target=server_instance.start, daemon=True)
        server_thread.start()

        host, port = server_instance.server_socket.getsockname()
        client_instance = DistributedDatabaseClient(host, port)

        return {"server": server_instance, "client": client_instance}
    
    testing_pair_instances = [testing_pair(i) for i in range(3)]
    yield testing_pair_instances

def test_server_execution_consistency(testing_pairs):
    # randomly pick one to create table
    pair = choice(testing_pairs)
    response = pair["client"].send_message("CREATE TABLE movie(title, year, score)")
    assert (
        response == "Success: -1"
    ), "Client should receive a create success response"

    # make sure every one have this table
    for testing_pair in testing_pairs:
        response = testing_pair["client"].send_message("SELECT name FROM sqlite_master")
        assert (
            response == "Success: [('movie',)]"
        ), "Client should receive a created database"
        