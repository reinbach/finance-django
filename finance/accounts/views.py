from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (TemplateView, CreateView, UpdateView,
                                  DeleteView, ListView)
from finance.accounts.models import AccountType, Account


class DashboardView(TemplateView):
    template_name = "accounts/dashboard.html"


class SettingsView(TemplateView):
    template_name = "accounts/settings.html"

    def get_context_data(self, **kwargs):
        kwargs = super(SettingsView, self).get_context_data(**kwargs)
        kwargs["account_types"] = AccountType.objects.all()
        return kwargs


class AccountTypeAddView(CreateView):
    model = AccountType
    success_url = reverse_lazy("accounts.settings")

    def form_valid(self, form):
        response = super(AccountTypeAddView, self).form_valid(form)
        messages.success(self.request,
                         u"Succcessfully added Account Type {0}".format(
                             form.cleaned_data["name"]
                         )
        )
        return response


class AccountTypeEditView(UpdateView):
    model = AccountType
    success_url = reverse_lazy("accounts.settings")

    def form_valid(self, form):
        response = super(AccountTypeEditView, self).form_valid(form)
        messages.success(self.request,
                         u"Succcessfully updated Account Type {0}".format(
                             form.cleaned_data["name"]
                         )
        )
        return response


class AccountTypeDeleteView(DeleteView):
    model = AccountType
    success_url = reverse_lazy("accounts.settings")

    def post(self, request, *args, **kwargs):
        response = super(AccountTypeDeleteView, self).post(request, *args,
                                                           **kwargs)
        messages.success(request, u"Successfully deleted Account Type")
        return response


class AccountView(ListView):
    model = Account

    def get_context_data(self, **kwargs):
        kwargs = super(AccountView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs


class AccountAddView(CreateView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")

    def get_context_data(self, **kwargs):
        kwargs = super(AccountAddView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def form_valid(self, form):
        response = super(AccountAddView, self).form_valid(form)
        messages.success(self.request,
                         u"Succcessfully added Account {0}".format(
                             form.cleaned_data["name"]
                         )
        )
        return response


class AccountEditView(UpdateView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")

    def get_context_data(self, **kwargs):
        kwargs = super(AccountEditView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def form_valid(self, form):
        response = super(AccountEditView, self).form_valid(form)
        messages.success(self.request,
                         u"Succcessfully updated Account {0}".format(
                             form.cleaned_data["name"]
                         )
        )
        return response


class AccountDeleteView(DeleteView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")

    def post(self, request, *args, **kwargs):
        response = super(AccountDeleteView, self).post(request, *args,
                                                           **kwargs)
        messages.success(request, u"Successfully deleted Account")
        return response
