import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from .models import Song


def _copy_to_web_root(source_path, destination, missing):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source_path.exists():
        shutil.copy2(source_path, destination)
    else:
        missing.append(str(destination))


def _load_songs_json(songs_path):
    if not songs_path.exists():
        return []
    raw = songs_path.read_text(encoding="utf-8", errors="replace")
    return json.loads(raw)


def _write_songs_json(songs_path, data):
    songs_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_songs_data_js(js_path, data):
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    js_path.write_text(f"const songs = {payload};\n", encoding="utf-8")


def _write_datori_html(html_path, data):
    if not html_path.exists():
        return False
    default_option = '<option value="">-- Izvēlies dziesmu --</option>'
    lines = []
    for item in data:
        audio = item.get("audio") or ""
        title = item.get("title") or ""
        if not audio or not title:
            continue
        lines.append(f'<option value="{audio}">{title}</option>')
    options = "\n    ".join([default_option] + lines)
    content = html_path.read_text(encoding="utf-8", errors="replace")
    pattern = r'(<select[^>]*id="songSelector"[^>]*>)(.*?)(</select>)'
    match = re.search(pattern, content, flags=re.DOTALL)
    if not match:
        return False
    updated = re.sub(
        pattern,
        r"\1\n    " + options + r"\n  \3",
        content,
        flags=re.DOTALL,
    )
    html_path.write_text(updated, encoding="utf-8")
    return True


def _sync_song_to_json(song, data=None):
    web_root = getattr(settings, "PUTEKLIS_WEB_PATH", None)
    if not web_root:
        return None, 0, 0, []

    songs_path = Path(web_root) / "songs.json"
    missing = []
    own_write = data is None
    if data is None:
        data = _load_songs_json(songs_path)

    audio_name = Path(song.audio_file.name).name
    lyrics_name = Path(song.lyrics_file.name).name if song.lyrics_file else ""
    image_name = Path(song.cover_image.name).name if song.cover_image else ""

    if song.status != Song.STATUS_PUBLISHED:
        audio_rel = f"music/{audio_name}" if audio_name else ""
        if audio_rel:
            data = [
                item
                for item in data
                if not (
                    item.get("title") == song.title
                    and item.get("audio") == audio_rel
                )
            ]
        if own_write:
            _write_songs_json(songs_path, data)
            _write_songs_data_js(Path(web_root) / "songs_data.js", data)
            if not _write_datori_html(Path(web_root) / "datori.html", data):
                missing.append(str(Path(web_root) / "datori.html"))
        return data, 0, 0, missing

    entry = {
        "title": song.title,
        "audio": f"music/{audio_name}" if audio_name else "",
        "lyrics": f"lyrics/{lyrics_name}" if lyrics_name else "",
        "image": f"cover/{image_name}" if image_name else "",
        "style": song.style or "",
    }

    added = 0
    updated = 0
    matched = False
    for idx, item in enumerate(data):
        if (
            item.get("title") == entry["title"]
            and item.get("audio") == entry["audio"]
        ):
            matched = True
            if item != entry:
                data[idx] = entry
                updated = 1
            break

    if not matched:
        data.append(entry)
        added = 1

    if own_write:
        _write_songs_json(songs_path, data)
        _write_songs_data_js(Path(web_root) / "songs_data.js", data)
        if not _write_datori_html(Path(web_root) / "datori.html", data):
            missing.append(str(Path(web_root) / "datori.html"))

    if song.audio_file:
        _copy_to_web_root(
            Path(song.audio_file.path),
            Path(web_root) / "music" / audio_name,
            missing,
        )
    if song.lyrics_file:
        _copy_to_web_root(
            Path(song.lyrics_file.path),
            Path(web_root) / "lyrics" / lyrics_name,
            missing,
        )
    if song.cover_image:
        _copy_to_web_root(
            Path(song.cover_image.path),
            Path(web_root) / "cover" / image_name,
            missing,
        )

    return data, added, updated, missing


def _remove_song_from_json(song):
    web_root = getattr(settings, "PUTEKLIS_WEB_PATH", None)
    if not web_root:
        return False

    songs_path = Path(web_root) / "songs.json"
    if not songs_path.exists():
        return False

    data = _load_songs_json(songs_path)
    audio_name = Path(song.audio_file.name).name
    audio_rel = f"music/{audio_name}" if audio_name else ""

    filtered = [
        item
        for item in data
        if not (
            item.get("title") == song.title
            and item.get("audio") == audio_rel
        )
    ]

    if filtered == data:
        return False

    _write_songs_json(songs_path, filtered)
    _write_songs_data_js(Path(web_root) / "songs_data.js", filtered)
    _write_datori_html(Path(web_root) / "datori.html", filtered)
    return True


def _log_sync(action, message, missing):
    log_path = Path(settings.BASE_DIR) / "sync.log"
    timestamp = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"[{timestamp}] {action}: {message}"]
    if missing:
        lines.append("Missing files:")
        lines.extend([f"- {path}" for path in missing])
    existing = ""
    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8", errors="replace")
    log_path.write_text(existing + "\n".join(lines) + "\n", encoding="utf-8")


def _get_audio_mtime(song, web_root):
    if not song.audio_file:
        return None
    audio_name = Path(song.audio_file.name).name
    source_path = Path(web_root) / "music" / audio_name
    if not source_path.exists():
        source_path = Path(song.audio_file.path)
    if not source_path.exists():
        return None
    mtime = source_path.stat().st_mtime
    return timezone.make_aware(datetime.fromtimestamp(mtime))


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'published_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'style')
    actions = ['sync_selected']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "sync/",
                self.admin_site.admin_view(self.sync_now),
                name="music_song_sync",
            ),
        ]
        return custom_urls + urls

    def sync_now(self, request):
        if request.method != "POST":
            context = {
                **self.admin_site.each_context(request),
                "title": "Sinhronizēt visas dziesmas",
            }
            return TemplateResponse(
                request,
                "admin/music/song/sync_confirm.html",
                context,
            )

        data = []
        added_total = 0
        updated_total = 0
        missing_total = []

        for song in Song.objects.all():
            data, added, updated, missing = _sync_song_to_json(song, data=data)
            added_total += added
            updated_total += updated
            missing_total.extend(missing)

        if data is not None:
            web_root = getattr(settings, "PUTEKLIS_WEB_PATH", None)
            if web_root:
                _write_songs_json(Path(web_root) / "songs.json", data)
                _write_songs_data_js(Path(web_root) / "songs_data.js", data)
                if not _write_datori_html(Path(web_root) / "datori.html", data):
                    missing_total.append(str(Path(web_root) / "datori.html"))

        message = (
            f"Sinhronizācija pabeigta. "
            f"Pievienoti: {added_total}, atjaunināti: {updated_total}."
        )
        _log_sync("sync_now", message, missing_total)
        self.message_user(request, message, level=messages.SUCCESS)
        return self._redirect_to_changelist()

    def _redirect_to_changelist(self):
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        return HttpResponseRedirect(reverse("admin:music_song_changelist"))

    def sync_selected(self, request, queryset):
        data = None
        added_total = 0
        updated_total = 0
        missing_total = []

        for song in queryset:
            data, added, updated, missing = _sync_song_to_json(song, data=data)
            added_total += added
            updated_total += updated
            missing_total.extend(missing)

        if data is not None:
            web_root = getattr(settings, "PUTEKLIS_WEB_PATH", None)
            if web_root:
                _write_songs_json(Path(web_root) / "songs.json", data)
                _write_songs_data_js(Path(web_root) / "songs_data.js", data)
                if not _write_datori_html(Path(web_root) / "datori.html", data):
                    missing_total.append(str(Path(web_root) / "datori.html"))

        message = (
            f"Sinhronizētas izvēlētās dziesmas. "
            f"Pievienoti: {added_total}, atjaunināti: {updated_total}."
        )
        _log_sync("sync_selected", message, missing_total)
        self.message_user(request, message, level=messages.SUCCESS)

    sync_selected.short_description = "Sinhronizēt izvēlētās dziesmas"

    def save_model(self, request, obj, form, change):
        web_root = getattr(settings, "PUTEKLIS_WEB_PATH", None)
        if web_root:
            created_at = _get_audio_mtime(obj, web_root)
            if created_at:
                obj.created_at = created_at
        super().save_model(request, obj, form, change)
        _, added, updated, missing = _sync_song_to_json(obj)
        message = (
            f"Saglabāts ieraksts. "
            f"Pievienots: {added}, atjaunināts: {updated}."
        )
        _log_sync("save", message, missing)

    def delete_model(self, request, obj):
        removed = _remove_song_from_json(obj)
        message = "Dzēsts ieraksts no songs.json." if removed else "Ieraksts nav atrasts songs.json."
        _log_sync("delete", message, [])
        super().delete_model(request, obj)
