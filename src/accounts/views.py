from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin

from eCommerce.mixins import NextUrlMixin, RequestFormAttachMixin

from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from .models import EmailActivation


class Accounts(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(Accounts, self).get_context_data(*args, **kwargs)
        context['title'] = "Account Home"
        context['description'] = "Account Home"
        return context

    def get_object(self):
        return self.request.user


class AccountEmailActivateView(FormMixin, View):
    success_url = '/'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(
                    request, "your email has been confirmed, please login.")
                return redirect("accounts:login")
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse("password_reset")
                    msg = """Your email has already been confirmed
                    Do you need to <a href="{link}">reset your password?</a>
                    """.format(link=reset_link)
                    messages.success(request, mark_safe(msg))
                    return redirect("accounts:login")
        context = {
            'form': self.get_form(),
            'key': key,
        }
        return render(request, 'registration/activation-error.html', context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = """Activation link sent, please check email"""
        messages.success(self.request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation_email()
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        request = self.request
        context = {
            'form': form,
            'key': self.key,
        }
        return render(request, 'registration/activation-error.html', context)


class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    form_class = GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'accounts/login.html'
    default_next = "/"

    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')


class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail-update-view.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(
            UserDetailUpdateView,
            self).get_context_data(
            *
            args,
            **kwargs)
        context['title'] = 'Change your Account Details'
        return context

    def get_success_url(self):
        return reverse("accounts:home")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")
