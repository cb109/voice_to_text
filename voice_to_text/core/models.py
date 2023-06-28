import uuid

from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """Add created and modified timestamps to a model."""

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AudioFile(TimestampMixin, models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    filepath = models.CharField(max_length=512, default="", blank=True)

    duration = models.FloatField(default=0.0)


class AudioFileChunk(TimestampMixin, models.Model):
    original_parent_file = models.ForeignKey(
        AudioFile, on_delete=models.CASCADE, related_name="chunks"
    )

    filepath = models.CharField(max_length=512, default="", blank=True)

    duration = models.FloatField(default=0.0)

    index = models.PositiveIntegerField(default=0)

    transcribed = models.BooleanField(default=False)

    transcribed_text = models.TextField(default="", blank=True)
