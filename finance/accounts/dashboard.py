import datetime

from collections import defaultdict
from finance.accounts.models import Account, AccountType


def get_months(year):
    current_year = datetime.date.today().year
    if int(year) > current_year:
        return []
    elif int(year) == current_year:
        month_count = datetime.date.today().month
    else:
        month_count = 12
    return [i for i in range(1, month_count + 1)]


def get_monthly_totals(profile, debits=True):
    """Totals for the accounts broken into the months
    of the selected year
    """
    if debits:
        accounts = Account.objects.filter(profile=profile).debits()
    else:
        accounts = Account.objects.filter(profile=profile).credits()
    monthly_accounts = defaultdict(dict)
    month_account_covered = []
    months = get_months(profile.year)
    for month in months:
        for acct in accounts:
            for trx in acct.transactions(month=month):
                if trx.date.month not in monthly_accounts:
                    monthly_accounts[trx.date.month] = []
                if (trx.date.month, acct.name) not in month_account_covered:
                    month_account_covered.append((trx.date.month, acct.name))
                    monthly_accounts[trx.date.month].append(
                        {"label": acct.name, "balance": trx.balance}
                    )
        if month in monthly_accounts.keys():
            monthly_accounts[month].sort(key=lambda d: d["balance"])
    return monthly_accounts


def get_debits_title(profile):
    return "/".join([x.name for x in AccountType.objects.filter(
        profile=profile
    ).debits()])


def get_credits_title(profile):
    return "/".join([x.name for x in AccountType.objects.filter(
        profile=profile
    ).credits()])


def get_monthly_debits_vs_credits(profile):
    monthly_debits = get_monthly_totals(profile)
    monthly_credits = get_monthly_totals(profile, False)
    months = get_months(profile.year)
    monthly_totals = []
    for month in months:
        debits = monthly_debits.get(month, [])
        debit_total = sum([x.get("balance", 0) for x in debits])
        credits = monthly_credits.get(month, [])
        credit_total = sum([x.get("balance", 0) for x in credits])
        monthly_totals.append((month, debit_total + credit_total))
    return monthly_totals
