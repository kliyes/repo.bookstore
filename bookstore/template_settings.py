#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

"""
All html templates are setup here, mainly used in views layer
"""

TEMPLATE_INDEX = "index.html"
TEMPLATE_HOME = "home.html"

""" account """
TEMPLATE_LOGIN = "account/login.html"
TEMPLATE_AJAX_LOGIN = "account/includes/ajax_login.html"
TEMPLATE_SIGNUP = "account/signup.html"
TEMPLATE_VERIFICATION_SENT = "account/verification_sent.html"
TEMPLATE_CONFIRM_EMAIL = "account/confirm_email.html"
TEMPLATE_RESET_PASSWORD = "account/reset_passwd.html"
TEMPLATE_PASSWORD_RESET_DONE = "account/password_reset_done.html"
TEMPLATE_PASSWORD_RESET_FROM_KEY = "account/password_reset_from_key.html"

""" profiles """
TEMPLATE_SETTINGS = "profiles/settings.html"
TEMPLATE_SETUP_PICTURE = "profiles/set_picture.html"
TEMPLATE_USER_PAGE = "profiles/user_page.html"

TEMPLATE_NOTIFICATIONS = "profiles/notifications.html"
TEMPLATE_MYFANS = "profiles/myfans.html"
TEMPLATE_MYHEROS = "profiles/myheros.html"
TEMPLATE_ONESFANS = "profiles/onesfans.html"

""" activity """
TEMPLATE_CREATE_ACTIVITY = "activity/create_activity.html"
TEMPLATE_ACTIVITY_DETAIL = "activity/activity_detail.html"
TEMPLATE_SET_POSTER = "activity/set_poster.html"
TEMPLATE_ACTIVITY_CREATE_DONE = 'activity/activity_create_done.html'
TEMPLATE_LATEST_ACTIVITY = "activity/includes/latest_activity.html"
TEMPLATE_HOTEST_ACTIVITY = "activity/includes/hotest_activity.html"

""" site """
TEMPLATE_FEEDBACK = "site/feedback.html"
