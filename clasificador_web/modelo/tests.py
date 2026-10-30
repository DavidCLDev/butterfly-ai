from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import ButterflySighting


class SightingViewTests(TestCase):
    def setUp(self):
        self.media_dir = TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(self.media_dir.cleanup)

        self.user = User.objects.create_user(username="ana", password="test-password")
        self.client.force_login(self.user)

    def image_upload(self, name="butterfly.png"):
        image_bytes = BytesIO()
        Image.new("RGB", (32, 32), color="purple").save(image_bytes, format="PNG")
        return SimpleUploadedFile(
            name,
            image_bytes.getvalue(),
            content_type="image/png",
        )

    @patch("modelo.views.predict_genus", return_value=("Morpho", 93.5))
    def test_upload_classifies_and_saves_sighting(self, predict_genus):
        response = self.client.post(
            reverse("sighting_list"),
            {"image": self.image_upload()},
        )

        self.assertRedirects(response, reverse("sighting_list"))
        sighting = ButterflySighting.objects.get()
        self.assertEqual(sighting.user, self.user)
        self.assertEqual(sighting.genus, "Morpho")
        self.assertEqual(sighting.confidence, 93.5)
        self.assertTrue(sighting.image.storage.exists(sighting.image.name))
        predict_genus.assert_called_once()

    def test_upload_runs_the_onnx_model(self):
        response = self.client.post(
            reverse("sighting_list"),
            {"image": self.image_upload()},
        )

        self.assertRedirects(response, reverse("sighting_list"))
        sighting = ButterflySighting.objects.get()
        self.assertIn(
            sighting.genus,
            {
                "Anartia",
                "Ascia",
                "Battus",
                "Danaus",
                "Dryas",
                "Heliconius",
                "Morpho",
                "Papilio",
                "Phoebis",
                "Vanessa",
            },
        )
        self.assertGreaterEqual(sighting.confidence, 0)
        self.assertLessEqual(sighting.confidence, 100)

    @patch("modelo.views.predict_genus")
    def test_rejects_non_image_upload(self, predict_genus):
        response = self.client.post(
            reverse("sighting_list"),
            {
                "image": SimpleUploadedFile(
                    "not-an-image.png",
                    b"not an image",
                    content_type="image/png",
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ButterflySighting.objects.exists())
        predict_genus.assert_not_called()

    def test_user_cannot_view_or_delete_another_users_sighting(self):
        other_user = User.objects.create_user(
            username="luis",
            password="test-password",
        )
        sighting = ButterflySighting.objects.create(
            user=other_user,
            image=self.image_upload("private.png"),
            genus="Vanessa",
            confidence=80,
        )

        response = self.client.get(reverse("sighting_list"))
        self.assertNotContains(response, "Vanessa")

        response = self.client.post(
            reverse("delete_sighting", args=[sighting.pk]),
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ButterflySighting.objects.filter(pk=sighting.pk).exists())
        response = self.client.get(
            reverse("sighting_image", args=[sighting.pk]),
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_removes_sighting_and_image(self):
        sighting = ButterflySighting.objects.create(
            user=self.user,
            image=self.image_upload(),
            genus="Morpho",
            confidence=90,
        )
        image_name = sighting.image.name

        image_response = self.client.get(
            reverse("sighting_image", args=[sighting.pk]),
        )
        self.assertEqual(image_response.status_code, 200)
        self.assertEqual(image_response["Content-Type"], "image/png")
        image_response.close()

        response = self.client.post(
            reverse("delete_sighting", args=[sighting.pk]),
        )

        self.assertRedirects(response, reverse("sighting_list"))
        self.assertFalse(ButterflySighting.objects.filter(pk=sighting.pk).exists())
        self.assertFalse(sighting.image.storage.exists(image_name))
