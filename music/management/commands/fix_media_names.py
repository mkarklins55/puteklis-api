import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from music.models import Song


class Command(BaseCommand):
    help = "Align media file names with songs.json entries"

    def add_arguments(self, parser):
        default_root = Path(settings.BASE_DIR).parent / "puteklis_weblapa"
        parser.add_argument(
            "--json-path",
            default=str(default_root / "songs.json"),
            help="Path to songs.json",
        )
        parser.add_argument(
            "--source-root",
            default=str(default_root),
            help="Root folder for music/lyrics/cover files",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report changes without modifying files or DB",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_path"]).expanduser()
        source_root = Path(options["source_root"]).expanduser()
        dry_run = options["dry_run"]

        if not json_path.exists():
            self.stderr.write(f"Missing songs.json: {json_path}")
            return

        mapping = self._load_mapping(json_path)
        media_root = Path(settings.MEDIA_ROOT)

        updated = 0
        skipped = 0
        copied = 0

        for song in Song.objects.all():
            target = mapping.get(song.title)
            if not target:
                skipped += 1
                continue

            changed, copied_files = self._apply_targets(
                song=song,
                media_root=media_root,
                source_root=source_root,
                targets=target,
                dry_run=dry_run,
            )
            if changed:
                updated += 1
            copied += copied_files

        self.stdout.write(
            f"Done. Updated: {updated}, Copied: {copied}, Skipped: {skipped}"
        )

    @staticmethod
    def _load_mapping(json_path):
        raw = json_path.read_text(encoding="utf-8", errors="replace")
        data = json.loads(raw)
        mapping = {}
        for item in data:
            title = (item.get("title") or "").strip()
            if not title or title in mapping:
                continue
            mapping[title] = {
                "audio": (item.get("audio") or "").strip(),
                "lyrics": (item.get("lyrics") or "").strip(),
                "image": (item.get("image") or "").strip(),
            }
        return mapping

    def _apply_targets(self, song, media_root, source_root, targets, dry_run):
        changed = False
        copied = 0

        for field_name, subdir in (
            ("audio_file", "music"),
            ("lyrics_file", "lyrics"),
            ("cover_image", "cover"),
        ):
            rel = targets.get(subdir) or ""
            if not rel:
                continue
            target_name = Path(rel).name
            target_rel = f"{subdir}/{target_name}"
            target_media = media_root / target_rel

            field = getattr(song, field_name)
            if field and field.name.endswith(target_name):
                continue

            if not target_media.exists():
                source_path = source_root / target_rel
                if not source_path.exists() and field:
                    source_path = Path(field.path)
                if source_path.exists():
                    if not dry_run:
                        target_media.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_path, target_media)
                    copied += 1

            if not dry_run:
                field.name = target_rel
            changed = True

        if changed and not dry_run:
            song.save(update_fields=["audio_file", "lyrics_file", "cover_image"])
        return changed, copied
