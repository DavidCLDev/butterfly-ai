from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import User


class RegistrationViewTests(TestCase):
    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Ana",
                "username": "ana",
                "email": "ana@example.com",
                "password1": "Strong-password-482!",
                "password2": "Strong-password-482!",
                "accept_terms": "on",
            },
        )

        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="ana")
        self.assertEqual(user.first_name, "Ana")
        self.assertEqual(user.email, "ana@example.com")

    def test_register_requires_terms_acceptance(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "ana",
                "password1": "Strong-password-482!",
                "password2": "Strong-password-482!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="ana").exists())
