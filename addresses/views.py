from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from billing.models import BillingProfile

from .models import Address
from .forms import AddressForm


def checkout_address_create_view(request):
    user = request.user
    session_key = request.session.session_key
    form = AddressForm(request.POST or None)
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    address_type = request.POST.get('id_shipping_type', None)
    redirect_path = next_ or next_post or None

    if user.is_authenticated:
        email_obj = user.email
    else:
        email_obj =  request.session.get('customer_email')
   
    if form.is_valid():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request, email=email_obj)
        instance = form.save(commit=False)

        if billing_profile is not None:
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.session_key = session_key
            instance.save()
            if user.is_authenticated:
                instance.user = user
                instance.save()
            request.session[address_type + "_address_id"] = instance.id
            request.session["email_obj"] = instance.billing_profile.email
        else:
            return redirect("cart:checkout")
        if url_has_allowed_host_and_scheme(redirect_path, request.get_host()):
            return redirect(redirect_path)
    context = {
        "form": form,
    }
    return redirect("cart:checkout")


def checkout_address_reuse_view(request):
    form = AddressForm(request.POST or None)
    email_obj = request.session.get("email_obj")
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request, email=email_obj)
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    address_type = request.POST.get('address_type', 'shipping')
    redirect_path = next_ or next_post or None

    if request.method == "POST":
        shipping_address = request.POST.get('shipping_address', None)
        if shipping_address is not None:
            request.session[address_type + "_address_id"] = shipping_address
        if url_has_allowed_host_and_scheme(
                redirect_path, request.get_host()):
            return redirect(redirect_path)
    return redirect("cart:checkout")


def checkout_address_change_view(request):
    form = AddressForm()
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    address_type = request.GET.get('address_type') or request.POST.get('id_shipping_type', None)
    redirect_path = next_ or next_post or reverse('cart:checkout')

    # determine billing profile for this request (guest or authenticated)
    email_obj = None
    if request.user.is_authenticated:
        try:
            email_obj = request.user.email
        except Exception:
            email_obj = None
    else:
        email_obj = request.session.get('customer_email') or request.session.get('email_obj')

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request, email=email_obj)

    address_qs = None
    if billing_profile is not None:
        address_qs = Address.objects.filter(billing_profile=billing_profile)

    context = {
        "form": form,
        "address_type": address_type,
        "next": redirect_path,
        "address_qs": address_qs,
        "action_url": reverse('checkout_address_reuse')
    }
    return render(request, 'addresses/create_address.html', context)

class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'addresses/address_list.html'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'addresses/address_form.html'
    success_url = reverse_lazy('address:home')
    
    def form_valid(self, form):
        request = self.request
        if request.user.is_authenticated:
            form.instance.user = request.user
            billing_obj, billing_profile_created = BillingProfile.objects.new_or_get(request)
        else:
            billing_obj, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if billing_obj is not None:
            form.instance.billing_profile = billing_obj
        else:
            form.instance.billing_profile = billing_profile_created
        return super().form_valid(form)
    

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'addresses/address_form.html'
    success_url = reverse_lazy('address:home')
    
    def get_queryset(self):            
        return Address.objects.filter(user=self.request.user)
        

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'addresses/address_confirm_delete.html'
    success_url = reverse_lazy('address:home')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
