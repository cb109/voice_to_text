import math
import os
import subprocess
import uuid

from django.conf import settings
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

    def __str__(self):
        return f"#{self.pk}, {self.filepath}, {self.duration}s"

    def chunkify(self):
        if self.chunks.exists() or not self.duration:
            return

        basename = os.path.basename(self.filepath)
        base, ext = os.path.splitext(basename)
        prefix = f"{base}-chunk-"

        file_directory = os.path.dirname(self.filepath)
        output_pattern = os.path.join(file_directory, f"{prefix}%04d{ext}")

        subprocess.check_call(
            [
                "ffmpeg",
                "-i",
                self.filepath,
                "-f",
                "segment",
                "-segment_time",
                str(settings.MAX_SECONDS_PER_CHUNK),
                "-c",
                "copy",
                output_pattern,
            ]
        )

        chunk_files = []
        for filename in os.listdir(file_directory):
            if not (filename.startswith(prefix) and filename.endswith(ext)):
                continue
            chunk_filepath = os.path.join(file_directory, filename)
            chunk_files.append(chunk_filepath)

        for i, chunk_filepath in enumerate(sorted(chunk_files)):
            AudioFileChunk.objects.create(
                original_parent_file=self,
                filepath=chunk_filepath,
                duration=get_duration(chunk_filepath),
                index=i,
            )

    def cleanup_files(self):
        # TODO: Once all chunks are transcribed, remove all audio files.
        pass


class AudioFileChunk(TimestampMixin, models.Model):
    original_parent_file = models.ForeignKey(
        AudioFile, on_delete=models.CASCADE, related_name="chunks"
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    filepath = models.CharField(max_length=512, default="", blank=True)

    duration = models.FloatField(default=0.0)

    index = models.PositiveIntegerField(default=0)

    transcribed = models.BooleanField(default=False)

    transcribed_text = models.TextField(default="", blank=True)

    def __str__(self):
        return f"#{self.pk}, {self.index}, {self.filepath}, {self.duration}s"


def get_duration(filepath: str) -> float:
    options = [
        "ffprobe",
        "-i",
        filepath,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-of",
        "csv=p=0",
    ]
    duration = subprocess.check_output(options)
    return float(duration)
