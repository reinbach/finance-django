import datetime
import pytest

from finance.accounts.dashboard import (get_months, get_monthly_totals,
                                        get_debits_title, get_credits_title,
                                        get_monthly_debits_vs_credits)
from tests.fixtures import (profile_factory, account_type_factory,
                            account_factory, transaction_factory)


class TestGetMonths():
    def test_full_year(self):
        months = get_months(2010)
        assert len(months) == 12

    def test_future_year(self):
        assert get_months(datetime.date.today().year + 1) == []

    def test_current_year(self):
        months = get_months(datetime.date.today().year)
        assert len(months) == datetime.date.today().month


@pytest.mark.django_db
class TestGetMonthlyAccounts():
    def test_debit_empty(self):
        p = profile_factory()
        assert get_monthly_totals(p) == {}

    def test_debit_single_trx(self):
        p = profile_factory()
        acct_type1 = account_type_factory(profile=p, yearly=True,
                                          default_type="DEBIT")
        acct_type2 = account_type_factory(profile=p)
        acct1 = account_factory(profile=p, account_type=acct_type1)
        acct2 = account_factory(profile=p, account_type=acct_type2)
        trx = transaction_factory(account_debit=acct1, account_credit=acct2,
                                  amount=10.00,
                                  date=datetime.date(p.year, 5, 1))
        trxs = get_monthly_totals(p)
        assert len(trxs) == 1
        assert trxs[5] == [{"label": acct1.name, "balance": trx.amount}]

    def test_debit_multiple_trx(self):
        p = profile_factory()
        acct_type1 = account_type_factory(profile=p, yearly=True,
                                          default_type="DEBIT")
        acct_type2 = account_type_factory(profile=p)
        acct1 = account_factory(profile=p, account_type=acct_type1)
        acct2 = account_factory(profile=p, account_type=acct_type2)
        trx1 = transaction_factory(account_debit=acct1, account_credit=acct2,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=acct1, account_credit=acct2,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trxs = get_monthly_totals(p)
        assert len(trxs) == 1
        assert trxs[5] == [
            {"label": acct1.name, "balance": trx1.amount + trx2.amount}
        ]

    def test_debit_multiple(self):
        p = profile_factory()
        acct_type1 = account_type_factory(profile=p, yearly=True,
                                          default_type="DEBIT")
        acct_type2 = account_type_factory(profile=p)
        acct1 = account_factory(profile=p, account_type=acct_type1)
        acct2 = account_factory(profile=p, account_type=acct_type2)
        acct3 = account_factory(profile=p, account_type=acct_type1)
        trx1 = transaction_factory(account_debit=acct1, account_credit=acct2,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=acct3, account_credit=acct2,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trx3 = transaction_factory(account_debit=acct2, account_credit=acct3,
                                   amount=15.00,
                                   date=datetime.date(p.year, 5, 20))
        trx4 = transaction_factory(account_debit=acct1, account_credit=acct2,
                                   amount=12.00,
                                   date=datetime.date(p.year, 8, 2))
        trx5 = transaction_factory(account_debit=acct1, account_credit=acct2,
                                   amount=28.00,
                                   date=datetime.date(p.year, 8, 12))
        trxs = get_monthly_totals(p)
        assert len(trxs) == 2
        assert trxs[5] == [
            {"label": acct3.name, "balance": trx2.amount - trx3.amount},
            {"label": acct1.name, "balance": trx1.amount}
        ]
        assert trxs[8] == [
            {"label": acct1.name, "balance": trx4.amount + trx5.amount},
        ]

    def test_credit_empty(self):
        p = profile_factory()
        assert get_monthly_totals(p, False) == {}

    def test_credit_single_trx(self):
        p = profile_factory()
        acct_type1 = account_type_factory(profile=p, yearly=True,
                                          default_type="CREDIT")
        acct_type2 = account_type_factory(profile=p)
        acct1 = account_factory(profile=p, account_type=acct_type1)
        acct2 = account_factory(profile=p, account_type=acct_type2)
        trx = transaction_factory(account_debit=acct2, account_credit=acct1,
                                  amount=10.00,
                                  date=datetime.date(p.year, 5, 1))
        trxs = get_monthly_totals(p, False)
        assert len(trxs) == 1
        assert trxs[5] == [{"label": acct1.name, "balance": -trx.amount}]

    def test_credit_multiple_trx(self):
        p = profile_factory()
        acct_type1 = account_type_factory(profile=p, yearly=True,
                                          default_type="CREDIT")
        acct_type2 = account_type_factory(profile=p)
        acct1 = account_factory(profile=p, account_type=acct_type1)
        acct2 = account_factory(profile=p, account_type=acct_type2)
        trx1 = transaction_factory(account_debit=acct2, account_credit=acct1,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=acct2, account_credit=acct1,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trxs = get_monthly_totals(p, False)
        assert len(trxs) == 1
        assert trxs[5] == [
            {"label": acct1.name, "balance": -trx1.amount - trx2.amount}
        ]

    def test_credit_multiple(self):
        p = profile_factory()
        acct_type1 = account_type_factory(profile=p, yearly=True,
                                          default_type="CREDIT")
        acct_type2 = account_type_factory(profile=p)
        acct1 = account_factory(profile=p, account_type=acct_type1)
        acct2 = account_factory(profile=p, account_type=acct_type2)
        acct3 = account_factory(profile=p, account_type=acct_type1)
        trx1 = transaction_factory(account_debit=acct2, account_credit=acct1,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=acct2, account_credit=acct3,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trx3 = transaction_factory(account_debit=acct3, account_credit=acct2,
                                   amount=15.00,
                                   date=datetime.date(p.year, 5, 20))
        trx4 = transaction_factory(account_debit=acct2, account_credit=acct1,
                                   amount=12.00,
                                   date=datetime.date(p.year, 8, 2))
        trx5 = transaction_factory(account_debit=acct2, account_credit=acct1,
                                   amount=28.00,
                                   date=datetime.date(p.year, 8, 12))
        trxs = get_monthly_totals(p, False)
        assert len(trxs) == 2
        assert trxs[5] == [
            {"label": acct1.name, "balance": -trx1.amount},
            {"label": acct3.name, "balance": -trx2.amount + trx3.amount}
        ]
        assert trxs[8] == [
            {"label": acct1.name, "balance": -trx4.amount - trx5.amount},
        ]


@pytest.mark.django_db
class TestGetDebitsTitle():
    def test_empty(self):
        p = profile_factory()
        assert get_debits_title(p) == ""

    def test_single(self):
        p = profile_factory()
        account_type_factory(profile=p, name="Expenses", yearly=True,
                             default_type="DEBIT")
        account_type_factory(profile=p, name="Income", yearly=True,
                             default_type="CREDIT")
        account_type_factory(profile=p, name="Liabilities", yearly=False,
                             default_type="CREDIT")
        assert get_debits_title(p) == "Expenses"

    def test_multiple(self):
        p = profile_factory()
        account_type_factory(profile=p, name="Exp1", yearly=True,
                             default_type="DEBIT")
        account_type_factory(profile=p, name="Exp2", yearly=True,
                             default_type="DEBIT")
        assert get_debits_title(p) == "Exp1/Exp2"

    def test_isolation(self):
        p = profile_factory()
        account_type_factory(name="Expenses", yearly=True,
                             default_type="DEBIT")
        assert get_debits_title(p) == ""


@pytest.mark.django_db
class TestGetCreditsTitle():
    def test_empty(self):
        p = profile_factory()
        assert get_credits_title(p) == ""

    def test_single(self):
        p = profile_factory()
        account_type_factory(profile=p, name="Income", yearly=True,
                             default_type="CREDIT")
        account_type_factory(profile=p, name="Liabilities", yearly=False,
                             default_type="CREDIT")
        account_type_factory(profile=p, name="Expenses", yearly=True,
                             default_type="DEBIT")
        assert get_credits_title(p) == "Income"

    def test_multiple(self):
        p = profile_factory()
        account_type_factory(profile=p, name="Inc1", yearly=True,
                             default_type="CREDIT")
        account_type_factory(profile=p, name="Inc2", yearly=True,
                             default_type="CREDIT")
        assert get_credits_title(p) == "Inc1/Inc2"

    def test_isolation(self):
        p = profile_factory()
        account_type_factory(name="Income", yearly=True, default_type="CREDIT")
        assert get_credits_title(p) == ""


@pytest.mark.django_db
class TestMonthlyDebitsVsCredits():
    def test_future_year(self):
        p = profile_factory(current_year=datetime.date.today().year + 1)
        assert get_monthly_debits_vs_credits(p) == []

    def test_empty(self):
        p = profile_factory(current_year=2010)
        assert get_monthly_debits_vs_credits(p) == [
            (x, 0) for x in range(1, 13)
        ]
