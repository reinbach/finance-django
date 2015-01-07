import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from finance.core.models import Profile
from mock import patch, Mock
from tests.fixtures import BaseWebTest


class TestHomeView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("home"))
        assert response.status_code == 200
        assert "Dashboard" not in response

    def test_view_logged_in(self):
        response = self.app.get(reverse("home"), user=self.user)
        assert response.status_code == 200
        assert "Dashboard" in response


class TestContactView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("contact"))
        assert response.status_code == 200
        form = response.form
        form["subject"] = "Hello"
        form["message"] = "just testing"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Your message has been sent. Thank you!" in response

    def test_validation(self):
        response = self.app.get(reverse("contact"))
        assert response.status_code == 200
        form = response.form
        form["message"] = "just testing"
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response


class TestRegisterView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("register"))
        assert response.status_code == 200
        form = response.form
        form["email"] = "test@example.com"
        form["password"] = "321"
        form["confirm_password"] = "321"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully registered" in response
        assert User.objects.filter(
            username="test@example.com"
        ).exists() is True
        user = User.objects.filter(username="test@example.com")
        assert Profile.objects.filter(user=user).exists() is True
        assert "Dashboard" in response

    def test_validation(self):
        response = self.app.get(reverse("register"))
        assert response.status_code == 200
        form = response.form
        form["email"] = "test@example.com"
        form["password"] = "321"
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_mismatched_passwords(self):
        response = self.app.get(reverse("register"))
        assert response.status_code == 200
        form = response.form
        form["email"] = "test@example.com"
        form["password"] = "321"
        form["confirm_password"] = "123"
        response = form.submit()
        assert response.status_code == 200
        assert "Passwords do not match" in response

    def test_failed_auth(self):
        mock_auth = Mock(return_value=None)
        with patch("finance.core.views.authenticate", mock_auth):
            response = self.app.get(reverse("register"))
            assert response.status_code == 200
            form = response.form
            form["email"] = "test@example.com"
            form["password"] = "321"
            form["confirm_password"] = "321"
            response = form.submit().follow()
            assert response.status_code == 200
            assert "Successfully registered" in response
            assert User.objects.filter(
                username="test@example.com"
            ).exists() is True
            user = User.objects.filter(username="test@example.com")
            assert Profile.objects.filter(user=user).exists() is True
            assert "Dashboard" not in response
            mock_auth.assert_called_with(username=u"test@example.com",
                                         password=u"321")


class TestLogoutView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("logout"), user=self.user)
        assert response.status_code == 200
        assert "You have successfully logged out" in response


class TestProfileView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("profile.home"), user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Profile</h1>' in response

        form = response.forms[1]
        new_year = datetime.date.today().year
        form["current_year"] = new_year
        response = form.submit().follow()
        assert response.status_code == 200

        p = Profile.objects.get(pk=self.profile.pk)
        assert p.current_year == new_year

    def test_permissions(self):
        response = self.app.get(reverse("profile.home"))
        assert response.status_code == 302

    def test_validation(self):
        response = self.app.get(reverse("profile.home"), user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Profile</h1>' in response

        form = response.forms[1]
        form["current_year"].force_value("")
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response
