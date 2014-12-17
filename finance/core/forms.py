from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail


class ContactForm(forms.Form):
    subject = forms.CharField()
    email = forms.EmailField(required=False, help_text="(optional)")
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        send_mail("Hello from KidVM", self.cleaned_data["message"],
                  self.cleaned_data.get("email", 'unknown'),
                  [settings.EMAIL_ADDRESS], fail_silently=True)


class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        data = super(RegisterForm, self).clean()
        if data.get("password") and data.get("confirm_password"):
            if data["password"] != data["confirm_password"]:
                raise forms.ValidationError("Passwords do not match")
        return data

    def register(self):
        user = User.objects.create_user(self.cleaned_data['email'],
                                        self.cleaned_data['email'],
                                        self.cleaned_data['password'])
        return user
