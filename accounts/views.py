from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin

from ecommerce.mixins import NextUrlMixin, RequestFormAttachMixin
from addresses.models import Address
from billing.models import BillingProfile
from orders.models import Order

from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from .models import EmailActivation, User, GuestEmail


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
    model = GuestEmail
    form_class = GuestForm
    default_next = reverse_lazy('accounts:register')

    def get_success_url(self):
        return self.get_next_url()
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        session_id=self.request.session.session_key

        if not GuestEmail.objects.filter(email=email, session_id=session_id).exists():
            GuestEmail.objects.create(email=email, session_id=session_id)
            return redirect(self.get_next_url())
        else:
            # If we already have email, what is the appropriate responce?
            # assuming the cart app ins't the only one submiting a guest form
            return self.form_invalid(form)

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

    def form_valid(self, form):
        request = self.request
        session_key = request.session.session_key
        # save user (RegisterForm.save sets is_active=False)
        user = form.save()
        email = user.email
        # find any GuestEmail for this email (regardless of session)
        try:
            guest_qs = GuestEmail.objects.filter(email=email)
            guest_obj = guest_qs.first() if guest_qs.exists() else None
        except Exception:
            guest_obj = None

        # create or get BillingProfile for this email and attach to user
        try:
            billing_profile, _ = BillingProfile.objects.new_or_get(request, email=email)
            if billing_profile.user is None:
                billing_profile.user = user
            if guest_obj:
                billing_profile.guest_user = guest_obj
            billing_profile.save()
        except Exception:
            billing_profile = None

        # attach any addresses created during the guest session to this user/billing_profile
        try:
            if session_key:
                Address.objects.filter(session_key=session_key).update(user=user)
                if billing_profile:
                    Address.objects.filter(session_key=session_key).update(billing_profile=billing_profile)
        except Exception:
            pass

        # attach any orders created during the guest session to the billing_profile
        try:
            if session_key and billing_profile:
                Order.objects.filter(session_key=session_key).update(billing_profile=billing_profile)
        except Exception:
            pass

        # cleanup guest session marker if present
        try:
            del request.session['guest_email_id']
        except Exception:
            pass

        messages.success(request, "Account created. Please check your email to activate.")
        return super(RegisterView, self).form_valid(form)


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
        return reverse("account:home")


def logout_view(request):
    logout(request)
    return redirect("account:login")
