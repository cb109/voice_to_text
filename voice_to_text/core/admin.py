from django.contrib import admin

from voice_to_text.core.models import AudioFile
from voice_to_text.core.models import AudioFileChunk


class AudioFileAdmin(admin.ModelAdmin):
    list_display = (
        "filepath",
        "duration",
        "id",
        "created_at",
        "modified_at",
    )


class AudioFileChunkAdmin(admin.ModelAdmin):
    list_display = (
        "filepath",
        "transcribed",
        "duration",
        "index",
        "original_parent_file",
        "id",
        "created_at",
        "modified_at",
    )


admin.site.register(AudioFile, AudioFileAdmin)
admin.site.register(AudioFileChunk, AudioFileChunkAdmin)
