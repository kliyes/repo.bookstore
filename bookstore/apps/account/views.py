# -*-coding:utf-8 -*-

import random, StringIO

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import logout as django_logout
from django.views.decorators.csrf import csrf_exempt

from account.models import EmailAddress, EmailConfirmation
from common import utils
from sites.models import Motto
 
association_model = models.get_model("django_openid", "Association")
if association_model is not None:
    from django_openid.models import UserOpenidAssociation

from account.decorators import login_get_forbidden, signup_allowed
from account.utils import get_default_redirect
from account.forms import AddEmailForm, ChangeLanguageForm, ChangePasswordForm
from account.forms import ChangeTimezoneForm, LoginForm, ResetPasswordKeyForm
from account.forms import ResetPasswordForm, SetPasswordForm, SignupForm

import logging
log = logging.getLogger("mysite")


#@ensure_csrf_cookie
def adminLogin(request, **kwargs):
    form_class = kwargs.pop("form_class", LoginForm)
    success_url = request.REQUEST.get("success_url", "/protocol/create_client/")

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.login(request)
            if request.user.is_superuser:
                return HttpResponseRedirect(success_url)
            else:
                utils.addMsg(request, messages.ERROR, "not admin account")
        else:
            utils.addMsg(request, messages.ERROR, form.errors)
            
    return render_to_response("account/admin_login.html", RequestContext(request,
        {"form": form_class(), }))

def group_and_bridge(kwargs):
    """
    Given kwargs from the view (with view specific keys popped) pull out the
    bridge and fetch group from database.
    """
    
    bridge = kwargs.pop("bridge", None)
    
    if bridge:
        try:
            group = bridge.get_group(**kwargs)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None
    
    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    return {
        "group": group,
    }

@login_get_forbidden
def login(request, **kwargs):
    form_class = kwargs.pop("form_class", LoginForm)
    template_name = settings.TEMPLATE_LOGIN
    
    # 如果是ajax弹出框登录，重置模板
    if request.is_ajax():
        template_name = settings.TEMPLATE_AJAX_LOGIN
    
    success_url = kwargs.pop("success_url", None)
    url_required = kwargs.pop("url_required", False)
    extra_context = kwargs.pop("extra_context", {})
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    
    group, bridge = group_and_bridge(kwargs)
    
    if extra_context is None:
        extra_context = {}
    if success_url is None:
        if hasattr(settings, "LOGIN_REDIRECT_URLNAME"):
            fallback_url = reverse(settings.LOGIN_REDIRECT_URLNAME)
        else:
            fallback_url = settings.LOGIN_REDIRECT_URL
        success_url = get_default_redirect(request, fallback_url, redirect_field_name)
    
    if request.method == "POST" and not url_required:
        form = form_class(request.POST, group=group)
        if form.is_valid():
            form.login(request)
            request.session["failedLoginCount"] = 0
            return after_login(request, success_url) 
            #return HttpResponseRedirect(request.GET.get("whatNext", "/home/"))
        else:
            utils.addMsg(request, messages.ERROR, form.errors)
            request.session["failedLoginCount"] = request.session.get("failedLoginCount", 0) + 1
    else:
        form = form_class(group=group)
    
    ctx = group_context(group, bridge)
    
    motto = Motto.objects.get(id=random.randint(1, Motto.objects.getCount()))
    
    ctx.update({
        "form": form,
        "url_required": url_required,
        "redirect_field_name": redirect_field_name,
        "whatNext": request.GET.get("whatNext"), 
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
        "motto": motto
    })
    ctx.update(extra_context)
    
    return render_to_response(template_name, RequestContext(request, ctx))

def after_login(request, success_url):
    '''登录后处理'''
    __saveTextDraft(request)
    
    whatNext = request.GET.get("whatNext", success_url)
    
    profile = request.user.get_profile()
    profile.updateLoginCount()
    log.debug("login_count: %s of profile: %s" % (profile.login_count, profile.id))
    if profile.login_count == 1: 
        utils.addMsg(request, messages.INFO, u"第一次登录, 展示一下个性吧")
        return HttpResponseRedirect(reverse("profiles_setting"))
    
    return HttpResponseRedirect(whatNext)

def __saveTextDraft(request):
    '''私有函数: 用于未登录状态下用户已编辑输入内容需要临时保存'''
    draft = request.POST.get("draft", None)
    if draft and draft.strip():
        request.session["draft"] = draft.strip() 

def logout(request, next_page=None, **kwargs):
    # Simple Wrapper around django.contrib.auth.views.logout to default
    #    next_page based off the setting LOGOUT_REDIRECT_URLNAME.

    if next_page is None and hasattr(settings, "LOGOUT_REDIRECT_URLNAME"):
        next_page = reverse(settings.LOGOUT_REDIRECT_URLNAME)

    return django_logout(request, next_page, **kwargs)

@login_get_forbidden
@signup_allowed
def signup(request, **kwargs):
    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", settings.TEMPLATE_SIGNUP)
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    success_url = kwargs.pop("success_url", None)
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
    if success_url is None:
        if hasattr(settings, "SIGNUP_REDIRECT_URLNAME"):
            fallback_url = reverse(settings.SIGNUP_REDIRECT_URLNAME)
        else:
            if hasattr(settings, "LOGIN_REDIRECT_URLNAME"):
                fallback_url = reverse(settings.LOGIN_REDIRECT_URLNAME)
            else:
                fallback_url = settings.LOGIN_REDIRECT_URL
        success_url = get_default_redirect(request, fallback_url, redirect_field_name)
    
    if request.method == "POST":
        form = form_class(request.POST, group=group)
        if form.is_valid():
            user, emailAddress = form.save(request=request)
            
            # 若注册需要Email激活,则发送邮件,  异步邮件队列方式发送邮件 in future TODO
            if settings.ACCOUNT_EMAIL_VERIFICATION:
                user.is_active = False #default True
                user.save()
                
                EmailConfirmation.objects.send_confirmation(emailAddress)
                    
                ctx.update({
                    "email": form.cleaned_data["email"],
                    "success_url": success_url,
                })
                ctx = RequestContext(request, ctx)
                return render_to_response(settings.TEMPLATE_VERIFICATION_SENT, ctx)
            
            # 不需要发送激活邮件,直接登录
            else:
                form.login(request, user)
                return render_to_response("account/signup_success.html", 
                    RequestContext(request, {'email': user.email, 'nickname': user.get_profile().name}))
                
                #return HttpResponseRedirect(success_url)  #later using this
        else:
            utils.addMsg(request, messages.ERROR, form.errors)    
            
    else:
        form = form_class(group=group)
    
    motto = Motto.objects.get(id=random.randint(1, Motto.objects.getCount()))
    ctx.update({
        "form": form,
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
        "motto": motto
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))

# 用于账号激活邮件重发
def send_confirm_email(request):
    email = request.GET.get("email")
    
    try:
        emailAddress = EmailAddress.objects.get(email=email)
    except EmailAddress.DoesNotExist:
        log.warning("Email address not exists: %s" % email)
        
    EmailConfirmation.objects.send_confirmation(emailAddress)
            
    utils.addMsg(request, messages.SUCCESS, u"激活邮件已重发成功，请注意查收邮件")
    return render_to_response(settings.TEMPLATE_VERIFICATION_SENT, 
        RequestContext(request, {"email": email}))

def confirm_email(request, confirmation_key):
    #已经激活,则无需重复激活
    confirmation_key = confirmation_key.lower()
    try:
        confirmEntity = EmailConfirmation.objects.get(confirmation_key=confirmation_key)
        if confirmEntity.email_address and confirmEntity.email_address.verified:
            return render_to_response(settings.TEMPLATE_CONFIRM_EMAIL, {
                "verified": True ,"msg": u"账号已处于激活状态,不需要重复激活",
            }, context_instance=RequestContext(request))
    except EmailConfirmation.DoesNotExist:
        return render_to_response(settings.TEMPLATE_CONFIRM_EMAIL,
            {"invalid": True, "msg": u"激活码无效"},                        
            context_instance=RequestContext(request)
        )
    
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)
    return render_to_response(settings.TEMPLATE_CONFIRM_EMAIL, {
        "email_address": email_address,
    }, context_instance=RequestContext(request))

@login_required
def email(request, **kwargs):
    
    form_class = kwargs.pop("form_class", AddEmailForm)
    template_name = kwargs.pop("template_name", "account/email.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST" and request.user.is_authenticated():
        if request.POST["action"] == "add":
            add_email_form = form_class(request.user, request.POST)
            if add_email_form.is_valid():
                add_email_form.save()
                messages.add_message(request, messages.INFO,
                    ugettext(u"Confirmation email sent to %(email)s") % {
                            "email": add_email_form.cleaned_data["email"]
                        }
                    )
                add_email_form = form_class() # @@@
        else:
            add_email_form = form_class()
            if request.POST["action"] == "send":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(
                        user=request.user,
                        email=email,
                    )
                    messages.add_message(request, messages.INFO,
                        ugettext("Confirmation email sent to %(email)s") % {
                            "email": email,
                        }
                    )
                    EmailConfirmation.objects.send_confirmation(email_address)
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "remove":
                email = request.POST["email"]
                try:
                    email_address = EmailAddress.objects.get(
                        user=request.user,
                        email=email
                    )
                    email_address.delete()
                    messages.add_message(request, messages.SUCCESS,
                        ugettext("Removed email address %(email)s") % {
                            "email": email,
                        }
                    )
                except EmailAddress.DoesNotExist:
                    pass
            elif request.POST["action"] == "primary":
                email = request.POST["email"]
                email_address = EmailAddress.objects.get(
                    user=request.user,
                    email=email,
                )
                email_address.set_as_primary()
    else:
        add_email_form = form_class()
    
    ctx = group_context(group, bridge)
    ctx.update({
        "add_email_form": add_email_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def password_change(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ChangePasswordForm)
    template_name = kwargs.pop("template_name", "account/change_password.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if not request.user.password:
        return HttpResponseRedirect(reverse("set_passwd"))
    
    if request.method == "POST":
        password_change_form = form_class(request.user, request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            utils.addMsg(request, messages.SUCCESS,
                ugettext(u"密码修改成功.")
            )
            password_change_form = form_class(request.user)
            
            return HttpResponseRedirect(reverse("profiles_setting"))
    else:
        password_change_form = form_class(request.user)
        
    ctx = group_context(group, bridge)
    ctx.update({
        "pwdform": password_change_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))
    


@login_required
def password_set(request, **kwargs):
    
    form_class = kwargs.pop("form_class", SetPasswordForm)
    template_name = kwargs.pop("template_name", "account/password_set.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.user.password:
        return HttpResponseRedirect(reverse("acct_passwd"))
    
    if request.method == "POST":
        password_set_form = form_class(request.user, request.POST)
        if password_set_form.is_valid():
            password_set_form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Password successfully set.")
            )
            return HttpResponseRedirect(reverse("acct_passwd"))
    else:
        password_set_form = form_class(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "password_set_form": password_set_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def password_delete(request, **kwargs):
    
    template_name = kwargs.pop("template_name", "account/password_delete.html")
    
    # prevent this view when openids is not present or it is empty.
    if not request.user.password or \
        (not hasattr(request, "openids") or \
            not getattr(request, "openids", None)):
        return HttpResponseForbidden()
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST":
        request.user.password = u""
        request.user.save()
        return HttpResponseRedirect(reverse("acct_passwd_delete_done"))
    
    ctx = group_context(group, bridge)
    
    return render_to_response(template_name, RequestContext(request, ctx))

@login_get_forbidden
def reset_password(request, **kwargs):
    form_class = kwargs.pop("form_class", ResetPasswordForm)
    template_name = kwargs.pop("template_name", settings.TEMPLATE_RESET_PASSWORD)
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
    if request.method == "POST":
        password_reset_form = form_class(request.POST)
        if password_reset_form.is_valid():
            email = password_reset_form.save()
            if group:
                redirect_to = bridge.reverse("acct_passwd_reset_done", group)
                return HttpResponseRedirect(redirect_to)
            else:
                redirect_to = reverse("acct_passwd_reset_done")
                return HttpResponseRedirect(redirect_to+"?email="+email)
    else:
        password_reset_form = form_class()
    
    ctx.update({
        "resetForm": password_reset_form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset_done(request, **kwargs):
    
    template_name = kwargs.pop("template_name", settings.TEMPLATE_PASSWORD_RESET_DONE)
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    ctx.update({
        "email": request.GET.get("email"),
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


def password_reset_from_key(request, uidb36, key, **kwargs):
    
    form_class = kwargs.get("form_class", ResetPasswordKeyForm)
    template_name = kwargs.get("template_name", settings.TEMPLATE_PASSWORD_RESET_FROM_KEY)
    token_generator = kwargs.get("token_generator", default_token_generator)
    
    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)
    
    # pull out user
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404
    
    user = get_object_or_404(User, id=uid_int)
    
    if token_generator.check_token(user, key):
        if request.method == "POST":
            password_reset_key_form = form_class(request.POST, user=user, temp_key=key)
            if password_reset_key_form.is_valid():
                password_reset_key_form.save()
                messages.add_message(request, messages.SUCCESS, ugettext(u"密码重置成功."))
                password_reset_key_form = None
        else:
            password_reset_key_form = form_class()
        ctx.update({
            "form": password_reset_key_form,
        })
    else:
        ctx.update({
            "token_fail": True,
        })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def timezone_change(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ChangeTimezoneForm)
    template_name = kwargs.pop("template_name", "account/timezone_change.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Timezone successfully updated.")
            )
    else:
        form = form_class(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "form": form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))


@login_required
def language_change(request, **kwargs):
    
    form_class = kwargs.pop("form_class", ChangeLanguageForm)
    template_name = kwargs.pop("template_name", "account/language_change.html")
    
    group, bridge = group_and_bridge(kwargs)
    
    if request.method == "POST":
        form = form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                ugettext(u"Language successfully updated.")
            )
            next = request.META.get("HTTP_REFERER", None)
            return HttpResponseRedirect(next)
    else:
        form = form_class(request.user)
    
    ctx = group_context(group, bridge)
    ctx.update({
        "form": form,
    })
    
    return render_to_response(template_name, RequestContext(request, ctx))

### for secure code 
from django.utils import simplejson as json
def checkIsLogin(request):
    """判断请求是否已登录"""
    if not request.user.is_authenticated():
        return HttpResponse(json.dumps({"status": "unlogin"}))
    
    return HttpResponse(json.dumps({"status": "login"}))

def isEmailRegistered(request):
    try:
        email = (request.GET.get("email")).strip()
    except ValueError, User.DoesNotExist:
        raise Http404("request params exception")

    user = None
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return HttpResponse(json.dumps({'status':'unused'}))    
    
    if user.is_active:
        return HttpResponse(json.dumps({'status':'used'}))
    return HttpResponse(json.dumps({'status':'unused'}))  


from common import img_utils 

def requestSecureImg(request):
    code = img_utils.generateCode()
    writeCode2Session(request, code)
    buffer = img_utils.drawSecureImg(code)
    buffer.closed
    return HttpResponse(buffer.getvalue(),'image/gif')


SECURE_CODE_KEY = "secureCode"

# 验证码验证方法
#@ensure_csrf_cookie
def checkSecureCode(request):
    try:
        secureCode = (request.POST.get("secureCode")).strip()
    except ValueError:
        raise Http404("request params exception")
    if secureCode.upper() == request.session[SECURE_CODE_KEY].upper():
        return HttpResponse(json.dumps({'status':'true'}))
    
    return HttpResponse(json.dumps({'status':'false', }))

def writeCode2Session(request, code):
    request.session[SECURE_CODE_KEY] = ''   # Initialize secure code in session, this is needed 
    for i in code:
        request.session[SECURE_CODE_KEY] += i

