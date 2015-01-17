import datetime

from collections import defaultdict
from finance.accounts.models import Account


def get_months(year):
    current_year = datetime.date.today().year
    if int(year) > current_year:
        return []
    elif int(year) == current_year:
        month_count = datetime.date.today().month
    else:
        month_count = 12
    return [i for i in range(1, month_count + 1)]


def get_monthly_debits(profile):
    """Totals for the debit accounts broken into the months
    of the selected year
    """
    debits = Account.objects.filter(profile=profile).debits()
    monthly_debits = defaultdict(dict)
    month_debit_covered = []
    months = get_months(profile.year)
    for debit in debits:
        for month in months:
            for trx in debit.transactions(month=month):
                if trx.date.month not in monthly_debits:
                    monthly_debits[trx.date.month] = []
                if (trx.date.month, debit.name) not in month_debit_covered:
                    month_debit_covered.append((trx.date.month, debit.name))
                    monthly_debits[trx.date.month].append(
                        {"label": debit.name, "balance": trx.balance}
                    )
    return monthly_debits
