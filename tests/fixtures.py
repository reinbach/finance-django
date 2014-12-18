from django_dynamic_fixture import G
from finance.accounts.models import Account, AccountType, Transaction


def account_type_factory(**kwargs):
    return G(AccountType, **kwargs)


def account_factory(**kwargs):
    if "account_type" not in kwargs:
        kwargs["account_type"] = account_type_factory()
    return G(Account, **kwargs)


def transaction_factory(**kwargs):
    if "account_debit" not in kwargs:
        kwargs["account_debit"] = account_factory()
    if "account_credit" not in kwargs:
        kwargs["account_credit"] = account_factory()
    return G(Transaction, **kwargs)