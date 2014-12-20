from django.core.urlresolvers import reverse
from finance.accounts.models import AccountType
from tests.fixtures import BaseWebTest, account_type_factory, profile_factory


def is_settings_page(response):
    return '<h1 class="page-header">Settings</h1>' in response


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
        assert is_settings_page(response) is True

    def test_permissions(self):
        response = self.app.get(reverse("accounts.settings"))
        assert response.status_code == 302


class TestAccountTypeAddView(BaseWebTest):
    def test_view(self):
        response = self.app.get(reverse("accounts.account_type.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct1"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully added Account Type acct1" in response
        assert AccountType.objects.filter(name="acct1").exists() is True

    def test_validation(self):
        response = self.app.get(reverse("accounts.account_type.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = ""
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_name_uniqueness(self):
        acct = account_type_factory(profile=self.profile)
        response = self.app.get(reverse("accounts.account_type.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = acct.name
        response = form.submit()
        assert response.status_code == 200
        assert "Name needs to be unique" in response


class TestAccountTypeEditView(BaseWebTest):
    def test_permissions(self):
        acct = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct.pk]))
        assert response.status_code == 302

    def test_view(self):
        acct = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct2"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully updated Account Type acct2" in response

    def test_validation(self):
        acct = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = ""
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_name_uniqueness(self):
        account_type_factory(profile=self.profile, name="acct2")
        acct = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct2"
        response = form.submit()
        assert response.status_code == 200
        assert "Name needs to be unique" in response

    def test_no_change(self):
        acct = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct1"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully updated Account Type acct1" in response

    def test_isolation(self):
        profile = profile_factory()
        acct = account_type_factory(profile=profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct.pk]), user=self.user,
                                expect_errors=True)
        assert response.status_code == 404


class TestAccountTypeDeleteView(BaseWebTest):
    csrf_checks = False

    def test_view(self):
        acct = account_type_factory(profile=self.profile)
        response = self.app.post(reverse("accounts.account_type.delete",
                                         args=[acct.pk]),
                                 user=self.user).follow()
        assert response.status_code == 200
        assert "Successfully deleted Account Type" in response
        assert AccountType.objects.filter(pk=acct.pk).exists() is False

    def test_permission(self):
        acct = account_type_factory(profile=self.profile)
        response = self.app.post(reverse("accounts.account_type.delete",
                                         args=[acct.pk])).follow()
        assert response.status_code == 200
        assert AccountType.objects.filter(pk=acct.pk).exists() is True

    def test_isolation(self):
        profile = profile_factory()
        acct = account_type_factory(profile=profile)
        response = self.app.post(reverse("accounts.account_type.delete",
                                         args=[acct.pk]),
                                 user=self.user, expect_errors=True)
        assert response.status_code == 404
