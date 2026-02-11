import os
import subprocess
import time
import uuid
from typing import IO, Callable, Optional, Tuple

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import replicate


@require_http_methods(("GET", "POST"))
def home(request):
    replicate_api_token = request.session.get("replicate_api_token", "")

    if request.method == "POST":
        # Remember API token for subsequent requests.
        replicate_api_token = request.POST["replicate_api_token"].strip()
        if replicate_api_token:
            request.session["replicate_api_token"] = replicate_api_token
            return redirect("home")

    return render(
        request, "core/home.html", {"replicate_api_token": replicate_api_token}
    )


@csrf_exempt
@require_http_methods(("POST"))
def share_target(request):
    """Pass given audio file to replicate.com and return transcribed text.

    This endpoint is the target for the mobile phone's "Share file"
    feature.

    FILES Args:

        audio (IO): The uploaded audio content. Any audio format which
            ffmpeg understands is accepted and will be converted to .wav
            before passing it to openai/whisper.

    POST Args:

        token (str): The REPLICATE_API_TOKEN to authenticate against
            replicate.com.

    Returns:

        json (dict): With 'text' (str) being the transcription result
            and 'time' (float) as the number of seconds this took.

    """
    replicate_api_token = request.session["replicate_api_token"]
    model = request.POST.get("model", WHISPER_MODEL_DEFAULT)

    audio: IO = request.FILES["audio"]
    try:
        normalized_audio_filepath, cleanup_files = _normalize_audio(audio)
        results = _transcribe_audio_file_with_replicate(
            audio_filepath=normalized_audio_filepath,
            model=model,
            replicate_api_token=replicate_api_token,
        )
    finally:
        cleanup_files()

    return render(request, "core/share_target.html", {"results": results})


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
    audio_filepath: str,
    replicate_api_token: str,
) -> dict:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

    start_time = time.time()

    audio: IO = open(audio_filepath, "rb")
    output = replicate.run(
        # https://replicate.com/openai/whisper?input=python
        "openai/whisper:8099696689d249cf8b122d833c36ac3f75505c666a395ca40ef26f68e7d3d16e",
        input={
            "audio": audio,
            "language": "auto",
        },
    )

    end_time = time.time()

    return {
        "text": output["transcription"],
        "time": end_time - start_time,  # In seconds.
    }
