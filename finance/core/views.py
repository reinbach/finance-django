from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, FormView, UpdateView
from finance.accounts.models import Account
from finance.core.forms import RegisterForm, ContactForm
from finance.core.models import Profile
from finance.core.utils import get_year_choices


class HomeView(TemplateView):
    template_name = "home.html"


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm

    def get_success_url(self):
        return reverse("contact")

    def get_context_data(self, **kwargs):
        kwargs = super(ContactView, self).get_context_data(**kwargs)
        kwargs["page"] = "contact"
        return kwargs

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request,
                         u"Your message has been sent. Thank you!")
        return super(ContactView, self).form_valid(form)


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = RegisterForm

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        registered_user = form.register()
        user = authenticate(username=registered_user.username,
                            password=form.cleaned_data["password"])
        if user is not None:
            login(self.request, user)
        messages.success(self.request, "Successfully registered")
        return super(RegisterView, self).form_valid(form)


class ProfileView(UpdateView):
    model = Profile
    success_url = reverse_lazy("profile.home")
    fields = ["current_year"]

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

    def get_form(self, form_class):
        form = super(ProfileView, self).get_form(form_class)
        form.fields["current_year"].widget = forms.Select(
            choices=get_year_choices()
        )
        return form

    def form_valid(self, form):
        response = super(ProfileView, self).form_valid(form)
        # clear cache of related accounts
        for acct in Account.objects.filter(profile=self.object,
                                           account_type__yearly=True):
            acct.clear_cache()
        messages.success(self.request, "Successfully updated current year"
                         " to {0}".format(form.cleaned_data["current_year"]))
        return response
