import datetime
import pytest

from decimal import Decimal
from finance.accounts.models import Account, AccountType, Transaction
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

    def test_get_total(self):
        a1 = account_factory()
        a2 = account_factory()
        transaction_factory(account_debit=a1, account_credit=a2,
                            amount="10.00")
        transaction_factory(account_debit=a1, account_credit=a2, amount="5.00")
        assert a1.get_total(a1.debit.all()) == 15.00
        assert a1.get_total(a1.credit.all()) == 0
        assert a2.get_total(a2.debit.all()) == 0
        assert a2.get_total(a2.credit.all()) == 15.00

    def test_balance(self):
        a = account_factory()
        transaction_factory(account_debit=a, amount="5")
        transaction_factory(account_credit=a, amount="2.5")
        transaction_factory(account_debit=a, amount="15.15")
        assert a.balance == Decimal("17.65")

    def test_balance_empty(self):
        a = account_factory()
        assert a.balance == 0

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


@pytest.mark.django_db
class TestTransaction():
    def test_unicode(self):
        a1 = account_factory(name="acct1")
        a2 = account_factory(name="acct2")
        t = Transaction(account_debit=a1, account_credit=a2, amount="10.00",
                        summary="quick trx")
        assert unicode(t) == "quick trx 10.00"
