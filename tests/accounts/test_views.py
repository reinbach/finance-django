import datetime
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from finance.accounts.models import AccountType, Account, Transaction
from decimal import Decimal
from tests.fixtures import (BaseWebTest, account_type_factory, profile_factory,
                            account_factory, transaction_factory)


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
        acct1 = account_factory(profile=self.profile, name="acct1")
        profile = profile_factory()
        acct2 = account_factory(profile=profile, name="acct2")
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
        updated_acct = Account.objects.get(pk=acct.pk)
        assert updated_acct.name == "acct2"

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


class TestTransactionView(BaseWebTest):
    def setUp(self):
        super(TestTransactionView, self).setUp()
        self.acct1 = account_factory(profile=self.profile)
        self.acct2 = account_factory(profile=self.profile)

    def test_view(self):
        transaction_factory(account_debit=self.acct1,
                            account_credit=self.acct2, amount="10.00")
        response = self.app.get(reverse("accounts.transaction.list"),
                                user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Transactions</h1>' in response
        assert self.acct1.name in response
        assert self.acct2.name in response
        assert "10.00" in response

    def test_permission(self):
        response = self.app.get(reverse("accounts.transaction.list"))
        assert response.status_code == 302
        assert '<h1 class="page-header">Transaction</h1>' not in response

    def test_isolation(self):
        transaction_factory(account_debit=self.acct1,
                            account_credit=self.acct2, amount="10.00")
        profile = profile_factory()
        acct1 = account_factory(profile=profile, name="n_acct1")
        acct2 = account_factory(profile=profile, name="n_acct2")
        transaction_factory(account_debit=acct1,
                            account_credit=acct2, amount="5.00")
        response = self.app.get(reverse("accounts.transaction.list"),
                                user=self.user)
        assert response.status_code == 200
        assert '<h1 class="page-header">Transactions</h1>' in response
        assert self.acct1.name in response
        assert self.acct2.name in response
        assert "10.00" in response
        assert acct1.name not in response
        assert acct2.name not in response
        assert "5.00" not in response


class TestTransactionAddView(BaseWebTest):
    def setUp(self):
        super(TestTransactionAddView, self).setUp()
        self.acct1 = account_factory(profile=self.profile)
        self.acct2 = account_factory(profile=self.profile)

    def test_view(self):
        response = self.app.get(reverse("accounts.transaction.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["account_debit"] = self.acct1.pk
        form["account_credit"] = self.acct2.pk
        form["amount"] = "10.00"
        form["summary"] = "short"
        form["description"] = "desc"
        form["date"] = datetime.date(2010, 1, 1)
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully added Transaction" in response
        assert Transaction.objects.filter(
            account_debit=self.acct1,
            account_credit=self.acct2,
            date=datetime.date(2010, 1, 1)
        ).exists() is True

    def test_permissions(self):
        response = self.app.get(reverse("accounts.transaction.add"))
        assert response.status_code == 302

    def test_validation(self):
        response = self.app.get(reverse("accounts.transaction.add"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["account_credit"] = self.acct2.pk
        form["amount"] = "10.00"
        form["summary"] = "short"
        form["description"] = "desc"
        form["date"] = datetime.date(2010, 1, 1)
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response


class TestTransactionEditView(BaseWebTest):
    def setUp(self):
        super(TestTransactionEditView, self).setUp()
        self.acct1 = account_factory(profile=self.profile)
        self.acct2 = account_factory(profile=self.profile)

    def test_view(self):
        trx = transaction_factory(account_debit=self.acct1,
                                  account_credit=self.acct2, amount="10.00")
        response = self.app.get(reverse("accounts.transaction.edit",
                                        args=[trx.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["amount"] = "10"
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully updated Transaction" in response
        updated_trx = Transaction.objects.get(pk=trx.pk)
        assert updated_trx.amount == Decimal("10.00")

    def test_permissions(self):
        trx = transaction_factory(account_debit=self.acct1,
                                  account_credit=self.acct2)
        response = self.app.get(reverse("accounts.transaction.edit",
                                        args=[trx.pk]))
        assert response.status_code == 302

    def test_validation(self):
        trx = transaction_factory(account_debit=self.acct1,
                                  account_credit=self.acct2)
        response = self.app.get(reverse("accounts.transaction.edit",
                                        args=[trx.pk]), user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["amount"] = ""
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_isolation(self):
        profile = profile_factory()
        acct1 = account_factory(profile=profile, name="acct1")
        acct2 = account_factory(profile=profile, name="acct2")
        trx = transaction_factory(account_debit=acct1, account_credit=acct2)
        response = self.app.get(reverse("accounts.transaction.edit",
                                        args=[trx.pk]), user=self.user,
                                expect_errors=True)
        assert response.status_code == 404


class TestTransactionDeleteView(BaseWebTest):
    csrf_checks = False

    def setUp(self):
        super(TestTransactionDeleteView, self).setUp()
        self.acct1 = account_factory(profile=self.profile)
        self.acct2 = account_factory(profile=self.profile)

    def test_view(self):
        trx = transaction_factory(account_debit=self.acct1,
                                  account_credit=self.acct2)
        response = self.app.post(reverse("accounts.transaction.delete",
                                         args=[trx.pk]),
                                 user=self.user).follow()
        assert response.status_code == 200
        assert "Successfully deleted Transaction" in response
        assert Transaction.objects.filter(pk=trx.pk).exists() is False

    def test_permission(self):
        trx = transaction_factory(account_debit=self.acct1,
                                  account_credit=self.acct2)
        response = self.app.post(reverse("accounts.transaction.delete",
                                         args=[trx.pk]))
        assert response.status_code == 302
        assert Transaction.objects.filter(pk=trx.pk).exists() is True

    def test_isolation(self):
        trx = transaction_factory()
        response = self.app.post(reverse("accounts.transaction.delete",
                                         args=[trx.pk]),
                                 user=self.user, expect_errors=True)
        assert response.status_code == 404
        assert Transaction.objects.filter(pk=trx.pk).exists() is True


class TestTransactionImportView(BaseWebTest):
    def setUp(self):
        super(TestTransactionImportView, self).setUp()
        self.acct1 = account_factory(profile=self.profile)
        self.acct2 = account_factory(profile=self.profile)
        self.sample_file = os.path.join(settings.BASE_DIR,
                                        "tests/import_test_sample.csv")

    def test_view(self):
        response = self.app.get(reverse("accounts.transaction.import"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["account_main"] = self.acct1.pk
        form["filename"] = [self.sample_file]
        response = form.submit()
        assert response.status_code == 200
        assert "Confirm Import Transaction" in response
        form = response.forms[1]
        form["form-0-account_debit"] = self.acct2.pk
        form["form-1-account_debit"] = self.acct2.pk
        response = form.submit().follow()
        assert response.status_code == 200
        assert "Successfully added 2 Transactions" in response

    def test_validation(self):
        response = self.app.get(reverse("accounts.transaction.import"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["account_main"] = self.acct1.pk
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_confirm_validation(self):
        response = self.app.get(reverse("accounts.transaction.import"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["account_main"] = self.acct1.pk
        form["filename"] = [self.sample_file]
        response = form.submit()
        assert response.status_code == 200
        assert "Confirm Import Transaction" in response
        form = response.forms[1]
        form["form-0-account_debit"] = self.acct2.pk
        response = form.submit()
        assert response.status_code == 200
        assert "is required" in response

    def test_isolation(self):
        n_acct = account_factory(name="n_acct")
        response = self.app.get(reverse("accounts.transaction.import"),
                                user=self.user)
        assert response.status_code == 200
        assert n_acct.name not in response

    def test_confirm_isolation(self):
        n_acct = account_factory(name="n_acct")
        response = self.app.get(reverse("accounts.transaction.import"),
                                user=self.user)
        assert response.status_code == 200
        form = response.forms[1]
        form["account_main"] = self.acct1.pk
        form["filename"] = [self.sample_file]
        response = form.submit()
        assert response.status_code == 200
        assert "Confirm Import Transaction" in response
        assert n_acct.name not in response