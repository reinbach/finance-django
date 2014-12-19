from django.contrib.auth.models import User
from django.db import models


def get_user_profile(user):
    return Profile.objects.get(user=user)


class Profile(models.Model):
    user = models.ForeignKey(User)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{0}".format(self.user.username)
