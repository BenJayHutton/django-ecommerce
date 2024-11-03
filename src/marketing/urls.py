from django.urls import path
from.views import MarketingPreferenceUpdateView, MailchimpWebhookView

app_name = 'marketing'

urlpatterns = [
    path('settings/email/', MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    path('webhook/mailchimp/', MailchimpWebhookView.as_view(), name='webhook-mailchimp'),
]
