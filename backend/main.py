from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.create_meet import router as create_meet_router
from livekit import api

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

app.include_router(create_meet_router)

@app.get("/token")
async def get_token(room: str, name: str):

    token = (
        api.AccessToken(
            LIVEKIT_API_KEY,
            LIVEKIT_API_SECRET
        )
        .with_identity(name)
        .with_name(name)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room
            )
        )
        .to_jwt()
    )

    return {"token": token}