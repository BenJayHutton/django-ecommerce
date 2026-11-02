import logging
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, View
from django.shortcuts import render, redirect

from .forms import MarketingPreferenceForm
from .mixins import CsrfExemptMixin
from .models import MarketingPreference
from .utils import Mailchimp

now = timezone.now()
project_error_log = logging.getLogger("project_error_log")
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)


class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceForm
    template_name = 'base/forms.html'
    success_url = '/marketing/settings/email/'
    success_message = 'Your email prefefence have bee updated'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return redirect("/accounts/login/?next=/marketing/settings/email/")
        return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Update Email Preference'
        return context

    def get_object(self):
        try:
            user = self.request.user        
            obj, created = MarketingPreference.objects.get_or_create(user=user)
            return obj
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)


class MailchimpWebhookView(CsrfExemptMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            list_id = data.get('data[list_id]')
            if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
                hook_type = data.get("type")
                email = data.get('data[email]')
                response_status, response_status = Mailchimp().check_subscription_status(email)
                sub_status = response_status['status']
                is_subbed = None
                mailchimp_subbed = None
                if sub_status == "subscribed":
                    is_subbed, mailchimp_subbed(True, True)
                elif sub_status == "unsubscribed":
                    is_subbed, mailchimp_subbed(False, False)
                if is_subbed is not None and mailchimp_subbed is not None:
                    qs = MarketingPreference.objects.filter(user__email__iexact=email)
                    if qs.exits():
                        qs.Update(subscribed=is_subbed, mailchimp_subscribed=mailchimp_subbed, mailchimp_msg=str(data))
            return HttpResponse("Thank you", status=200)
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)
