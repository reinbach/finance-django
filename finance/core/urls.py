from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from finance.core.views import ProfileView

urlpatterns = patterns(
    "",
    url("^$", login_required(ProfileView.as_view()),
        name="profile.home"),
)
