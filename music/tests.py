import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from PIL import Image
from rest_framework.test import APIClient

from .models import Song


def _make_image_file(name="cover.png"):
    buffer = io.BytesIO()
    image = Image.new("RGB", (1, 1), color="black")
    image.save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SongApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_only_published_songs(self):
        Song.objects.create(
            title="Public song",
            audio_file=SimpleUploadedFile("public.mp3", b"audio"),
            lyrics_file=SimpleUploadedFile("public.txt", b"lyrics"),
            cover_image=_make_image_file(),
            status=Song.STATUS_PUBLISHED,
        )
        Song.objects.create(
            title="Draft song",
            audio_file=SimpleUploadedFile("draft.mp3", b"audio"),
            lyrics_file=SimpleUploadedFile("draft.txt", b"lyrics"),
            cover_image=_make_image_file("draft.png"),
            status=Song.STATUS_DRAFT,
        )

        response = self.client.get("/api/songs/")
        self.assertEqual(response.status_code, 200)
        titles = {item["title"] for item in response.json()}
        self.assertIn("Public song", titles)
        self.assertNotIn("Draft song", titles)

    def test_admin_sees_draft_songs(self):
        Song.objects.create(
            title="Draft song",
            audio_file=SimpleUploadedFile("draft.mp3", b"audio"),
            lyrics_file=SimpleUploadedFile("draft.txt", b"lyrics"),
            cover_image=_make_image_file("draft.png"),
            status=Song.STATUS_DRAFT,
        )
        User = get_user_model()
        admin = User.objects.create_user(
            username="admin",
            password="pass12345",
            is_staff=True,
        )

        self.client.force_authenticate(user=admin)
        response = self.client.get("/api/songs/")
        self.assertEqual(response.status_code, 200)
        titles = {item["title"] for item in response.json()}
        self.assertIn("Draft song", titles)
