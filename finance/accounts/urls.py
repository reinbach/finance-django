from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from finance.accounts.views import (DashboardView, SettingsView,
                                    AccountTypeAddView, AccountTypeEditView,
                                    AccountTypeDeleteView, AccountView,
                                    AccountAddView, AccountEditView,
                                    AccountDeleteView)


urlpatterns = patterns(
    "",
    url("^$", login_required(DashboardView.as_view()),
        name="accounts.dashboard"),
    url("^settings/$", login_required(SettingsView.as_view()),
        name="accounts.settings"),

    # account types
    url("^settings/account_type/add/$",
        login_required(AccountTypeAddView.as_view()),
        name="accounts.account_type.add"),
    url("^settings/account_type/edit/(?P<pk>\d+)/$",
        login_required(AccountTypeEditView.as_view()),
        name="accounts.account_type.edit"),
    url("^settings/account_type/delete/(?P<pk>\d+)/$",
        login_required(AccountTypeDeleteView.as_view()),
        name="accounts.account_type.delete"),

    # accounts
    url("^list/$", login_required(AccountView.as_view()),
        name="accounts.account.list"),
    url("^add/$", login_required(AccountAddView.as_view()),
        name="accounts.account.add"),
    url("^edit/(?P<pk>\d+)/$", login_required(AccountEditView.as_view()),
        name="accounts.account.edit"),
    url("^delete/(?P<pk>\d+)/$", login_required(AccountDeleteView.as_view()),
        name="accounts.account.delete"),
)
