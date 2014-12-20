from django import forms
from finance.accounts.models import AccountType


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
