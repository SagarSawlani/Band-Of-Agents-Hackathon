from fastapi import UploadFile, File, APIRouter
from groq import Groq
import tempfile
import os

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

