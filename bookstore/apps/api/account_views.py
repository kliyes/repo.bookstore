#coding=utf8


from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout

from common.utils import jsonResponse
from account.views import group_and_bridge
from account.models import EmailConfirmation
from account.forms import LoginForm, SignupForm
from protocol.decorators import post_request_required, authorized 
from api import errors
from api.consts import statusCode

EMAIL_AUTHENTICATION = getattr(settings, "ACCOUNT_EMAIL_AUTHENTICATION", False)
UNIQUE_EMAIL = getattr(settings, "ACCOUNT_UNIQUE_EMAIL", False)

ACCOUNT_NOT_EXIST = 1
ACCOUNT_NOT_ACTIVATED = 2 

@authorized
@post_request_required
def login(request, **kwargs):
    group, bridge = group_and_bridge(kwargs)
    form = LoginForm(request.POST, group=group)
    
    status = _checkEmail(request.POST.get("email", None)) 
    if status == ACCOUNT_NOT_EXIST:
        return jsonResponse(errors.ACCOUNT_NOT_EXIST)
    elif status == ACCOUNT_NOT_ACTIVATED:
        return jsonResponse(errors.ACCOUNT_NOT_ACTIVATED)
    
    if form.is_valid():
        form.login(request)
        request.session["failedLoginCount"] = 0
        request.user.get_profile().updateLoginCount()
        return jsonResponse(statusCode(0, "login successfully"))
    else:
        request.session["failedLoginCount"] = request.session.get("failedLoginCount", 0) + 1
        return jsonResponse(errors.EMAIL_OR_PASSWORD_ERR)
           
def _checkEmail(email):
    if UNIQUE_EMAIL or EMAIL_AUTHENTICATION:
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return ACCOUNT_NOT_EXIST
        
        if user:
            if not user.is_active:
                return ACCOUNT_NOT_ACTIVATED
    return 0 #other 
            
@authorized
@post_request_required
def signup(request, **kwargs):
    group, bridge = group_and_bridge(kwargs)
    form = SignupForm(request.POST, group=group)
    if form.is_valid():
        user, emailAddress = form.save(request=request)
        
        # 若注册需要Email激活,则发送邮件, 异步邮件队列方式发送邮件 
        if settings.ACCOUNT_EMAIL_VERIFICATION:
            user.is_active = False #default True
            user.save()
            EmailConfirmation.objects.send_confirmation(emailAddress)
            
            return jsonResponse(statusCode(0, """Signed up with %s successfullly. 
                Please activate your account """ % form.cleaned_data["email"]))
        
        # 不需要发送激活邮件,直接登录
        else:
            form.login(request, user)
            return jsonResponse(statusCode(1, "Signed up successfully"))
    else:
        return jsonResponse(errors.SIGNUP_ERR)  
    
@authorized
@post_request_required    
def logout(request, **kwargs):
    auth_logout(request)
    return jsonResponse(statusCode(0, "Logged out successfully"))
    #return jsonResponse({"status": 0, "msg": "Logged out successfully"})
