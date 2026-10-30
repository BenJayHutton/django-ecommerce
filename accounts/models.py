import logging
import random, string
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.template.loader import get_template
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

length = 32
random_string = ''.join(random.choices(string.ascii_letters+string.digits+string.punctuation, k=length))
DEFAULT_ACTIVATION_DAYS = getattr(settings, "DEFAULT_ACTIVATION_DAYS", 7)

project_debug = logging.getLogger("project_debug_log")
project_access = logging.getLogger("project_access_log")
project_error = logging.getLogger("project_error_log")

now = timezone.now()


class UserManager(BaseUserManager):
    def new_or_create(self, email):
        qs = self.get_queryset().filter(email=email)
        created = False
        if qs.count() == 1:
            obj = qs.first()
        else:
            user_obj = GuestEmail.objects.filter(email=email)
            if user_obj:
                obj = self.create_user(email=email, password=random_string)
                created = True
        return obj, created

    def create_user(self, email, full_name=None, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("users must have an email address")
        if not password:
            raise ValueError("Must enter password")

        user_obj = self.model(
            email=self.normalize_email(email),
            full_name=full_name
        )
        user_obj.set_password(password)  # can be used to change password
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.is_active = is_active
        user_obj.save()
        return user_obj

    def create_staffuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True,
        )
        return user

    def create_superuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True,
            is_admin=True,
        )
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    guest = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perms(self, perm, obj=None):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin


class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_rangee = now

        return self.filter(
            activated=False,
            forced_expired=False
        ).filter(
            timestamp__gt=start_range,
            timestamp__lte=end_rangee,
        )


class EmailActivationManager(models.Manager):
     # overriding get_queryset so we can use the queryset above
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        return self.get_queryset().filter(Q(email=email) | Q(
            user__email=email)).filter(activated=False)


class EmailActivation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    key = models.CharField(max_length=120, blank=True, null=True)
    activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7)  # expires in x days
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            # pre activation user signal
            user = self.user
            user.is_active = True
            user.save()
            # post activation user signal
            self.activated = True
            self.save()
            return True
        return False

    def __str__(self):
        return self.email

    def regenerate_key(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation_email(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                scheme_url = getattr(settings, 'HOST_SCHEME', None)
                base_url = getattr(settings, 'BASE_URL', None)
                port = getattr(settings, 'PORT', None)
                key_path = reverse(
                    "account:email-activate",
                    kwargs={
                        'key': self.key})
                path = str(f"{scheme_url}{base_url}:{port}/{key_path}")
                context = {
                    'path': path,
                    'email': self.email,
                }
                txt_ = get_template("registration/emails/verify.txt").render(context)
                html_ = get_template("registration/emails/verify.html").render(context)
                subject = '1-Click Email Activation'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]
                try:
                    if not settings.EMAIL_BACKEND:
                        raise RuntimeError("EMAIL_BACKEND is not configured")
                    sent_mail = send_mail(
                        subject,
                        txt_,
                        from_email,
                        recipient_list,
                        html_message=html_,
                        fail_silently=False,
                    )
                    return sent_mail
                except Exception as e:
                    project_debug.exception(f'[{now}] send_activation_email error: {type(e)}: {e}')
                    return False
        return False


class GuestEmailManager(models.Manager):
    def new_or_get(self, request, email):
        session_key = request.session.session_key
        created = False
        qs = self.get_queryset().filter(email=email, session_key=session_key).first()

        if qs:
            return qs, created
        else:
            qs = self.create(email=email, session_key=session_key)
            created = True
            return qs, created


class GuestEmail(models.Model):
    email = models.EmailField()
    session_key = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = GuestEmailManager()

    def __str__(self):
        return self.email
