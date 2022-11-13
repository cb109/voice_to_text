from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from shared_whispers.core.views import api_transcribe_audio
from shared_whispers.core.views import share_target
from shared_whispers.core.views import transcribe_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/transcribe/", api_transcribe_audio, name="api-transcribe"),
    path("share/", share_target, name="share-target"),
    path("", transcribe_page, name="transcribe-page"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
