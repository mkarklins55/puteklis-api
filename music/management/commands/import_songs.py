import json
from datetime import datetime
from pathlib import Path

from django.utils import timezone
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from music.models import Song


class Command(BaseCommand):
    help = "Import songs from a songs.json file"

    def add_arguments(self, parser):
        default_root = Path(settings.BASE_DIR).parent / "puteklis_weblapa"
        parser.add_argument(
            "--path",
            default=str(default_root / "songs.json"),
            help="Path to songs.json",
        )
        parser.add_argument(
            "--source-root",
            default=str(default_root),
            help="Root folder for music/lyrics/cover files",
        )
        parser.add_argument(
            "--status",
            choices=[Song.STATUS_DRAFT, Song.STATUS_PUBLISHED],
            default=Song.STATUS_PUBLISHED,
            help="Status for imported songs",
        )

    def handle(self, *args, **options):
        json_path = Path(options["path"]).expanduser()
        source_root = Path(options["source_root"]).expanduser()
        status = options["status"]

        if not json_path.exists():
            self.stderr.write(f"Missing file: {json_path}")
            return

        raw = json_path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)

        created = 0
        skipped = 0

        for item in data:
            title = (item.get("title") or "").strip()
            audio_rel = self._normalize_rel(item.get("audio"))
            lyrics_rel = self._normalize_rel(item.get("lyrics"))
            image_rel = self._normalize_rel(item.get("image"))
            style = (item.get("style") or "").strip()

            if not title or not audio_rel:
                skipped += 1
                continue

            audio_name = Path(audio_rel).name
            if Song.objects.filter(
                title=title, audio_file__endswith=audio_name
            ).exists():
                skipped += 1
                continue

            song = Song(title=title, style=style, status=status)
            self._attach_file(song.audio_file, source_root, audio_rel, name=audio_name)
            self._attach_file(song.lyrics_file, source_root, lyrics_rel, warn_missing=False)
            self._attach_file(song.cover_image, source_root, image_rel)
            created_at = self._get_audio_mtime(source_root, audio_rel)
            if created_at:
                song.created_at = created_at
            song.save()
            created += 1

        self.stdout.write(
            f"Import complete. Created: {created}, Skipped: {skipped}"
        )

    @staticmethod
    def _normalize_rel(value):
        if not value:
            return ""
        return str(value).replace("\\", "/").lstrip("/")

    def _attach_file(self, field, source_root, rel_path, warn_missing=True, name=None):
        if not rel_path:
            return
        if name is None:
            name = rel_path
        storage = field.storage
        if storage.exists(name):
            field.name = name
            return
        source_path = source_root / rel_path
        if not source_path.exists():
            if warn_missing:
                self.stdout.write(
                    self.style.WARNING(f"Missing file: {source_path}")
                )
            return
        with source_path.open("rb") as handle:
            field.save(name, File(handle), save=False)

    def _get_audio_mtime(self, source_root, rel_path):
        if not rel_path:
            return None
        source_path = source_root / rel_path
        if not source_path.exists():
            return None
        mtime = source_path.stat().st_mtime
        return timezone.make_aware(datetime.fromtimestamp(mtime))
