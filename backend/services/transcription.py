from ..config import settings

_whisper_model = None


def load_model() -> None:
    global _whisper_model
    if settings.WHISPER_MODE == "local":
        import whisper
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)


def transcribe(audio_path: str) -> str:
    if settings.WHISPER_MODE == "api":
        return _transcribe_api(audio_path)
    return _transcribe_local(audio_path)


def _transcribe_local(audio_path: str) -> str:
    if _whisper_model is None:
        load_model()
    result = _whisper_model.transcribe(
        audio_path,
        language="en",
        initial_prompt="Singapore, dementia care, medication, agitation",
    )
    return result["text"].strip()


def _transcribe_api(audio_path: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="en",
            prompt="Singapore, dementia care, medication, agitation",
        )
    return result.text.strip()
