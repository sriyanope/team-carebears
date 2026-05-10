import logging

from openai import BadRequestError

from ..config import settings

logger = logging.getLogger(__name__)

_whisper_model = None
_ENGLISH_PROMPT = "Singapore, dementia care, medication, agitation"
_CHINESE_PROMPT = (
    "以下是粤语口语录音。请直接输出中文转写，尽量使用中文汉字，"
    "不要输出英文，不要输出拼音，不要做翻译。"
)


def load_model() -> None:
    global _whisper_model
    if settings.WHISPER_MODE == "local":
        import whisper
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)


def transcribe(audio_path: str, language: str = "en") -> str:
    if settings.WHISPER_MODE == "api":
        return _transcribe_api(audio_path, language)
    return _transcribe_local(audio_path, language)


def _resolve_transcription_language(language: str) -> str:
    normalized = (language or "en").strip().lower()
    return normalized


def _is_chinese_page(language: str) -> bool:
    return (language or "").strip().lower() == "zh"


def _han_character_ratio(text: str) -> float:
    stripped = "".join(char for char in text if not char.isspace())
    if not stripped:
        return 0.0
    han_count = sum(1 for char in stripped if "\u4e00" <= char <= "\u9fff")
    return han_count / len(stripped)


def _looks_non_chinese(text: str) -> bool:
    stripped = "".join(char for char in text if not char.isspace())
    if not stripped:
        return True
    contains_han = any("\u4e00" <= char <= "\u9fff" for char in stripped)
    latin_count = sum(1 for char in stripped if char.isascii() and char.isalpha())
    return (not contains_han) or (_han_character_ratio(stripped) < 0.35 and latin_count >= 4)


def _transcribe_local(audio_path: str, language: str = "en") -> str:
    if _whisper_model is None:
        load_model()
    transcription_language = _resolve_transcription_language(language)
    kwargs: dict = {"language": transcription_language, "temperature": 0.0}
    if transcription_language == "en":
        kwargs["initial_prompt"] = _ENGLISH_PROMPT
    elif _is_chinese_page(language):
        kwargs["language"] = "zh"
        kwargs["initial_prompt"] = _CHINESE_PROMPT
        kwargs["condition_on_previous_text"] = False
    result = _whisper_model.transcribe(audio_path, **kwargs)
    transcript = result["text"].strip()

    if _is_chinese_page(language) and _looks_non_chinese(transcript):
        logger.warning(
            "Chinese-page transcript looked non-Chinese (%r); retrying with stronger Chinese bias.",
            transcript,
        )
        retry_kwargs = {
            **kwargs,
            "language": "zh",
            "initial_prompt": _CHINESE_PROMPT + " 只输出中文汉字和中文标点。",
            "condition_on_previous_text": False,
            "temperature": 0.0,
        }
        retry_result = _whisper_model.transcribe(audio_path, **retry_kwargs)
        retry_transcript = retry_result["text"].strip()
        if retry_transcript and _han_character_ratio(retry_transcript) >= _han_character_ratio(transcript):
            transcript = retry_transcript

    return transcript


def _transcribe_api(audio_path: str, language: str = "en") -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    transcription_language = _resolve_transcription_language(language)
    kwargs: dict = {"model": "whisper-1", "language": transcription_language, "temperature": 0}
    if transcription_language == "en":
        kwargs["prompt"] = _ENGLISH_PROMPT
    elif _is_chinese_page(language):
        kwargs["language"] = "zh"
        kwargs["prompt"] = _CHINESE_PROMPT
    try:
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(file=f, **kwargs)
    except BadRequestError:
        if not _is_chinese_page(language):
            raise
        logger.warning("Chinese-page API transcription failed with language='zh'; retrying without language lock.")
        fallback_kwargs = {**kwargs}
        fallback_kwargs.pop("language", None)
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(file=f, **fallback_kwargs)

    transcript = result.text.strip()
    if _is_chinese_page(language) and _looks_non_chinese(transcript):
        logger.warning(
            "Chinese-page API transcript looked non-Chinese (%r); retrying with stronger Chinese prompt.",
            transcript,
        )
        retry_kwargs = {
            **kwargs,
            "language": "zh",
            "prompt": _CHINESE_PROMPT + " 只输出中文汉字和中文标点。",
            "temperature": 0,
        }
        with open(audio_path, "rb") as f:
            retry_result = client.audio.transcriptions.create(file=f, **retry_kwargs)
        retry_transcript = retry_result.text.strip()
        if retry_transcript and _han_character_ratio(retry_transcript) >= _han_character_ratio(transcript):
            transcript = retry_transcript

    return transcript
