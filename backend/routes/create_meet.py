from fastapi import FastAPI, APIRouter
from services.meeting_service import create_meet

router = APIRouter()


@router.post("/create-meet")
async def create_meet_endpoint():
    return create_meet()