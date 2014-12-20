from django.core.urlresolvers import reverse
from finance.accounts.models import AccountType, Account
from tests.fixtures import (BaseWebTest, account_type_factory, profile_factory,
                            account_factory)


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
        assert AccountType.objects.filter(
            name="acct1",
            profile=self.profile
        ).exists() is True

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
        acct_type = account_type_factory(profile=self.profile)
        response = self.app.get(reverse("accounts.account_type.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = acct_type.name
        response = form.submit()
        assert response.status_code == 200
        assert "Name needs to be unique" in response


class TestAccountTypeEditView(BaseWebTest):
    def test_permissions(self):
        acct_type = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct_type.pk]))
        assert response.status_code == 302

    def test_view(self):
        acct_type = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct_type.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct2"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully updated Account Type acct2" in response

    def test_validation(self):
        acct_type = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct_type.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = ""
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_name_uniqueness(self):
        account_type_factory(profile=self.profile, name="acct2")
        acct_type = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct_type.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct2"
        response = form.submit()
        assert response.status_code == 200
        assert "Name needs to be unique" in response

    def test_no_change(self):
        acct_type = account_type_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct_type.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct1"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully updated Account Type acct1" in response

    def test_isolation(self):
        profile = profile_factory()
        acct_type = account_type_factory(profile=profile, name="acct1")
        response = self.app.get(reverse("accounts.account_type.edit",
                                        args=[acct_type.pk]), user=self.user,
                                expect_errors=True)
        assert response.status_code == 404


class TestAccountTypeDeleteView(BaseWebTest):
    csrf_checks = False

    def test_view(self):
        acct_type = account_type_factory(profile=self.profile)
        response = self.app.post(reverse("accounts.account_type.delete",
                                         args=[acct_type.pk]),
                                 user=self.user).follow()
        assert response.status_code == 200
        assert "Successfully deleted Account Type" in response
        assert AccountType.objects.filter(pk=acct_type.pk).exists() is False

    def test_permission(self):
        acct_type = account_type_factory(profile=self.profile)
        response = self.app.post(reverse("accounts.account_type.delete",
                                         args=[acct_type.pk])).follow()
        assert response.status_code == 200
        assert AccountType.objects.filter(pk=acct_type.pk).exists() is True

    def test_isolation(self):
        profile = profile_factory()
        acct_type = account_type_factory(profile=profile)
        response = self.app.post(reverse("accounts.account_type.delete",
                                         args=[acct_type.pk]),
                                 user=self.user, expect_errors=True)
        assert response.status_code == 404
        assert AccountType.objects.filter(pk=acct_type.pk).exists() is True


class TestAccountView(BaseWebTest):
    def test_view(self):
        acct = account_factory(profile=self.profile)
        response = self.app.get(reverse("accounts.account.list"),
                                user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Accounts</h1>' in response
        assert acct.name in response

    def test_permission(self):
        acct = account_factory(profile=self.profile)
        response = self.app.get(reverse("accounts.account.list"))
        assert response.status_code == 302
        assert '<h1 class="page-header">Accounts</h1>' not in response
        assert acct.name not in response

    def test_isolation(self):
        acct1 = account_factory(profile=self.profile)
        profile = profile_factory()
        acct2 = account_factory(profile=profile)
        response = self.app.get(reverse("accounts.account.list"),
                                user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Accounts</h1>' in response
        assert acct1.name in response
        assert acct2.name not in response


class TestAccountAddView(BaseWebTest):
    def test_view(self):
        acct_type = account_type_factory(profile=self.profile)
        response = self.app.get(reverse("accounts.account.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct1"
        form["description"] = "desc"
        form["account_type"] = acct_type.pk
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully added Account acct1" in response
        assert Account.objects.filter(name="acct1",
                                      profile=self.profile).exists() is True

    def test_permissions(self):
        response = self.app.get(reverse("accounts.account.add"))
        assert response.status_code == 302

    def test_validation(self):
        acct_type = account_type_factory(profile=self.profile)
        response = self.app.get(reverse("accounts.account.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["description"] = "desc"
        form["account_type"] = acct_type.pk
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_name_uniqueness(self):
        acct_type = account_type_factory(profile=self.profile)
        account_factory(name="acct1")
        response = self.app.get(reverse("accounts.account.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct1"
        form["description"] = "desc"
        form["account_type"] = acct_type.pk
        response = form.submit()
        assert response.status_code == 200
        assert "Account with this Name already exists" in response


class TestAccountEditView(BaseWebTest):
    def test_view(self):
        acct = account_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account.edit",
                                        args=[acct.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct2"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully updated Account acct2" in response

    def test_permissions(self):
        acct = account_factory(profile=self.profile)
        response = self.app.get(reverse("accounts.account.edit",
                                        args=[acct.pk]))
        assert response.status_code == 302

    def test_validation(self):
        acct = account_factory(profile=self.profile, name="acct1")
        response = self.app.get(reverse("accounts.account.edit",
                                        args=[acct.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = ""
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_isolation(self):
        profile = profile_factory()
        acct = account_factory(profile=profile, name="acct1")
        response = self.app.get(reverse("accounts.account.edit",
                                        args=[acct.pk]), user=self.user,
                                expect_errors=True)
        assert response.status_code == 404

    def test_name_uniqueness(self):
        account_factory(profile=self.profile, name="acct1")
        acct = account_factory(profile=self.profile, name="acct2")
        response = self.app.get(reverse("accounts.account.edit",
                                        args=[acct.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["name"] = "acct1"
        response = form.submit()
        assert response.status_code == 200
        assert "Account with this Name already exists" in response


class TestAccountDeleteView(BaseWebTest):
    csrf_checks = False

    def test_view(self):
        acct = account_factory(profile=self.profile)
        response = self.app.post(reverse("accounts.account.delete",
                                         args=[acct.pk]),
                                 user=self.user).follow()
        assert response.status_code == 200
        assert "Successfully deleted Account" in response
        assert Account.objects.filter(pk=acct.pk).exists() is False

    def test_permission(self):
        acct = account_factory(profile=self.profile)
        response = self.app.post(reverse("accounts.account.delete",
                                         args=[acct.pk])).follow()
        assert response.status_code == 200
        assert Account.objects.filter(pk=acct.pk).exists() is True

    def test_isolation(self):
        profile = profile_factory()
        acct = account_factory(profile=profile)
        response = self.app.post(reverse("accounts.account.delete",
                                         args=[acct.pk]),
                                 user=self.user, expect_errors=True)
        assert response.status_code == 404
        assert Account.objects.filter(pk=acct.pk).exists() is True
