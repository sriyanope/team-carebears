import json
from ..config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic
        _client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def categorise(transcript: str) -> dict:
    prompt = f"""You are a dementia care assistant in Singapore.
Analyse this caregiver voice note and return ONLY valid JSON:
{{
  "categories": [...],
  "ai_tags": [...],
  "severity": "low|medium|high"
}}
Categories must be from: mood, food, medication, incident, sleep, behaviour, recognition, hydration
ai_tags: 2-4 short specific tags, e.g. "agitation-mild", "appetite-50pct"
Voice note: "{transcript}"
"""
    try:
        client = _get_client()
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)
    except Exception:
        return {"categories": [], "ai_tags": [], "severity": "low"}
