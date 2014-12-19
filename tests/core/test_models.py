import pytest

from finance.core.models import get_user_profile
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