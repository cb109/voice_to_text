import os
import subprocess
import time
import uuid
from typing import Callable
from typing import IO
from typing import Optional
from typing import Tuple

from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from replicate import default_client as replicate_client


ALLOWED_WHISPER_MODELS = ("tiny", "small", "medium")


@require_http_methods(("GET"))
def share_target(request):
    return HttpResponse("shared")


@require_http_methods(("GET", "POST"))
def transcribe_page(request):
    if request.method == "GET":
        return render(
            request, "core/transcribe_page.html", _get_session_template_context(request)
        )
    return transcribe_audio(request)


@require_http_methods(("POST",))
def transcribe_audio(request):
    """Pass given audio file to replicate.com and and show results on page.

    For details on input args, see api_transcribe_audio().

    Returns:

        html

    """
    results = _handle_transcription_request(request)
    return render(
        request,
        "core/transcribe_page.html",
        {"results": results, **_get_session_template_context(request)},
    )


@require_http_methods(("POST",))
def api_transcribe_audio(request):
    """Pass given audio file to replicate.com and return transcribed text.

    FILES Args:

        audio (IO): The uploaded audio content. Any audio format which
            ffmpeg understands is accepted and will be converted to .wav
            before passing it to openai/whisper.

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
    results = _handle_transcription_request(request)
    return JsonResponse(results)


def _handle_transcription_request(request, do_cleanup: bool = True) -> dict:
    replicate_api_token = request.POST["token"]
    model = request.POST.get("model", "small")
    language = request.POST.get("language", None)

    audio: IO = request.FILES["audio"]
    normalized_audio_filepath, cleanup_files = _normalize_audio(audio)
    normalized_audio = open(normalized_audio_filepath, "rb")

    # TODO: Validate it's not too long, refuse if it is.

    results = _transcribe_audio_file_with_replicate(
        audio=normalized_audio,
        model=model,
        replicate_api_token=replicate_api_token,
        language=language,
    )

    if do_cleanup:
        cleanup_files()

    return results


def _normalize_audio(audio: IO) -> Tuple[str, Callable]:
    """Save given audio data to disk and normalize it to .wav format.

    Return path to .wav file as well as a function to remove the files
    in case they are not needed anymore later on.

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

    def _cleanup_files():
        for filepath in (initial_audio_filepath, normalized_audio_filepath):
            try:
                os.remove(filepath)
            except Exception as err:
                print(err)

    return normalized_audio_filepath, _cleanup_files


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
