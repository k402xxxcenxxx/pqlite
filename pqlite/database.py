from __future__ import annotations

import sqlite3


class Database:
    def __init__(self, db_file):
        """
        Initializes the database connection.

        :param db_file: The filename of the SQLite database.
        """
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def execute(self, sql, params=None):
        """
        Executes an arbitrary SQL command.

        :param sql: The SQL command to execute.
        :param params: Optional parameters for the SQL command.
        :return: The result of the execution, if any.
        """
        if params is None:
            params = []
        self.cursor.execute(sql, params)
        if sql.strip().upper().startswith("SELECT"):
            return self.cursor.fetchall()
        else:
            self.connection.commit()
            return self.cursor.rowcount

    def close(self):
        """
        Closes the database connection.
        """
        self.connection.close()
