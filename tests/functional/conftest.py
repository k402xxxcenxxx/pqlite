import random
import pytest

from itertools import permutations
import threading

from pqlite.server import DistributedDatabaseServer
from pqlite.client import DistributedDatabaseClient


class TestOperation:
    movie_list = [
        "Titanic" "The Shawshank Redemption",
        "The Godfather",
        "Inception",
        "Pulp Fiction",
        "The Dark Knight",
        "Forrest Gump",
        "Fight Club",
        "The Matrix",
        "Star Wars: Episode IV - A New Hope",
        "Jurassic Park",
        "The Lord of the Rings: The Fellowship of the Ring",
        "Avatar",
        "The Avengers",
        "Harry Potter and the Sorcerer's Stone",
        "Toy Story",
        "The Lion King",
        "Gladiator",
        "Forrest Gump",
        "The Silence of the Lambs",
    ]

    def __init__(self):
        self.transaction = self.gen_transaction()

    def gen_transaction(self):
        pass


class CreateTableOperation(TestOperation):

    def gen_transaction(self):
        return """
            CREATE TABLE movie(
                id INTEGER PRIMARY KEY,
                title TEXT UNIQUE,
                year INTEGER, score REAL)
        """


class DeleteOperation(TestOperation):

    def gen_transaction(self):
        movie = random.choice(self.movie_list)
        return f"DELETE FROM movie WHERE title = '{movie}'"


class InsertOperation(TestOperation):

    def gen_transaction(self):
        movie = random.choice(self.movie_list)
        year = random.choice(range(1900, 2024))
        score = round(random.uniform(0, 10), 1)

        return f"""
            INSERT INTO movie (title, year, score)
            VALUES ('{movie}', {year}, {score})
            ON CONFLICT (title) DO UPDATE SET score = {score}
            """


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

    # Clean up
    for p in pairs:
        p["server"].close()


@pytest.fixture(scope="module")
def testing_cases(request):
    n_cases = request.param

    cases = [CreateTableOperation()]
    cases.extend(
        [
            random.choices(
                [InsertOperation(), DeleteOperation()], weights=[0.8, 0.2]
            )[0]
            for _ in range(n_cases - 1)
        ]
    )
    return cases
