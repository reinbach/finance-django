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
        expense_type = account_type_factory(profile=p, yearly=True,
                                            default_type="DEBIT")
        asset_type = account_type_factory(profile=p)
        exp = account_factory(profile=p, account_type=expense_type)
        bank = account_factory(profile=p, account_type=asset_type)
        trx = transaction_factory(account_debit=exp, account_credit=bank,
                                  amount=10.00,
                                  date=datetime.date(p.year, 5, 1))
        trxs = get_monthly_totals(p)
        assert len(trxs) == 1
        assert trxs[5] == [{"label": exp.name, "balance": trx.amount}]

    def test_debit_multiple_trx(self):
        p = profile_factory()
        expense_type = account_type_factory(profile=p, yearly=True,
                                        default_type="DEBIT")
        asset_type = account_type_factory(profile=p)
        exp = account_factory(profile=p, account_type=expense_type)
        bank = account_factory(profile=p, account_type=asset_type)
        trx1 = transaction_factory(account_debit=exp, account_credit=bank,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=exp, account_credit=bank,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trx3 = transaction_factory(account_debit=bank, account_credit=exp,
                                   amount=5.00,
                                   date=datetime.date(p.year, 5, 2))
        trxs = get_monthly_totals(p)
        assert len(trxs) == 1
        assert trxs[5] == [
            {"label": exp.name,
             "balance": trx1.amount + trx2.amount - trx3.amount}
        ]

    def test_debit_multiple(self):
        p = profile_factory()
        expense_type = account_type_factory(profile=p, yearly=True,
                                          default_type="DEBIT")
        asset_type = account_type_factory(profile=p)
        bank = account_factory(profile=p, account_type=asset_type)
        exp1 = account_factory(profile=p, account_type=expense_type)
        exp2 = account_factory(profile=p, account_type=expense_type)
        trx1 = transaction_factory(account_debit=exp1, account_credit=bank,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=exp2, account_credit=bank,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trx3 = transaction_factory(account_debit=bank, account_credit=exp2,
                                   amount=15.00,
                                   date=datetime.date(p.year, 5, 20))
        trx4 = transaction_factory(account_debit=exp1, account_credit=bank,
                                   amount=12.00,
                                   date=datetime.date(p.year, 8, 2))
        trx5 = transaction_factory(account_debit=exp1, account_credit=bank,
                                   amount=28.00,
                                   date=datetime.date(p.year, 8, 12))
        trxs = get_monthly_totals(p)
        assert len(trxs) == 2
        assert trxs[5] == [
            {"label": exp1.name, "balance": trx1.amount},
            {"label": exp2.name, "balance": trx2.amount - trx3.amount}
        ]
        assert trxs[8] == [
            {"label": exp1.name, "balance": trx4.amount + trx5.amount},
        ]

    def test_credit_empty(self):
        p = profile_factory()
        assert get_monthly_totals(p, False) == {}

    def test_credit_single_trx(self):
        p = profile_factory()
        income_type = account_type_factory(profile=p, yearly=True,
                                          default_type="CREDIT")
        asset_type = account_type_factory(profile=p)
        inc = account_factory(profile=p, account_type=income_type)
        bank = account_factory(profile=p, account_type=asset_type)
        trx = transaction_factory(account_debit=bank, account_credit=inc,
                                  amount=10.00,
                                  date=datetime.date(p.year, 5, 1))
        trxs = get_monthly_totals(p, False)
        assert len(trxs) == 1
        assert trxs[5] == [{"label": inc.name, "balance": -trx.amount}]

    def test_credit_multiple_trx(self):
        p = profile_factory()
        income_type = account_type_factory(profile=p, yearly=True,
                                          default_type="CREDIT")
        asset_type = account_type_factory(profile=p)
        inc = account_factory(profile=p, account_type=income_type)
        bank = account_factory(profile=p, account_type=asset_type)
        trx1 = transaction_factory(account_debit=bank, account_credit=inc,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=bank, account_credit=inc,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trxs = get_monthly_totals(p, False)
        assert len(trxs) == 1
        assert trxs[5] == [
            {"label": inc.name, "balance": -trx1.amount - trx2.amount}
        ]

    def test_credit_multiple(self):
        p = profile_factory()
        income_type = account_type_factory(profile=p, yearly=True,
                                          default_type="CREDIT")
        asset_type = account_type_factory(profile=p)
        bank = account_factory(profile=p, account_type=asset_type)
        inc1 = account_factory(profile=p, account_type=income_type)
        inc2 = account_factory(profile=p, account_type=income_type)
        trx1 = transaction_factory(account_debit=bank, account_credit=inc1,
                                   amount=10.00,
                                   date=datetime.date(p.year, 5, 1))
        trx2 = transaction_factory(account_debit=bank, account_credit=inc2,
                                   amount=20.00,
                                   date=datetime.date(p.year, 5, 2))
        trx3 = transaction_factory(account_debit=inc2, account_credit=bank,
                                   amount=15.00,
                                   date=datetime.date(p.year, 5, 20))
        trx4 = transaction_factory(account_debit=bank, account_credit=inc1,
                                   amount=12.00,
                                   date=datetime.date(p.year, 8, 2))
        trx5 = transaction_factory(account_debit=bank, account_credit=inc1,
                                   amount=28.00,
                                   date=datetime.date(p.year, 8, 12))
        trxs = get_monthly_totals(p, False)
        assert len(trxs) == 2
        assert trxs[5] == [
            {"label": inc1.name, "balance": -trx1.amount},
            {"label": inc2.name, "balance": -trx2.amount + trx3.amount}
        ]
        assert trxs[8] == [
            {"label": inc1.name, "balance": -trx4.amount - trx5.amount},
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

    def test_totals(self):
        p = profile_factory(current_year=2010)
        expense_type = account_type_factory(profile=p, yearly=True,
                                        default_type="DEBIT")
        income_type = account_type_factory(profile=p, yearly=True,
                                        default_type="CREDIT")
        asset_type = account_type_factory(profile=p)
        bank = account_factory(profile=p, account_type=asset_type)
        inc1 = account_factory(profile=p, account_type=income_type)
        inc2 = account_factory(profile=p, account_type=income_type)
        exp1 = account_factory(profile=p, account_type=expense_type)
        exp2 = account_factory(profile=p, account_type=expense_type)
        transaction_factory(account_debit=bank, account_credit=inc1,
                            amount=100.00, date=datetime.date(2010, 1, 1))
        transaction_factory(account_debit=bank, account_credit=inc2,
                            amount=10.00, date=datetime.date(2010, 1, 4))
        transaction_factory(account_debit=exp1, account_credit=bank,
                            amount=15.00, date=datetime.date(2010, 1, 6))
        transaction_factory(account_debit=exp2, account_credit=bank,
                            amount=20.00, date=datetime.date(2010, 1, 13))
        transaction_factory(account_debit=exp2, account_credit=bank,
                            amount=25.00, date=datetime.date(2010, 1, 16))
        transaction_factory(account_debit=exp1, account_credit=bank,
                            amount=30.00, date=datetime.date(2010, 2, 1))
        transaction_factory(account_debit=exp1, account_credit=bank,
                            amount=35.00, date=datetime.date(2011, 2, 1))
        monthly_debits_credits = get_monthly_debits_vs_credits(p)
        assert (1, -50) in monthly_debits_credits
        assert (2, 30) in monthly_debits_credits
