from database.repositories import TicketRepository
from langchain_core.tools import tool
from database.db_manager import Database


db = Database('jira_ticketing.db')

ticket_obj = TicketRepository(db)

@tool
def create_ticket(assignee_id: int, title: str):
    """
    Create a new ticket and assign it to a user.
    :param assignee_id: The ID of the user to assign the ticket to
    :param title: The title of the ticket
    :return: A message indicating success with the ticket ID or failure if the assignee does not exist
    """
    if ticket_obj.verify_user(assignee_id):
        ticket_id = ticket_obj.insert_ticket(assignee_id, title)
        return f"Successfully inserted the ticket. Here's your ticket id {ticket_id}"
    else:
        return f"The person to be assigned (id: {assignee_id}) does not exist"


def print_rows(rows, cursor=None, col_names=None):
    """
    Pretty-print sqlite3 rows in a table format.

    Args:
        rows: A single tuple (fetchone) or list of tuples (fetchall).
        cursor: Optional sqlite3 cursor to get column names dynamically.
        col_names: Optional list of strings for column names as a fallback.
    """
    if rows is None:
        print("No results.")
        return

    if isinstance(rows, tuple):
        rows = [rows]

    if not rows:
        print("No results.")
        return

    header = []
    if cursor is not None and cursor.description:
        header = [desc[0] for desc in cursor.description]
    elif col_names:
        header = col_names

    str_rows = [[str(col) for col in row] for row in rows]

    if header:
        str_rows.insert(0, header)

    if not str_rows:
        print("No results.")
        return

    col_widths = [max(len(row[i]) for row in str_rows) for i in range(len(str_rows[0]))]

    fmt = " | ".join("{:<" + str(w) + "}" for w in col_widths)

    for i, row in enumerate(str_rows):
        print(fmt.format(*row))

@tool
def view_ticket(ticket_id: int):
    """
    Retrieve details of a ticket by its ID.
    :param ticket_id: The ID of the ticket to view
    :return: The ticket details if the ticket exists, otherwise a message indicating the ticket does not exist
    """
    if ticket_obj.verify_ticket(ticket_id):
        rows = ticket_obj.view_ticket(ticket_id)
        print_rows(rows)

        return f"Displayed the rows"
    else:
        return f"The ticket with id {ticket_id} does not exist"




