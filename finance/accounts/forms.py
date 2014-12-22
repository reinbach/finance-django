import uuid

from django import forms
from django.conf import settings
from django.forms.formsets import formset_factory, BaseFormSet
from finance.accounts.models import (AccountType, Transaction,
                                     TransactionsImport, Account)
from finance.accounts.utils import (get_account_choices,
                                    get_account_type_choices)


class AccountTypeForm(forms.ModelForm):
    class Meta:
        model = AccountType
        fields = ["name"]

    def clean(self):
        data = super(AccountTypeForm, self).clean()
        if "name" in data:
            # TODO need to differentiate between profiles
            if AccountType.objects.filter(name=data["name"]).exclude(
                    pk=self.instance.pk
            ).exists():
                raise forms.ValidationError("Name needs to be unique")


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "description", "account_type"]

    def __init__(self, user, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields["account_type"].choices = get_account_type_choices(user)


class TransactionImportForm(forms.Form):
    account_main = forms.ChoiceField()
    filename = forms.FileField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(TransactionImportForm, self).__init__(*args, **kwargs)
        self.fields["account_main"].choices = get_account_choices(self.user)

    def process_file(self):
        filename = "{0}/imports/{1}.csv".format(settings.MEDIA_ROOT,
                                                uuid.uuid4())
        with open(filename, "wb+") as destination:
            for chunk in self.files["filename"].chunks():
                destination.write(chunk)
        parser = TransactionsImport(self.cleaned_data["account_main"],
                                   filename)
        parser.parse_file()
        return parser.transactions


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ["description"]


class TransactionBaseFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(TransactionBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(TransactionBaseFormSet, self)._construct_form(i, **kwargs)
        account_choices = get_account_choices(self.user)
        form.fields["account_debit"].choices = account_choices
        form.fields["account_credit"].choices = account_choices
        form.fields["DELETE"].label = "Duplicate"
        return form


TransactionFormSet = formset_factory(TransactionForm, can_delete=True, extra=0,
                                     formset=TransactionBaseFormSet)
