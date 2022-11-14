from django.urls import path

from voice_to_text.core.views import home
from voice_to_text.core.views import share_target

urlpatterns = [
    path("", home, name="home"),
    path("share-target", share_target, name="share-target"),
]
