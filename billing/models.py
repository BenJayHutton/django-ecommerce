from django.db import models
from django.urls import reverse

from accounts.models import GuestEmail, User


class BillingProfileManager(models.Manager):
    def new_or_get(self, request, email=None):
        session_key = request.session.session_key
        user = request.user
        billing_obj = None
        email_obj = None
        created = False
        if user.is_authenticated:
            email_obj=user.email
            billing_obj = self.get_queryset().filter(email=user.email).first()
        else:
            if email:
                billing_obj = self.get_queryset().filter(email=email).first()
            else:
                billing_obj = self.get_queryset().filter(session_key=session_key).first()
        
        if billing_obj:
            billing_obj.session_key = session_key
            billing_obj.save()
            if billing_obj.user is None and user.is_authenticated:
                billing_obj.user = user
                billing_obj.save()
        else:
            if user.is_authenticated:
                email_obj = user.email
            else:
                if email:
                    email_obj = email
            billing_obj = self.model.objects.create(email=email_obj, session_key=session_key)
            created = True
        return billing_obj, created


class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    guest_user = models.OneToOneField(GuestEmail, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    meta_data = models.TextField(null=True, blank=True)

    objects = BillingProfileManager()

    def __str__(self):
        return self.email

    def get_cards(self):
        return self.card_set.all()

    def get_payment_method_url(self):
        return reverse('billing:billing-payment-method')

    @property
    def has_card(self):
        card_qs = self.get_cards()
        return card_qs.exists()

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        card_qs = self.get_cards()
        card_qs.update(active=False)
        return card_qs.filter(active=True).count()
