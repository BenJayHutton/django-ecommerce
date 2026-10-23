from .models import BillingProfile


def get_or_create_guest_billing_profile(email):
    billing_profile, created = BillingProfile.objects.get_or_create(
        email=email,
        user=None
    )
    return billing_profile