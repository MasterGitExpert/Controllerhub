
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class U102LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "TestPass123!"
        self.user = User.objects.create_user(
            username="ayden",
            email="ayden@example.com",
            password=self.password,
            first_name="Ayden",
        )

    # U102-TC1: login page loads
    def test_login_page_renders(self):
        r = self.client.get(reverse("login"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Log in")

    # U102-TC2: successful login -> redirect to index
    def test_login_success_redirects_to_index(self):
        self.assertEqual(getattr(settings, "LOGIN_REDIRECT_URL", "/"), "/")
        r = self.client.post(reverse("login"), {
            "username": "ayden",
            "password": self.password,
            "next": "/",   # keep or omit; LOGIN_REDIRECT_URL = '/'
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], "/")

    # U102-TC3: navbar shows Account when authenticated
    def test_navbar_after_login(self):
        self.client.login(username="ayden", password=self.password)
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="nav-account"')
        self.assertNotContains(r, 'id="nav-login"')

    # U102-TC4: negative credentials stay on login and show error
    def test_login_failure_shows_error(self):
        r = self.client.post(reverse("login"), {
            "username": "ayden",
            "password": "WrongPassword",
            "next": "/",
        })
        self.assertEqual(r.status_code, 200)  # stays on login page
        # Error message text depends on your template; assert something stable:
        self.assertContains(r, "try again", status_code=200)

    # U102-TC5: password reset page renders (R2 readiness)
    def test_password_reset_page_renders(self):
        r = self.client.get(reverse("password_reset"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Reset password")
