from __future__ import annotations

import sqlite3


class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)

    def execute_query(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()

    def close(self):
        self.conn.close()
