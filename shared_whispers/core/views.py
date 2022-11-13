import os
import subprocess
import time
import uuid
from typing import IO
from typing import Optional

# from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings

from replicate import default_client as replicate_client


ALLOWED_WHISPER_MODELS = ("tiny", "small", "medium")


@require_http_methods(("POST",))
def transcribe_audio(request):
    """Pass given audio file to replicate.com and return transcribed text.

    POST Args:

        token (str): The REPLICATE_API_TOKEN to authenticate against
            replicate.com.

        model (str): Optional. The quality level for openai/whisper, one
            of 'tiny', 'small', 'medium'. Better quality takes longer.
            Defaults to 'small'.

        language (str): Optional, can be passed if we know the language
            beforehand, otherwise it will be auto-detected which takes a
            little longer.

    Returns:

        json (dict): With 'text' (str) being the transcription result
            and 'time' (float) as the number of seconds this took.

    """
    replicate_api_token = request.POST["token"]
    model = request.POST.get("model", "small")
    language = request.POST.get("language", None)

    audio: IO = request.FILES["audio"]
    normalized_audio_filepath = _normalize_audio(audio)
    normalized_audio = open(normalized_audio_filepath, "rb")

    # Validate it's not too long, refuse if it is.

    # Pass it to replicate for transcription using options.

    # Return transcription and how long it took.
    results = _transcribe_audio_file_with_replicate(
        audio=normalized_audio,
        model=model,
        replicate_api_token=replicate_api_token,
        language=language,
    )

    # Cleanup audio files?

    return JsonResponse(results)


def _normalize_audio(audio: IO) -> str:
    """Save given audio data to disk and normalize it to .wav format.

    Return path to .wav file.

    """
    prefix = str(uuid.uuid4()) + "_"

    audio_directory = os.path.join(settings.MEDIA_ROOT, "audio")
    if not os.path.isdir(audio_directory):
        os.makedirs(audio_directory)

    initial_audio_filepath = os.path.join(audio_directory, f"{prefix}{audio.name}")
    with open(initial_audio_filepath, "wb+") as initial:
        for chunk in audio.chunks():
            initial.write(chunk)

    basename, _ = os.path.splitext(audio.name)
    normalized_audio_filepath = os.path.join(
        settings.MEDIA_ROOT, "audio", f"{prefix}{basename}_normalized.wav"
    )
    ffmpeg_options = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        initial_audio_filepath,
        normalized_audio_filepath,
    ]
    subprocess.check_call(ffmpeg_options)

    return normalized_audio_filepath


def _transcribe_audio_file_with_replicate(
    audio: IO,
    model: str,
    replicate_api_token: str,
    language: Optional[str] = None,
) -> dict:
    assert model in ALLOWED_WHISPER_MODELS

    start_time = time.time()

    replicate_client.api_token = replicate_api_token
    whisper = replicate_client.models.get("openai/whisper")
    extra = {}
    if language:
        extra["language"] = language
    output = whisper.predict(audio=audio, model=model, **extra)

    end_time = time.time()

    return {
        "text": output["transcription"],
        "time": end_time - start_time,  # In seconds.
    }
