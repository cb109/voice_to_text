from django.urls import path

from shared_whispers.core.views import home
from shared_whispers.core.views import share_target

urlpatterns = [
    path("", home, name="home"),
    path("share-target", share_target, name="share-target"),
]
