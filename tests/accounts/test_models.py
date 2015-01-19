import datetime
import pytest

from decimal import Decimal
from finance.accounts.models import Account, AccountType, Transaction
from tests.fixtures import (account_factory, account_type_factory,
                            transaction_factory, profile_factory)


@pytest.mark.django_db
class TestAccountType():
    def test_unicode(self):
        a = AccountType(name="acct-type")
        assert unicode(a) == "acct-type"

    def test_yearly(self):
        at1 = account_type_factory(yearly=True)
        at2 = account_type_factory(yearly=False)
        at_list = AccountType.objects.yearly()
        assert at1 in at_list
        assert at2 not in at_list

    def test_debits(self):
        at1 = account_type_factory(yearly=True, default_type="DEBIT")
        at2 = account_type_factory(yearly=True, default_type="CREDIT")
        at3 = account_type_factory(yearly=False, default_type="DEBIT")
        at_list = AccountType.objects.debits()
        assert at1 in at_list
        assert at2 not in at_list
        assert at3 not in at_list

    def test_credits(self):
        at1 = account_type_factory(yearly=True, default_type="DEBIT")
        at2 = account_type_factory(yearly=True, default_type="CREDIT")
        at3 = account_type_factory(yearly=False, default_type="CREDIT")
        at_list = AccountType.objects.credits()
        assert at1 not in at_list
        assert at2 in at_list
        assert at3 not in at_list


@pytest.mark.django_db
class TestAccount():
    def test_unicode(self):
        at = account_type_factory(name="acct-type")
        a = Account(name="acct", account_type=at)
        assert unicode(a) == "acct"

    def test_balance(self):
        year = 2010
        p = profile_factory(current_year=year)
        a = account_factory(profile=p)
        transaction_factory(account_debit=a, amount="5",
                            date=datetime.date(year, 3, 2))
        transaction_factory(account_credit=a, amount="2.5",
                            date=datetime.date(year, 4, 6))
        transaction_factory(account_debit=a, amount="15.15",
                            date=datetime.date(year, 8, 1))
        # this trx is outside of the current year and should be ignored
        transaction_factory(account_debit=a, amount="20.00",
                            date=datetime.date(year + 1, 1, 8))
        assert a.balance() == Decimal("17.65")

    def test_balance_empty(self):
        a = account_factory()
        assert a.balance() == 0

    def test_balance_subaccounts(self):
        year = 2010
        p = profile_factory(current_year=year)
        acct1 = account_factory(profile=p, parent=None, is_category=True)
        acct2 = account_factory(profile=p, parent=acct1, is_category=True)
        acct3 = account_factory(profile=p, parent=acct2, is_category=False)
        acct4 = account_factory(profile=p, parent=acct1, is_category=False)
        transaction_factory(account_debit=acct3, amount="5.25",
                            date=datetime.date(year, 2, 1))
        transaction_factory(account_debit=acct3, amount="2.50",
                            date=datetime.date(year, 4, 7))
        transaction_factory(account_debit=acct4, amount="10.10",
                            date=datetime.date(year, 7, 19))
        transaction_factory(account_credit=acct4, amount="1.00",
                            date=datetime.date(year, 12, 14))
        # this trx is outside of the current year and should be ignored
        transaction_factory(account_credit=acct4, amount="20.00",
                            date=datetime.date(year + 1, 1, 4))
        assert acct1.balance() == Decimal("16.85")
        assert acct2.balance() == Decimal("7.75")

    def test_transactions(self):
        year = 2010
        p = profile_factory(current_year=year)
        a = account_factory(profile=p)
        t1 = transaction_factory(account_debit=a, amount="5",
                                 date=datetime.date(year, 1, 1))
        t2 = transaction_factory(account_credit=a, amount="2.5",
                                 date=datetime.date(year, 4, 1))
        t3 = transaction_factory(account_debit=a, amount="15.15",
                                 date=datetime.date(year, 4, 2))
        # this trx is outside of the current year and should be ignored
        transaction_factory(account_debit=a, amount="20.20",
                            date=datetime.date(year + 1, 1, 2))
        trxs = a.transactions()
        assert len(trxs) == 3
        assert trxs[0] == t3
        assert trxs[0].balance == Decimal("17.65")
        assert trxs[1] == t2
        assert trxs[1].balance == Decimal("2.50")
        assert trxs[2] == t1
        assert trxs[2].balance == Decimal("5.00")

    def test_subaccounts(self):
        a = account_factory(name="acct1", parent=None)
        b = account_factory(name="acct2", parent=a)
        assert b in list(a.subaccounts())
        assert list(b.subaccounts()) == []


@pytest.mark.django_db
class TestTransaction():
    def test_unicode(self):
        a1 = account_factory(name="acct1")
        a2 = account_factory(name="acct2")
        t = Transaction(account_debit=a1, account_credit=a2, amount="10.00",
                        summary="quick trx")
        assert unicode(t) == "quick trx 10.00"
