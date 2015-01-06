import datetime
import pytest

from django.db import IntegrityError
from finance.core.models import get_user_profile, Profile
from tests.fixtures import user_factory, profile_factory


@pytest.mark.django_db
class TestGetUserProfile():
    def test_method(self):
        u = user_factory()
        p = profile_factory(user=u)
        assert get_user_profile(u) == p


@pytest.mark.django_db
class TestProfile():
    def test_unicode(self):
        p = profile_factory(user__username="user")
        assert unicode(p) == "user"

    def test_uniqueness(self):
        u = user_factory()
        profile_factory(user=u)
        with pytest.raises(IntegrityError):
            p = Profile(user=u)
            p.save()

    def test_current_year_none(self):
        p = profile_factory(current_year=None)
        assert p.year == datetime.date.today().year

    def test_current_year(self):
        p = profile_factory(current_year=datetime.date(2010, 5, 16))
        assert p.year == 2010
