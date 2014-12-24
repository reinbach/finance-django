import pytest

from finance.accounts.utils import (BLANK_OPTION, get_account_choices,
                                    get_account_type_choices)
from tests.fixtures import (user_factory, profile_factory, account_factory,
                            account_type_factory)


@pytest.mark.django_db
class TestGetAccountTypeChoices():
    def test_empty(self):
        user = user_factory()
        assert get_account_type_choices(user) == BLANK_OPTION

    def test_valid_options(self):
        profile = profile_factory()
        acct_type1 = account_type_factory(profile=profile)
        acct_type2 = account_type_factory()
        choices = get_account_type_choices(profile.user)
        assert BLANK_OPTION[0] in choices
        assert (acct_type1.pk, acct_type1.name) in choices
        assert (acct_type2.pk, acct_type2.name) not in choices


@pytest.mark.django_db
class TestGetAccountChoices():
    def test_empty(self):
        user = user_factory()
        assert get_account_choices(user) == BLANK_OPTION

    def test_valid_options(self):
        profile = profile_factory()
        acct_type = account_type_factory(profile=profile)
        acct1 = account_factory(profile=profile, account_type=acct_type,
                                is_category=False, parent=None)
        acct2 = account_factory(is_category=False, parent=None)
        choices = get_account_choices(profile.user)
        assert BLANK_OPTION[0] in choices
        assert ("", acct_type.name) in choices
        assert (acct1.pk, "- {0}".format(acct1.name)) in choices
        assert (acct2.pk, "- {0}".format(acct2.name)) not in choices

    def test_valid_options_categories_only(self):
        profile = profile_factory()
        acct_type = account_type_factory(profile=profile)
        acct1 = account_factory(profile=profile, account_type=acct_type,
                                is_category=True, parent=None)
        acct2 = account_factory(profile=profile, is_category=False,
                                parent=None)
        choices = get_account_choices(profile.user, True)
        assert BLANK_OPTION[0] in choices
        assert ("", acct_type.name) in choices
        assert ("", "- {0}".format(acct1.name)) in choices
        assert (acct2.pk, "- {0}".format(acct2.name)) not in choices

    def test_valid_options_multiple(self):
        profile = profile_factory()
        acct_type1 = account_type_factory(profile=profile)
        acct1a = account_factory(profile=profile, account_type=acct_type1,
                                 is_category=False, parent=None)
        acct1b = account_factory(profile=profile, account_type=acct_type1,
                                 is_category=False, parent=None)
        acct_type2 = account_type_factory(profile=profile)
        acct2 = account_factory(profile=profile, account_type=acct_type2,
                                is_category=False, parent=None)
        acct_type3 = account_type_factory(profile=profile)
        acct3 = account_factory(is_category=False, parent=None)
        choices = get_account_choices(profile.user)
        assert BLANK_OPTION[0] in choices
        assert ("", acct_type1.name) in choices
        assert (acct1a.pk, "- {0}".format(acct1a.name)) in choices
        assert (acct1b.pk, "- {0}".format(acct1b.name)) in choices
        assert ("", acct_type2.name) in choices
        assert (acct2.pk, "- {0}".format(acct2.name)) in choices
        assert ("", acct_type3.name) not in choices
        assert (acct3.pk, "- {0}".format(acct3.name)) not in choices

    def test_valid_options_subaccounts(self):
        profile = profile_factory()
        acct_type1 = account_type_factory(profile=profile)
        acct1 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=True, parent=None)
        acct2 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=True, parent=acct1)
        acct3 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=False, parent=acct2)
        acct4 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=False, parent=acct1)
        choices = get_account_choices(profile.user)
        assert BLANK_OPTION[0] in choices
        assert ("", "- {0}".format(acct1.name)) in choices
        assert ("", "-- {0}".format(acct2.name)) in choices
        assert (acct3.pk, "--- {0}".format(acct3.name)) in choices
        assert (acct4.pk, "-- {0}".format(acct4.name)) in choices

    def test_valid_options_subaccounts_categories_only(self):
        profile = profile_factory()
        acct_type1 = account_type_factory(profile=profile)
        acct1 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=True, parent=None)
        acct2 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=True, parent=acct1)
        acct3 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=False, parent=acct2)
        acct4 = account_factory(profile=profile, account_type=acct_type1,
                                is_category=False, parent=acct1)
        choices = get_account_choices(profile.user, True)
        assert BLANK_OPTION[0] in choices
        assert ("", "- {0}".format(acct1.name)) in choices
        assert ("", "-- {0}".format(acct2.name)) in choices
        assert (acct3.pk, "--- {0}".format(acct3.name)) not in choices
        assert (acct4.pk, "-- {0}".format(acct4.name)) not in choices
