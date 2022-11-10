import os
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

import replicate


ALLOWED_WHISPER_MODELS = ("tiny", "small", "medium")


@login_required
@require_http_methods(("POST",))
def transcribe_audio_file(request):
    from pprint import pprint

    pprint(request.POST)
    pprint(request.FILES)

    # Get transcription options: model, language. If no
    # language is specified, don't pass any so it will be autodetected.

    # Get audiofile and save it to disk.

    # Convert it to .wav using ffmpeg or something similar.

    # Validate it's not too long, refuse if it is.

    # Pass it to replicate for transcription using options.

    # Return transcription and how long it took.

    # Cleanup audio files?

    return JsonResponse({"text": "TBD"})


def _transcribe_audio_file_with_replicate(
    audio_filepath: str, model: str, language: Optional[str] = None
) -> dict:
    assert "REPLICATE_API_TOKEN" in os.environ
    assert model in ALLOWED_WHISPER_MODELS

    whisper = replicate.models.get("openai/whisper")
    output = whisper.predict(audio=open(audio_filepath, "rb"), model=model)
    return output["transcription"]
