import datetime
import sys

from random import random

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from django.db import models, IntegrityError
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.contrib.sites.models import Site

from timezones.fields import TimeZoneField

from account.signals import email_confirmed, email_confirmation_sent

from common import utils

 
## Following code about email added by jun 
class EmailAddressManager(models.Manager):
    
    def add_email(self, user, email):
        try:
            email_address = self.create_or_get_email(user=user, email=email)
            return email_address
        except IntegrityError:
            return None
    
    # added by jun, to replace the self.create(user=user, email=email) method
    def create_or_get_email(self,user, email):
        try:
            emailAddress = EmailAddress.objects.get(user=user, email=email)
            return emailAddress
        except EmailAddress.DoesNotExist:
            return self.create(user=user, email=email)
    
    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except EmailAddress.DoesNotExist:
            return None
    
    def get_users_for(self, email):
        """
        returns a list of users with the given email.
        """
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in EmailAddress.objects.filter(
            verified=True, email=email)]


class EmailAddress(models.Model):
    
    user = models.ForeignKey(User, related_name='user')
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)
    
    objects = EmailAddressManager()
    
    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        self.user.email = self.email
        self.user.save()
        return True
    
    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user)
    
    class Meta:
        db_table = "t_email"
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        unique_together = (
            ("user", "email"),
        )

EMAIL_CONFIRM_VIEW = "account.views.confirm_email"
from account.threads import startEmailSendThread

# added by tom.jing for count the email sent times
class EmailSentCount(models.Model):
    email_address = models.EmailField()
    signup_count = models.IntegerField(default=0)
    reset_pwd_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = "t_email_sent_count"
        verbose_name = 'EmailSentCount'

from account.decorators import check_email_sent_count
class EmailConfirmationManager(models.Manager):
    
    def confirm_email(self, confirmation_key):
        try:
            confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        if not confirmation.key_expired():
            email_address = confirmation.email_address
            email_address.verified = True
            email_address.set_as_primary(conditional=True)
            email_address.save()
            email_confirmed.send(sender=self.model, email_address=email_address)
            return email_address
    
    @check_email_sent_count
    def send_confirmation(self, email_address):
        salt = sha_constructor(str(random())).hexdigest()[:5]
        confirmation_key = sha_constructor(salt + email_address.email).hexdigest()
        current_site = Site.objects.get_current()
        # check for the url with the dotted view path
        try:
            path = reverse(EMAIL_CONFIRM_VIEW, args=[confirmation_key])
        except NoReverseMatch:
            # or get path with named urlconf instead
            path = reverse("emailconfirmation_confirm_email", args=[confirmation_key])
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        activate_url = u"%s://%s%s" % (
            protocol,
            unicode(current_site.domain),
            path
        )
        context = {
            "user": email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "confirmation_key": confirmation_key,
        }
        
        #subject = render_to_string(settings.EMAIL_CONFIRMATION_SUBJECT, context)
        subject = settings.EMAIL_CONFIRMATION_SUBJECT
        
        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        message = render_to_string(settings.EMAIL_CONFIRMATION_MESSAGE, context)
        
        # launch a new thread to send email, don't let user wait for so long, by junn
        startEmailSendThread(subject, message, settings.DEFAULT_FROM_EMAIL, [email_address.email])
              
        confirmation = self.create(
            email_address=email_address,
            sent=datetime.datetime.now(),
            confirmation_key=confirmation_key
        )
        email_confirmation_sent.send(
            sender=self.model,
            confirmation=confirmation,
        )
        return confirmation
    
    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()


class EmailConfirmation(models.Model): 
    
    email_address = models.ForeignKey(EmailAddress)
    sent = models.DateTimeField()
    confirmation_key = models.CharField(max_length=40)
    
    objects = EmailConfirmationManager()
    
    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            days=settings.EMAIL_CONFIRMATION_DAYS)
        return expiration_date <= datetime.datetime.now()
    key_expired.boolean = True
    
    def __unicode__(self):
        return u"confirmation for %s" % self.email_address
    
    class Meta:
        db_table = "t_emailconfirmation"
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")


class Account(models.Model):
    
    user = models.ForeignKey(User, unique=True, verbose_name=_("user"))
    
    timezone = TimeZoneField(_("timezone"))
    language = models.CharField(_("language"),
        max_length = 10,
        choices = settings.LANGUAGES,
        default = settings.LANGUAGE_CODE
    )
    
    class Meta:
        db_table = 't_account'
        verbose_name = 'Account'
    
    def __unicode__(self):
        return self.user.username


class AnonymousAccount(object):
    
    def __init__(self, request=None):
        self.user = AnonymousUser()
        self.timezone = settings.TIME_ZONE
        if request is not None:
            self.language = get_language_from_request(request)
        else:
            self.language = settings.LANGUAGE_CODE
    
    def __unicode__(self):
        return "AnonymousAccount"


class PasswordReset(models.Model):
    
    user = models.ForeignKey(User, verbose_name=_("user"))
    
    temp_key = models.CharField(_("temp_key"), max_length=100)
    timestamp = models.DateTimeField(_("timestamp"), default=datetime.datetime.now)
    reset = models.BooleanField(_("reset yet?"), default=False)

    class Meta:
        db_table = 't_password_reset'
        verbose_name = 'PasswordReset'
    
    def __unicode__(self):
        return "%s (key=%s, reset=%r)" % (
            self.user.username,
            self.temp_key,
            self.reset
        )


@receiver(post_save, sender=User)
def create_account(sender, instance=None, **kwargs):
    if instance is None:
        return
    account, created = Account.objects.get_or_create(user=instance)


# @@@ move to emailconfirmation app?
@receiver(post_save, sender=User)
def superuser_email_address(sender, instance=None, **kwargs):
    if instance is None:
        return
    # only run when we are in syncdb or createsuperuser to be as unobstrusive
    # as possible and reduce the risk of running at inappropriate times
    if "syncdb" in sys.argv or "createsuperuser" in sys.argv:
        defaults = {
            "user": instance,
            "verified": True,
            "primary": True,
        }
        EmailAddress.objects.get_or_create(email=instance.email, **defaults)


@receiver(email_confirmed, sender=EmailConfirmation)
def mark_user_active(sender, instance=None, **kwargs):
    user = kwargs.get("email_address").user
    user.is_active = True
    user.save()

