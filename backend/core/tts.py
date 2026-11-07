import time
import base64
import httpx
from typing import Optional, Tuple
from backend.config import settings

async def generate_speech(
    text: str,
    provider: str = "elevenlabs",
    voice_id: Optional[str] = None
) -> Tuple[Optional[str], float]:
    """
    Synthesizes speech using ElevenLabs or OpenAI TTS.
    Returns (audio_base64_data_uri, latency_ms).
    """
    start_time = time.perf_counter()

    if provider == "browser":
        # Browser uses native SpeechSynthesis API on client-side (0ms network TTS)
        return None, 15.0

    # 1. Try ElevenLabs if configured
    if provider == "elevenlabs" and settings.ELEVENLABS_API_KEY:
        target_voice = voice_id or settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    return f"data:audio/mp3;base64,{audio_b64}", latency_ms
        except Exception:
            pass # Fall through to OpenAI TTS

    # 2. Try OpenAI TTS if configured
    if settings.OPENAI_API_KEY:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "tts-1",
            "voice": "alloy",
            "input": text[:400] # Truncate for speed
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    audio_b64 = base64.b64encode(resp.content).decode("utf-8")
                    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    return f"data:audio/mp3;base64,{audio_b64}", latency_ms
        except Exception:
            pass

    # Fallback to browser synthesis
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    return None, max(latency_ms, 20.0)

