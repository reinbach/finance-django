from finance.accounts.models import Account, AccountType

BLANK_OPTION = [("", "-" * 9)]


def get_account_type_choices(user):
    valid_options = [(x.pk, x.name) for x in AccountType.objects.filter(
        profile__user=user
    )]
    return BLANK_OPTION + valid_options


def get_account_choices(user):
    options = Account.objects.filter(profile__user=user).exclude(
        parent__isnull=False
    )
    acct_type = None
    valid_options = []
    for option in options:
        if option.account_type != acct_type:
            acct_type = option.account_type
            valid_options.append(("", acct_type.name))
        if option.is_category:
            valid_options.append(("", "- {0}".format(option.name)))
            valid_options = valid_options + get_suboptions(option, 1)
        else:
            valid_options.append((option.pk, "- {0}".format(option.name)))
    return BLANK_OPTION + valid_options


def get_suboptions(account, level):
    options = []
    for option in account.subaccounts():
        if option.is_category:
            options.append(("", "{0} {1}".format("-" * (level + 1),
                                                 option.name)))
            new_level = level + 1
            options = options + get_suboptions(option, new_level)
        else:
            options.append((option.pk, "{0} {1}".format("-" * (level + 1),
                                                        option.name)))
    return options
