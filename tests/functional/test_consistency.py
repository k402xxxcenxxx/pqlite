from __future__ import annotations
from random import choice
import threading

import pytest


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


@pytest.mark.parametrize("testing_cases", [10], indirect=True)
def test_server_execution_consistency2(testing_pairs, testing_cases):
    def execute_transaction(client, transaction):
        client.send_message(f"sync:db_ops:{transaction}")

    # List to store threads
    threads = []

    # randomly pick one to do the operation
    for case in testing_cases:
        pair = choice(testing_pairs)
        # Create a thread for each transaction and start it
        thread = threading.Thread(
            target=execute_transaction, args=(pair["client"], case.transaction)
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # every node should have the same output
    final_results = []
    for testing_pair in testing_pairs:
        final_results.append(
            testing_pair["client"].send_message(
                "db_ops:SELECT title, year, score FROM movie"
            )
        )

    assert all(
        r == final_results[0] for r in final_results
    ), "All result should be the same"
