import os
import wave
import io
import array
import logging
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# We use AsyncGroq so it doesn't block the LiveKit connection loop
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Vocabulary hints help Whisper correctly spell domain-specific tech words
VOCAB_HINT = (
    "tech stack, FastAPI, Python, Google Cloud Platform, GCP, "
    "LiveKit, WebSocket, asynchronous, Whisper, byte array, "
    "root-mean-square, hallucination, OCR, transformer, "
    "machine learning, backend, frontend, deploy, GitHub, "
    "resume screening, candidate, interview, hackathon, API, SDK, "
    "natural language processing, NLP, SQL, pipeline, "
    "computer science, bachelor's degree, internship, "
    "Tell me about yourself, challenging project"
)

async def transcribe_audio_chunk(pcm_data: bytes, sample_rate: int, num_channels: int, previous_text: str = "") -> str:
    """
    Takes raw PCM audio data, wraps it in a WAV container in memory,
    and sends it to Groq Whisper for transcription. Maintains context using 'previous_text'.
    """
    if not pcm_data or len(pcm_data) < 16000: # Ignore chunks shorter than ~0.5s
        return ""
    
    # --- Silence detection: skip chunks that are mostly quiet ---
    # This prevents Whisper's infamous "Thank you" hallucination on silent audio
    samples = array.array('h', pcm_data)  # 16-bit signed PCM
    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    if rms < 500:  # Below this threshold = background silence/mic bleed/noise
        logger.info(f"Skipping silent chunk (RMS={rms:.0f})")
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
    
    # Build the prompt: vocabulary hints + previous sentence for context
    prompt_parts = [VOCAB_HINT]
    if previous_text:
        prompt_parts.append(previous_text)
    
    try:
        transcription = await groq_client.audio.transcriptions.create(
            file=(wav_io.name, wav_io.read()),
            model="whisper-large-v3",
            response_format="text",
            language="en",
            prompt=" ".join(prompt_parts),
            temperature=0.0
        )
        return transcription.strip()
    except Exception as e:
        print(f"STT Error: {e}")
        return ""
