from __future__ import annotations
from random import choice

from itertools import permutations
import threading

import pytest

from pqlite.server import DistributedDatabaseServer
from pqlite.client import DistributedDatabaseClient


@pytest.fixture(scope="module")
def testing_pairs():

    def testing_pair(id):
        server_instance = DistributedDatabaseServer(
            "localhost", 0, f"test_{id}.db"
        )
        server_thread = threading.Thread(
            target=server_instance.start, daemon=True
        )
        server_thread.start()

        client_instance = DistributedDatabaseClient(
            server_instance.host, server_instance.port
        )

        return {"server": server_instance, "client": client_instance}

    # Create instances
    pairs = [testing_pair(i) for i in range(3)]

    # Group the instances to one cluster
    for p in permutations(range(3), 2):
        pairs[p[0]]["server"].add_node(
            pairs[p[1]]["server"].host, pairs[p[1]]["server"].port
        )

    yield pairs


def test_server_execution_consistency(testing_pairs):
    # randomly pick one to create table
    pair = choice(testing_pairs)
    response = pair["client"].send_message(
        "sync:db_ops:CREATE TABLE movie(title, year, score)"
    )
    assert (
        response == "Success: -1"
    ), "Client should receive a create success response"

    # make sure every one have this table
    for testing_pair in testing_pairs:
        response = testing_pair["client"].send_message(
            "db_ops:SELECT name FROM sqlite_master"
        )
        assert (
            response == "Success: [('movie',)]"
        ), "Client should receive a created database"
