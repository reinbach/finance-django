import datetime

from django.contrib.auth.models import User
from django.db import models


def get_user_profile(user):
    return Profile.objects.get(user=user)


class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    is_active = models.BooleanField(default=True)
    current_year = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{0}".format(self.user.username)

    @property
    def year(self):
        if self.current_year is not None:
            return self.current_year
        return datetime.date.today().year
