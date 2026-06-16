import os
import wave
import io
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

# We use AsyncGroq so it doesn't block the LiveKit connection loop
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def transcribe_audio_chunk(pcm_data: bytes, sample_rate: int, num_channels: int) -> str:
    """
    Takes raw PCM audio data, wraps it in a WAV container in memory,
    and sends it to Groq Whisper for transcription.
    """
    if not pcm_data or len(pcm_data) < 4000: # Ignore tiny noise chunks
        return ""
        
    # Create in-memory WAV file
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(2) # 16-bit PCM (2 bytes per sample)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    
    wav_io.seek(0)
    wav_io.name = "chunk.wav" # Groq API requires a filename extension
    
    try:
        transcription = await groq_client.audio.transcriptions.create(
            file=(wav_io.name, wav_io.read()),
            model="whisper-large-v3",
            response_format="text",
            language="en"
        )
        return transcription.strip()
    except Exception as e:
        print(f"STT Error: {e}")
        return ""
