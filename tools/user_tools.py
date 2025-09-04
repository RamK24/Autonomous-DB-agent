from database.repositories import UserRepository, TicketRepository
from langchain_core.tools import tool
from database.db_manager import Database


db = Database('jira_ticketing.db')

user_obj = UserRepository(db)


@tool
def create_user(name: str):
    """
    Create a new user with the specified name.
    :param name: The name of the user to create
    :return: A message indicating success with the user ID or failure due to duplicate name
    """
    user_id = user_obj.insert_user(name)
    if user_id:
        return f'Successfully inserted user {name} his id is {user_id}'
    else:
        return f"Unable to insert user due to duplicate name."
