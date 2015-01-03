import datetime
import os
import pytest

from django.conf import settings
from finance.accounts.trx_import import TransactionsImport
from tests.fixtures import account_factory, transaction_factory


@pytest.mark.django_db
class TestTransactionsImport():
    TEST_FILE = os.path.join(settings.BASE_DIR,
                             "tests/import_test_chase_sample.csv")

    def test_init(self):
        a = account_factory()
        t = TransactionsImport(a.pk, self.TEST_FILE)
        assert t.main_account_pk == a.pk
        assert t.filename == self.TEST_FILE
        assert t.transactions == []
        assert t.year == datetime.date.today().year

    def test_get_file_type(self):
        a = account_factory()
        t = TransactionsImport(a.pk, "example.csv")
        assert t.get_file_type() == "CSV"

    def test_get_file_type_pdf(self):
        a = account_factory()
        t = TransactionsImport(a.pk, "example.pdf")
        assert t.get_file_type() == "PDF"

    def test_get_file_type_default(self):
        a = account_factory()
        t = TransactionsImport(a.pk, "example.png")
        assert t.get_file_type() == "CSV"

    def test_is_duplicate(self):
        trx = {"summary": "sum", "amount": "10.00",
               "date": datetime.date(2010, 1, 1)}
        transaction_factory(summary=trx["summary"],
                            amount=trx["amount"], date="2010-01-01")
        a = account_factory()
        t = TransactionsImport(a.pk, self.TEST_FILE)
        assert t.is_duplicate(trx) is True

    def test_is_duplicate_false(self):
        trx = {"summary": "sum", "amount": "10.00",
               "date": datetime.date(2010, 1, 1)}
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

    def test_get_account_none_not_debit_or_credit(self):
        acct1 = account_factory()
        acct2 = account_factory()
        acct3 = account_factory()
        transaction_factory(account_debit=acct1, account_credit=acct3,
                            summary="sum")
        t = TransactionsImport(acct2.pk, self.TEST_FILE)
        assert t.get_account("sum") is None

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


@pytest.mark.django_db
class TestChaseCSVTransactionsImport():
    TEST_FILE = os.path.join(settings.BASE_DIR,
                             "tests/import_test_chase_sample.csv")

    def test_map_field(self):
        trx_import = {"Post Date": "01/01/2010",
                      "Description": "sum", "Amount": "15.25"}
        acct1 = account_factory()
        t = TransactionsImport(acct1.pk, self.TEST_FILE)
        trx = t.map_fields(trx_import)
        assert trx["date"] == datetime.datetime(2010, 1, 1, 0, 0, 0)
        assert trx["summary"] == "sum"
        assert trx["amount"] == "15.25"

    def test_map_field_unknown(self):
        trx_import = {"Date": "01/01/2010",
                      "Description": "sum", "Amount": "15.25"}
        acct1 = account_factory()
        t = TransactionsImport(acct1.pk, self.TEST_FILE)
        with pytest.raises(Exception):
            t.map_fields(trx_import)

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


@pytest.mark.django_db
class TestCapitalOne360TransactionsImport():
    TEST_FILE = os.path.join(settings.BASE_DIR,
                             "tests/import_test_capitalone360_sample.csv")

    def test_map_field(self):
        trx_import = {"BANK ID": "123", "Account Number": "321",
                      "Account Type": "Savings", "Balance": "10.25",
                      "Start Date": "2010-01-01", "End Date": "2010-01-31",
                      "Transaction Type": "Credit",
                      "Transaction Date": "2010-01-01",
                      "Transaction Amount": "2.15", "Transaction ID": "112",
                      " Transaction Description": "Interest Paid"}
        acct1 = account_factory()
        t = TransactionsImport(acct1.pk, self.TEST_FILE)
        trx = t.map_fields(trx_import)
        assert trx["date"] == datetime.datetime(2010, 1, 1, 0, 0, 0)
        assert trx["summary"] == "Interest Paid"
        assert trx["amount"] == "2.15"

    def test_parse_file(self):
        acct = account_factory()
        t = TransactionsImport(acct.pk, self.TEST_FILE)
        t.parse_file()
        assert len(t.transactions) == 3

    def test_parse_file_duplicate(self):
        acct = account_factory()
        transaction_factory(account_credit=acct,
                            summary="Monthly Interest Paid",
                            amount="0.22", date="2014-11-30")
        t = TransactionsImport(acct.pk, self.TEST_FILE)
        t.parse_file()
        assert len(t.transactions) == 3
        assert t.transactions[0]["DELETE"] is True
        assert t.transactions[1]["DELETE"] is False
        assert t.transactions[2]["DELETE"] is False


@pytest.mark.django_db
class TestChasePDFTransactionsImport():
    TEST_FILE = os.path.join(settings.BASE_DIR,
                             "tests/import_test_chase_sample.pdf")

    def test_parse_file(self):
        acct = account_factory()
        t = TransactionsImport(acct.pk, self.TEST_FILE)
        t.parse_file()
        assert len(t.transactions) == 69

    def test_parse_file_duplicate(self):
        acct = account_factory()
        transaction_factory(account_credit=acct,
                            summary="THE OXFORD HOUSE INN FRYEBURG ME",
                            amount="111.26", date="2013-12-14")
        t = TransactionsImport(acct.pk, self.TEST_FILE, year=2013)
        t.parse_file()
        assert len(t.transactions) == 69
        assert t.transactions[0]["DELETE"] is True
        assert t.transactions[-1]["DELETE"] is False
