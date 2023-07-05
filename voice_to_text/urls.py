from django.contrib import admin
from django.urls import path

from voice_to_text.core.views import home
from voice_to_text.core.views import share_target
from voice_to_text.core.views import show_results

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("share-target", share_target, name="share-target"),
    path("results/<uuid:file_uuid>", show_results, name="results"),
]
