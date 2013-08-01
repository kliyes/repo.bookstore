#coding=utf-8
#
# Copyright (C) 2012-2013 XIZHI TECH Co., Ltd. All rights reserved.
# Created on 2013-8-1, by Tom
#
#
from rest_framework.generics import GenericAPIView
from account.forms import LoginForm
from rest_framework.response import Response
from rest_framework import status

class Login(GenericAPIView):
    '''登录'''
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            form.login(request)
            profile = request.user.get_profile()
            return Response({'id': profile.id, 'name': profile.name})
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)