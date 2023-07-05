import os
import subprocess
import time
import uuid
from typing import IO, Callable, Optional, Tuple

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import replicate

from voice_to_text.core.models import AudioFile
from voice_to_text.core.models import get_duration

# https://replicate.com/openai/whisper/versions
# https://github.com/replicate/replicate-python
WHISPER_MODELS = ("tiny", "small", "medium")
WHISPER_MODEL_DEFAULT = "small"
WHISPER_VERSION = "30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed"


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

        model (str): Optional. The quality level for openai/whisper, one
            of 'tiny', 'small', 'medium'. Better quality takes longer.
            Defaults to 'small'.

            Note: Available options are based on the WHISPER_VERSION.

    Returns:

        json (dict): With 'text' (str) being the transcription result
            and 'time' (float) as the number of seconds this took.

    """
    replicate_api_token = request.session["replicate_api_token"]
    model = request.POST.get("model", WHISPER_MODEL_DEFAULT)

    audio: IO = request.FILES["audio"]
    try:
        normalized_audio_filepath, cleanup_files = _normalize_audio(audio)
        normalized_audio = open(normalized_audio_filepath, "rb")

        # TODO: Validate it's not too long, refuse if it is.

        results = _transcribe_audio_file_with_replicate(
            audio=normalized_audio,
            model=model,
            replicate_api_token=replicate_api_token,
        )
    finally:
        cleanup_files()

    return render(request, "core/share_target.html", {"results": results})


def _normalize_audio(audio: IO) -> AudioFile:
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

    audio_file = AudioFile.objects.create(
        filepath=normalized_audio_filepath,
        duration=get_duration(normalized_audio_filepath),
    )
    audio_file.chunkify()

    # def _cleanup_files():
    #     for filepath in (initial_audio_filepath, normalized_audio_filepath):
    #         try:
    #             os.remove(filepath)
    #         except Exception as err:
    #             print(err)

    return audio_file


def _transcribe_audio_file_with_replicate(
    audio: IO,
    model: str,
    replicate_api_token: str,
) -> dict:
    assert model in WHISPER_MODELS

    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

    start_time = time.time()

    output = replicate.run(
        "openai/whisper:" + WHISPER_VERSION,
        input={"audio": audio},
    )

    end_time = time.time()

    return {
        "text": output["transcription"],
        "time": end_time - start_time,  # In seconds.
    }
