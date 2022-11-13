from django.urls import path

from shared_whispers.core.views import api_transcribe_audio
from shared_whispers.core.views import share_target

urlpatterns = [
    path("api/transcribe/", api_transcribe_audio, name="api-transcribe"),
    path("", share_target, name="share-target"),
]
