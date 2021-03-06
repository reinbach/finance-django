from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import (TemplateView, CreateView, UpdateView, View,
                                  DeleteView, ListView, FormView, DetailView)
from finance.accounts.dashboard import (get_monthly_totals, get_debits_title,
                                        get_credits_title,
                                        get_monthly_debits_vs_credits)
from finance.accounts.forms import (AccountTypeForm, TransactionImportForm,
                                    TransactionFormSet, AccountForm,
                                    TransactionImportFormSet)
from finance.accounts.models import AccountType, Account, Transaction
from finance.accounts.utils import (get_account_choices,
                                    get_account_type_choices)
from finance.core.models import get_user_profile


class DashboardView(TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        kwargs = super(DashboardView, self).get_context_data(**kwargs)
        kwargs["page"] = "dashboard"
        profile = get_user_profile(self.request.user)
        kwargs["debits_title"] = get_debits_title(profile)
        kwargs["credits_title"] = get_credits_title(profile)
        return kwargs


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
        qs = qs.filter(profile__user=self.request.user).exclude(
            parent__isnull=False
        )
        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(AccountView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs


class AccountAddView(CreateView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")
    fields = ["name", "description", "account_type", "parent", "is_category"]

    def get_context_data(self, **kwargs):
        kwargs = super(AccountAddView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def get_form(self, form_class):
        form = super(AccountAddView, self).get_form(form_class)
        form.fields["account_type"].choices = get_account_type_choices(
            self.request.user
        )
        parent_account_choices = get_account_choices(self.request.user, True)
        form.fields["parent"].choices = parent_account_choices
        return form

    def form_valid(self, form):
        form.instance.profile = get_user_profile(self.request.user)
        response = super(AccountAddView, self).form_valid(form)
        if self.request.is_ajax():
            account_options = get_account_choices(self.request.user)
            parent_options = get_account_choices(self.request.user, True)
            return JsonResponse(
                {"result": render_to_string("options.html",
                                            {"options": account_options}),
                 "parent": render_to_string("options.html",
                                            {"options": parent_options}),
                 "new_pk": self.object.pk}
            )
        messages.success(self.request,
                         u"Successfully added Account {0}".format(
                             form.cleaned_data["name"]
                         ))
        return response

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({"result": render_to_string("form.html",
                                                            {"form": form})})
        return super(AccountAddView, self).form_invalid(form)


class AccountEditView(UpdateView):
    model = Account
    success_url = reverse_lazy("accounts.account.list")
    fields = ["name", "description", "account_type", "parent", "is_category"]

    def get_context_data(self, **kwargs):
        kwargs = super(AccountEditView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def get_form(self, form_class):
        form = super(AccountEditView, self).get_form(form_class)
        form.fields["account_type"].choices = get_account_type_choices(
            self.request.user
        )
        form.fields["parent"].choices = get_account_choices(self.request.user,
                                                            True)
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


class AccountTransactionView(DetailView):
    model = Account
    template_name = "accounts/transaction_list.html"

    def get_queryset(self):
        qs = super(AccountTransactionView, self).get_queryset()
        qs = qs.filter(profile__user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(AccountTransactionView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        paginator = Paginator(kwargs["object"].transactions(), 25)
        page = self.request.GET.get("page")
        try:
            trxs = paginator.page(page)
        except PageNotAnInteger:
            trxs = paginator.page(1)
        except EmptyPage:
            trxs = paginator.page(paginator.num_pages)
        kwargs["trxs"] = trxs
        kwargs["page_number"] = page

        return kwargs


class TransactionAddView(FormView):
    template_name = "accounts/transaction_add.html"
    form_class = TransactionFormSet
    success_url = reverse_lazy("accounts.account.list")

    def get_form_kwargs(self):
        kwargs = super(TransactionAddView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionAddView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        kwargs["form_account"] = AccountForm(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        added_trx_count = 0
        for f in form:
            if f.cleaned_data:
                f.save()
                added_trx_count += 1
        response = super(TransactionAddView, self).form_valid(form)
        messages.success(self.request,
                         u"Successfully added {0} Transaction(s)".format(
                             added_trx_count
                         ))
        return response


class TransactionEditView(UpdateView):
    model = Transaction
    success_url = reverse_lazy("accounts.account.list")

    def get_success_url(self):
        if "next" in self.request.GET:
            page = self.request.GET.get("page", 1)
            return "{0}?page={1}".format(
                reverse("accounts.transaction.list.by_account",
                        args=[self.request.GET["next"]]),
                page
            )
        return super(TransactionEditView, self).get_success_url()

    def get_queryset(self):
        qs = super(TransactionEditView, self).get_queryset()
        qs = qs.filter(account_debit__profile__user=self.request.user)
        return qs

    def get_form(self, form_class):
        form = super(TransactionEditView, self).get_form(form_class)
        account_choices = get_account_choices(self.request.user)
        form.fields["account_debit"].choices = account_choices
        form.fields["account_credit"].choices = account_choices
        return form

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionEditView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def form_valid(self, form):
        response = super(TransactionEditView, self).form_valid(form)
        messages.success(self.request, u"Successfully updated Transaction")
        return response


class TransactionDeleteView(DeleteView):
    model = Transaction
    success_url = reverse_lazy("accounts.account.list")

    def get_success_url(self):
        if "next" in self.request.GET:
            page = self.request.GET.get("page", 1)
            return "{0}?page={1}".format(
                reverse("accounts.transaction.list.by_account",
                        args=[self.request.GET["next"]]),
                page
            )
        return super(TransactionDeleteView, self).get_success_url()

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
    template_name = "accounts/transaction_import.html"
    form_class = TransactionImportForm
    success_url = reverse_lazy("accounts.account.list")

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionImportView, self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(TransactionImportView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        formset = TransactionImportFormSet(initial=form.process_file(),
                                           user=self.request.user)
        form_account = AccountForm(user=self.request.user)
        return render_to_response(
            "accounts/transaction_import_confirm.html",
            self.get_context_data(form=formset, form_account=form_account),
            context_instance=RequestContext(self.request)
        )


class TransactionImportConfirmView(FormView):
    template_name = "accounts/transaction_import_confirm.html"
    form_class = TransactionImportFormSet
    success_url = reverse_lazy("accounts.account.list")

    def get_form_kwargs(self):
        kwargs = super(TransactionImportConfirmView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super(TransactionImportConfirmView,
                       self).get_context_data(**kwargs)
        kwargs["page"] = "accounts"
        kwargs["form_account"] = AccountForm(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        import_trx_count = 0
        for f in form:
            if not f.cleaned_data["DELETE"]:
                f.save()
                import_trx_count += 1
        messages.success(self.request,
                         "Successfully added {0} Transactions".format(
                             import_trx_count
                         ))
        return super(TransactionImportConfirmView, self).form_valid(form)


class DataYearlyDebit(View):
    def get(self, request):
        profile = get_user_profile(request.user)
        return JsonResponse(get_monthly_totals(profile))


class DataYearlyDebitVsCredit(View):
    def get(self, request):
        profile = get_user_profile(request.user)
        return JsonResponse(get_monthly_debits_vs_credits(profile), safe=False)
