from django.conf.urls import patterns, url
from finance.accounts.views import (DashboardView, SettingsView,
                                    AccountTypeAddView, AccountTypeEditView,
                                    AccountTypeDeleteView)


urlpatterns = patterns(
    "",
    url("^$", DashboardView.as_view(), name="accounts.dashboard"),
    url("^settings/$", SettingsView.as_view(), name="accounts.settings"),

    # account types
    url("^settings/account_type/add/$", AccountTypeAddView.as_view(),
        name="accounts.account_type.add"),
    url("^settings/account_type/edit/(?P<pk>\d+)/$",
        AccountTypeEditView.as_view(), name="accounts.account_type.edit"),
    url("^settings/account_type/delete/(?P<pk>\d+)/$",
        AccountTypeDeleteView.as_view(), name="accounts.account_type.delete"),
)