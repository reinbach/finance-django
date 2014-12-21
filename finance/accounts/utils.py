from finance.accounts.models import Account, AccountType

BLANK_OPTION = [("", "-" * 9)]


def get_account_type_choices(user):
    valid_options = [(x.pk, x.name) for x in AccountType.objects.filter(
        profile__user=user
    )]
    return BLANK_OPTION + valid_options


def get_account_choices(user):
    options = Account.objects.filter(profile__user=user).order_by(
        "account_type"
    )
    acct_type = None
    valid_options = []
    for option in options:
        if option.account_type != acct_type:
            acct_type = option.account_type
            valid_options.append(("", acct_type.name))
        valid_options.append((option.pk, "- {0}".format(option.name)))
    return BLANK_OPTION + valid_options
