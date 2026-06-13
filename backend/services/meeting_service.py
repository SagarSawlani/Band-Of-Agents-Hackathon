import uuid

FRONTEND_URL = "http://localhost:3000"


def create_meet():
    room_id = str(uuid.uuid4())

    return {
        "room_id": room_id,
        "join_link": f"{FRONTEND_URL}/interview/{room_id}",
    }