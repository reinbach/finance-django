import datetime
import os
import pytest

from decimal import Decimal
from django.conf import settings
from django_dynamic_fixture.ddf import BadDataError
from finance.accounts.models import (Account, AccountType, Transaction,
                                     TransactionsImport)
from tests.fixtures import (account_factory, account_type_factory,
                            transaction_factory)


class TestAccountType():
    def test_unicode(self):
        a = AccountType(name="acct-type")
        assert unicode(a) == "acct-type"


@pytest.mark.django_db
class TestAccount():
    def test_unicode(self):
        at = account_type_factory(name="acct-type")
        a = Account(name="acct", account_type=at)
        assert unicode(a) == "acct"

    def test_balance(self):
        a = account_factory()
        transaction_factory(account_debit=a, amount="5")
        transaction_factory(account_credit=a, amount="2.5")
        transaction_factory(account_debit=a, amount="15.15")
        assert a.balance() == Decimal("17.65")

    def test_balance_empty(self):
        a = account_factory()
        assert a.balance() == 0

    def test_balance_subaccounts(self):
        acct1 = account_factory(parent=None, is_category=True)
        acct2 = account_factory(parent=acct1, is_category=True)
        acct3 = account_factory(parent=acct2, is_category=False)
        acct4 = account_factory(parent=acct1, is_category=False)
        transaction_factory(account_debit=acct3, amount="5.25")
        transaction_factory(account_debit=acct3, amount="2.50")
        transaction_factory(account_debit=acct4, amount="10.10")
        transaction_factory(account_credit=acct4, amount="1.00")
        assert acct1.balance() == Decimal("16.85")
        assert acct2.balance() == Decimal("7.75")

    def test_transactions(self):
        a = account_factory()
        t1 = transaction_factory(account_debit=a, amount="5",
                                 date=datetime.date(2010, 1, 1))
        t2 = transaction_factory(account_credit=a, amount="2.5",
                                 date=datetime.date(2010, 4, 1))
        t3 = transaction_factory(account_debit=a, amount="15.15",
                                 date=datetime.date(2010, 4, 2))
        trxs = a.transactions()
        assert len(trxs) == 3
        assert trxs[0] == (t1, Decimal("5.00"))
        assert trxs[1] == (t2, Decimal("2.50"))
        assert trxs[2] == (t3, Decimal("17.65"))

    def test_subaccounts(self):
        a = account_factory(name="acct1", parent=None)
        b = account_factory(name="acct2", parent=a)
        assert b in list(a.subaccounts())
        assert list(b.subaccounts()) == []

    def test_uniqueness(self):
        a = account_factory(name="acct1")
        account_factory(name="acct1")
        with pytest.raises(BadDataError):
            account_factory(name="acct1", account_type=a.account_type)


@pytest.mark.django_db
class TestTransaction():
    def test_unicode(self):
        a1 = account_factory(name="acct1")
        a2 = account_factory(name="acct2")
        t = Transaction(account_debit=a1, account_credit=a2, amount="10.00",
                        summary="quick trx")
        assert unicode(t) == "quick trx 10.00"


@pytest.mark.django_db
class TestTransactionsImport():
    TEST_FILE = os.path.join(settings.BASE_DIR, "tests/import_test_sample.csv")

    def test_init(self):
        a = account_factory()
        t = TransactionsImport(a.pk, self.TEST_FILE)
        assert t.main_account_pk == a.pk
        assert t.filename == self.TEST_FILE
        assert t.transactions == []

    def test_is_duplicate(self):
        trx = {"summary": "sum", "amount": "10.00", "date": "1/1/2010"}
        transaction_factory(summary=trx["summary"],
                            amount=trx["amount"], date="2010-01-01")
        a = account_factory()
        t = TransactionsImport(a.pk, self.TEST_FILE)
        assert t.is_duplicate(trx) is True

    def test_is_duplicate_false(self):
        trx = {"summary": "sum", "amount": "10.00", "date": "01/01/2010"}
        transaction_factory(summary=trx["summary"],
                            amount=trx["amount"])
        a = account_factory()
        t = TransactionsImport(a.pk, self.TEST_FILE)
        assert t.is_duplicate(trx) is False

    def test_get_account_debit(self):
        acct1 = account_factory()
        acct2 = account_factory()
        transaction_factory(account_debit=acct1, account_credit=acct2,
                            summary="sum")
        t = TransactionsImport(acct1.pk, self.TEST_FILE)
        assert t.get_account("sum") == acct2.pk

    def test_get_account_credit(self):
        acct1 = account_factory()
        acct2 = account_factory()
        transaction_factory(account_debit=acct1, account_credit=acct2,
                            summary="sum")
        t = TransactionsImport(acct2.pk, self.TEST_FILE)
        assert t.get_account("sum") == acct1.pk

    def test_get_account_none(self):
        acct1 = account_factory()
        acct2 = account_factory()
        transaction_factory(account_debit=acct1, account_credit=acct2,
                            summary="sum")
        t = TransactionsImport(acct2.pk, self.TEST_FILE)
        assert t.get_account("sumelse") is None

    def test_set_accounts_debit(self):
        acct1 = account_factory()
        acct2 = account_factory()
        transaction_factory(account_debit=acct1, account_credit=acct2,
                            summary="sum")
        trx = {"summary": "sum", "amount": "10.00", "date": "01/01/2010"}
        t = TransactionsImport(acct1.pk, self.TEST_FILE)
        t.set_accounts(trx)
        assert trx["account_debit"] == acct1.pk
        assert trx["account_credit"] == acct2.pk
        assert trx["amount"] == "10.00"

    def test_set_accounts_credit(self):
        acct1 = account_factory()
        acct2 = account_factory()
        transaction_factory(account_debit=acct1, account_credit=acct2,
                            summary="sum")
        trx = {"summary": "sum", "amount": "-10.00", "date": "01/01/2010"}
        t = TransactionsImport(acct1.pk, self.TEST_FILE)
        t.set_accounts(trx)
        assert trx["account_debit"] == acct2.pk
        assert trx["account_credit"] == acct1.pk
        assert trx["amount"] == "10.00"

    def test_map_field(self):
        trx_import = {"Post Date": "2010-01-01", "Description": "sum",
        "Amount": "15.25"}
        acct1 = account_factory()
        t = TransactionsImport(acct1.pk, self.TEST_FILE)
        trx = t.map_fields(trx_import)
        assert trx["date"] == "2010-01-01"
        assert trx["summary"] == "sum"
        assert trx["amount"] == "15.25"

    def test_parse_file(self):
        acct = account_factory()
        t = TransactionsImport(acct.pk, self.TEST_FILE)
        t.parse_file()
        assert len(t.transactions) == 2

    def test_parse_file_duplicate(self):
        acct = account_factory()
        transaction_factory(account_credit=acct, summary="SPICE & GRAIN",
                            amount="76.35", date="2013-02-22")
        t = TransactionsImport(acct.pk, self.TEST_FILE)
        t.parse_file()
        assert len(t.transactions) == 2
        assert t.transactions[0]["DELETE"] is True
        assert t.transactions[1]["DELETE"] is False
