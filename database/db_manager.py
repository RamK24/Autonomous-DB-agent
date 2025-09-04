from contextlib import contextmanager
import sqlite3
from sqlite3 import Error
import os


class Database:

    def __init__(self, db_file: str):
        self.db_file = db_file
        current_dir = os.path.dirname(__file__)
        self.db_file = os.path.join(current_dir, db_file)

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def execute_script(conn, script_file):
        """
        Execute a SQL script from a file.
        :param conn: Connection object
        :param script_file: Path to the .sql file
        """
        try:
            with open(script_file, 'r') as f:
                sql_script = f.read()
            c = conn.cursor()
            c.executescript(sql_script)
            print(f"Successfully executed script from {script_file}")
        except Error as e:
            print(f"Error executing script {script_file}: {e}")
        except FileNotFoundError:
            print(f"Error: The file {script_file} was not found.")

    @staticmethod
    def execute_query(conn, query, params=()):
        """
        Execute a single SQL query that modifies the database (INSERT, UPDATE, DELETE).
        :param conn: Connection object
        :param query: The SQL query to execute
        :param params: A tuple of parameters to pass to the SQL query
        :return: The last row id of the inserted row
        """
        try:
            c = conn.cursor()
            c.execute(query, params)
            return c.lastrowid
        except Error as e:
            print(f"Error executing query: {e}")
            return None

    @staticmethod
    def execute_view(conn, query, params=()):
        """
        Execute a single SQL query that modifies the database (VIEW).
        :param conn: Connection object
        :param query: The SQL query to execute
        :param params: A tuple of parameters to pass to the SQL query
        :return: The last row id of the inserted row
        """
        try:
            c = conn.cursor()
            c.execute(query, params)
            return c.fetchone()
        except Error as e:
            print(f"Error executing query: {e}")
            return None


