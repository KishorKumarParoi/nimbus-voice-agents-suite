import time
import json
import base64
import hmac
import hashlib
from typing import Optional, Dict, Any
from backend.config import settings

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def generate_livekit_token(
    room_name: str,
    participant_identity: str,
    participant_name: Optional[str] = None,
    can_publish: bool = True,
    can_subscribe: bool = True,
    ttl_seconds: int = 86400,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate an HS256 LiveKit JWT AccessToken natively using Python stdlib.
    Guaranteed compatible with LiveKit Cloud WebRTC and Vercel Serverless.
    """
    api_key = settings.LIVEKIT_API_KEY
    api_secret = settings.LIVEKIT_API_SECRET

    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    
    video_grants = {
        "room": room_name,
        "roomJoin": True,
        "canPublish": can_publish,
        "canSubscribe": can_subscribe,
        "canPublishData": True
    }

    payload = {
        "iss": api_key,
        "sub": participant_identity,
        "name": participant_name or participant_identity,
        "nbf": now - 10,
        "exp": now + ttl_seconds,
        "video": video_grants
    }
    
    if metadata:
        payload["metadata"] = json.dumps(metadata)

    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(api_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

