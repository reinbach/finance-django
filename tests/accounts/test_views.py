from django.core.urlresolvers import reverse
from tests.fixtures import BaseWebTest


class TestDashboardView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("accounts.dashboard"), user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Dashboard</h1>' in response

    def test_permissions(self):
        response = self.app.get(reverse("accounts.dashboard"))
        assert response.status_code == 302


class TestSettingsView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("accounts.settings"), user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Settings</h1>' in response