from ..config import settings

_whisper_model = None


def load_model() -> None:
    global _whisper_model
    if settings.WHISPER_MODE == "local":
        import whisper
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)


def transcribe(audio_path: str, language: str = "en") -> str:
    if settings.WHISPER_MODE == "api":
        return _transcribe_api(audio_path, language)
    return _transcribe_local(audio_path, language)


def _transcribe_local(audio_path: str, language: str = "en") -> str:
    if _whisper_model is None:
        load_model()
    kwargs: dict = {"language": language}
    if language == "en":
        kwargs["initial_prompt"] = "Singapore, dementia care, medication, agitation"
    result = _whisper_model.transcribe(audio_path, **kwargs)
    return result["text"].strip()


def _transcribe_api(audio_path: str, language: str = "en") -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    kwargs: dict = {"model": "whisper-1", "language": language}
    if language == "en":
        kwargs["prompt"] = "Singapore, dementia care, medication, agitation"
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(file=f, **kwargs)
    return result.text.strip()
