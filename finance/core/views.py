from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, FormView
from finance.core.forms import RegisterForm, ContactForm


class HomeView(TemplateView):
    template_name = "home.html"


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm

    def get_success_url(self):
        return reverse("contact")

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
