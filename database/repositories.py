from sqlite3 import Error


class UserRepository:

    def __init__(self, db):
        self.db = db

    def insert_user(self, name: str):
        with self.db.connection() as conn:
            query = "INSERT INTO users (name) VALUES (?)"
            try:
                user_id = self.db.execute_query(conn, query, (name, ))
                return user_id
            except Error as e:
                return f'Failed with error {e}'


class TicketRepository:
    def __init__(self, db):
        self.db = db

    def insert_ticket(self, assignee_id: int, title: str):
        with self.db.connection() as conn:
            query = "INSERT INTO tickets(title, assignee_id) VALUES(?, ?)"
            try:
                ticket_id = self.db.execute_query(conn, query, (title, assignee_id, ))
                return ticket_id
            except Error as e:
                return f'Failed with error {e}'

    def view_ticket(self, ticket_id: int):
        with self.db.connection() as conn:
            query = """SELECT t.id as ticket_id, t.title as ticket_title, u.name as user_name, u.id as user_id
            FROM tickets t LEFT JOIN users u ON t.assignee_id = u.id
            WHERE t.id = ?
            """
            try:
                result = self.db.execute_view(conn, query, (ticket_id,))
                return result
            except Error as e:
                return f"failed with error {e}"

    def verify_user(self, id: int):
        with self.db.connection() as conn:
            query = """SELECT id from users WHERE id = ?
            """
            try:
                if self.db.execute_view(conn, query, (id,)):
                    return True
                else:
                    return False
            except Error as e:
                return False

    def verify_ticket(self, ticket_id):
        with self.db.connection() as conn:
            query = """SELECT id from tickets WHERE id = ?
            """
            try:
                if self.db.execute_view(conn, query, (ticket_id,)):
                    return True
                else:
                    return False
            except Error as e:
                return False









