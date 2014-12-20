from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (TemplateView, CreateView, UpdateView,
                                  DeleteView, ListView, FormView)
from finance.accounts.forms import AccountTypeForm, TransactionImportForm
from finance.accounts.models import AccountType, Account, Transaction
from finance.core.models import get_user_profile


class DashboardView(TemplateView):
    template_name = "accounts/dashboard.html"


class SettingsView(TemplateView):
    template_name = "accounts/settings.html"

    def get_context_data(self, **kwargs):
        kwargs = super(SettingsView, self).get_context_data(**kwargs)
        kwargs["account_types"] = AccountType.objects.filter(
            profile__user=self.request.user
        )
        return kwargs


class AccountTypeAddView(CreateView):
    model = AccountType
    success_url = reverse_lazy("accounts.settings")
    form_class = AccountTypeForm

    def form_valid(self, form):
        form.instance.profile = get_user_profile(self.request.user)
        response = super(AccountTypeAddView, self).form_valid(form)
        messages.success(self.request,
                         u"Successfully added Account Type {0}".format(
                             form.cleaned_data["name"]
                         ))
        return response


class AccountTypeEditView(UpdateView):
    model = AccountType
    success_url = reverse_lazy("accounts.settings")
    form_class = AccountTypeForm

    def get_queryset(self):
        qs = super(AccountTypeEditView, self).get_queryset()
        qs = qs.filter(profile__user=self.request.user)
        return qs

    def form_valid(self, form):
        response = super(AccountTypeEditView, self).form_valid(form)
        messages.success(self.request,
                         u"Successfully updated Account Type {0}".format(
                             form.cleaned_data["name"]
                         ))
        return response


class AccountTypeDeleteView(DeleteView):
    model = AccountType
    success_url = reverse_lazy("accounts.settings")

    def get_queryset(self):
        qs = super(AccountTypeDeleteView, self).get_queryset()
        qs = qs.filter(profile__user=self.request.user)
        return qs

    def post(self, request, *args, **kwargs):
        response = super(AccountTypeDeleteView, self).post(request, *args,
                                                           **kwargs)
        messages.success(request, u"Successfully deleted Account Type")
        return response


class AccountView(ListView):
    model = Account

    def get_queryset(self):
        qs = super(AccountView, self).get_queryset()
        qs = qs.filter(profile__user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(AccountView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs


class AccountAddView(CreateView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")
    fields = ["name", "description", "account_type"]

    def get_context_data(self, **kwargs):
        kwargs = super(AccountAddView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def get_form(self, form_class):
        form = super(AccountAddView, self).get_form(form_class)
        profile = get_user_profile(self.request.user)
        form.fields["account_type"].choices = [(x.pk, x.name) for
                                               x in AccountType.objects.filter(
                                                   profile=profile)]
        return form

    def form_valid(self, form):
        form.instance.profile = get_user_profile(self.request.user)
        response = super(AccountAddView, self).form_valid(form)
        messages.success(self.request,
                         u"Successfully added Account {0}".format(
                             form.cleaned_data["name"]
                         ))
        return response


class AccountEditView(UpdateView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")
    fields = ["name", "description", "account_type"]

    def get_context_data(self, **kwargs):
        kwargs = super(AccountEditView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def get_form(self, form_class):
        form = super(AccountEditView, self).get_form(form_class)
        profile = get_user_profile(self.request.user)
        form.fields["account_type"].choices = [(x.pk, x.name) for
                                               x in AccountType.objects.filter(
                                                   profile=profile)]
        return form

    def get_queryset(self):
        qs = super(AccountEditView, self).get_queryset()
        qs = qs.filter(profile__user=self.request.user)
        return qs

    def form_valid(self, form):
        response = super(AccountEditView, self).form_valid(form)
        messages.success(self.request,
                         u"Successfully updated Account {0}".format(
                             form.cleaned_data["name"]
                         ))
        return response


class AccountDeleteView(DeleteView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")

    def get_queryset(self):
        qs = super(AccountDeleteView, self).get_queryset()
        qs = qs.filter(profile__user=self.request.user)
        return qs

    def post(self, request, *args, **kwargs):
        response = super(AccountDeleteView, self).post(request, *args,
                                                       **kwargs)
        messages.success(request, u"Successfully deleted Account")
        return response


class TransactionView(ListView):
    model = Transaction

    def get_queryset(self):
        qs = super(TransactionView, self).get_queryset()
        qs = qs.filter(account_debit__profile__user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionView, self).get_context_data(**kwargs)
        kwargs["page"] = "transactions"
        return kwargs


class TransactionAddView(CreateView):
    model = Transaction
    success_url = reverse_lazy("accounts.transaction.list")

    def get_form(self, form_class):
        form = super(TransactionAddView, self).get_form(form_class)
        profile = get_user_profile(self.request.user)
        account_choices = [("", "-" * 9)] + [(x.pk, x.name) for x in
                                             Account.objects.filter(
                                                 profile=profile)]
        form.fields["account_debit"].choices = account_choices
        form.fields["account_credit"].choices = account_choices
        return form

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionAddView, self).get_context_data(**kwargs)
        kwargs["page"] = "transactions"
        return kwargs

    def form_valid(self, form):
        response = super(TransactionAddView, self).form_valid(form)
        messages.success(self.request, u"Successfully added Transaction")
        return response


class TransactionEditView(UpdateView):
    model = Transaction
    success_url = reverse_lazy("accounts.transaction.list")

    def get_queryset(self):
        qs = super(TransactionEditView, self).get_queryset()
        qs = qs.filter(account_debit__profile__user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionEditView, self).get_context_data(**kwargs)
        kwargs["page"] = "transactions"
        return kwargs

    def form_valid(self, form):
        response = super(TransactionEditView, self).form_valid(form)
        messages.success(self.request, u"Successfully updated Transaction")
        return response


class TransactionDeleteView(DeleteView):
    model = Transaction
    success_url = reverse_lazy("accounts.transaction.list")

    def get_queryset(self):
        qs = super(TransactionDeleteView, self).get_queryset()
        qs = qs.filter(account_debit__profile__user=self.request.user)
        return qs

    def post(self, request, *args, **kwargs):
        response = super(TransactionDeleteView, self).post(request, *args,
                                                       **kwargs)
        messages.success(request, u"Successfully deleted Transaction")
        return response


class TransactionImportView(FormView):
    form_class = TransactionImportForm
    success_url = reverse_lazy("accounts.transaction.list")

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionImportView, self).get_context_data(**kwargs)
        kwargs["page"] = "transactions"
        return kwargs
