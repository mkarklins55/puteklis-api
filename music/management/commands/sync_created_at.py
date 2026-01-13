import json
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from music.models import Song


class Command(BaseCommand):
    help = "Sync Song.created_at from audio file modified time"

    def add_arguments(self, parser):
        default_root = Path(settings.BASE_DIR).parent / "puteklis_weblapa"
        parser.add_argument(
            "--source-root",
            default=str(default_root),
            help="Root folder for music files",
        )
        parser.add_argument(
            "--json-path",
            default=str(default_root / "songs.json"),
            help="Path to songs.json for original audio paths",
        )
        parser.add_argument(
            "--use-media",
            action="store_true",
            help="Fallback to media/ if source-root file missing",
        )

    def handle(self, *args, **options):
        source_root = Path(options["source_root"]).expanduser()
        json_path = Path(options["json_path"]).expanduser()
        use_media = options["use_media"]
        updated = 0
        skipped = 0

        title_to_audio = self._load_title_audio(json_path)

        for song in Song.objects.all():
            rel_path = title_to_audio.get(song.title, song.audio_file.name)
            if not rel_path:
                skipped += 1
                continue
            source_path = source_root / rel_path
            if not source_path.exists() and use_media:
                source_path = Path(settings.MEDIA_ROOT) / rel_path
            if not source_path.exists():
                skipped += 1
                continue
            mtime = source_path.stat().st_mtime
            created_at = timezone.make_aware(datetime.fromtimestamp(mtime))
            if song.created_at == created_at:
                skipped += 1
                continue
            song.created_at = created_at
            song.save(update_fields=["created_at"])
            updated += 1

        self.stdout.write(f"Sync complete. Updated: {updated}, Skipped: {skipped}")

    def _load_title_audio(self, json_path):
        if not json_path.exists():
            return {}
        raw = json_path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)
        mapping = {}
        for item in data:
            title = (item.get("title") or "").strip()
            audio = (item.get("audio") or "").strip()
            if title and audio and title not in mapping:
                mapping[title] = audio.replace("\\", "/").lstrip("/")
        return mapping
