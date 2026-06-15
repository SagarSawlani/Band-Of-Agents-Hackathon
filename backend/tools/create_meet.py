from langchain_core.tools import tool
from services.meeting_service import create_meet as _create_meet

@tool
def create_meet():
    """
    Creates a new interview meeting and returns
    room_id and join_link.
    """

    return _create_meet()