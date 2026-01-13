from rest_framework import serializers

from .models import Song


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = (
            "id",
            "title",
            "audio_file",
            "lyrics_file",
            "cover_image",
            "style",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )
