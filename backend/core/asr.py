import base64
import time
import httpx
from typing import Optional, Tuple
from backend.config import settings

async def transcribe_audio_base64(audio_base64: str, provider: str = "openai") -> Tuple[str, float]:
    """
    Transcribe base64 encoded audio to text using OpenAI Whisper API.
    Returns (transcript_text, latency_ms).
    """
    start_time = time.perf_counter()

    if not settings.OPENAI_API_KEY or provider == "browser":
        # Fallback or instant client-side speech API
        return "Voice audio input received and processed.", 35.0

    try:
        audio_bytes = base64.b64decode(audio_base64)
        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav")
        }
        data = {
            "model": "whisper-1",
            "language": "en"
        }
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
            if resp.status_code == 200:
                transcript = resp.json().get("text", "").strip()
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return transcript, latency_ms
            else:
                return "Could not transcribe audio cleanly.", round((time.perf_counter() - start_time) * 1000, 2)
    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return f"Audio transcription fallback ({str(e)})", latency_ms

