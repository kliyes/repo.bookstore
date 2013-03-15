#coding=utf8

'''
Created on Oct 26, 2012

@author: junn
'''

"""
Define all errors info wiht json format in this module, All are reusable level.

系统级错误:
    10000: 访问权限错误,无client_key
    10001: client key error

服务级错误
    200000-200999: 服务级通用错误
    201000-201999: 账号管理
    202000-202999: 活动管理
    203000-203999: 用户管理
    ...

示例:    
202001:  2服务级错误     02服务模块代码     001具体错误代码     
"""


class ErrorObj:
    """错误类,用于格式化错误数据成指定json对象
    """
    def __init__(self, errCode, errMsg):
        self.errCode = errCode
        self.errMsg = errMsg
    
    def format(self, *args, **kwargs):
        return {
            "err_code": self.errCode, 
            "err_msg":self.errMsg.format(*args, **kwargs)
        }
    
    def __unicode__(self):
        return {"err_code": self.errCode, "err_msg":self.errMsg}


############################  system level errors #############################
CLIENT_AUTHORIZED_ERR = ErrorObj(10000, u"Access authorized error")
CLIENT_KEY_ERR = ErrorObj(10001, u"client key error")
NOT_POST_REQUEST = ErrorObj(10002, "Post request is required")

HTTP404_ERR = ErrorObj(200404, u"Object Not found")
HTTP500_ERR = ErrorObj(200500, u"500 server error")

########################### service level errors #############################
# Account
ACCOUNT_NOT_EXIST = ErrorObj(201000, u"Account not exists")
ACCOUNT_IS_REGISTERED = ErrorObj(201001, u"Email has been registered")
ACCOUNT_NOT_ACTIVATED = ErrorObj(201002, u"Account not activated")
EMAIL_OR_PASSWORD_ERR = ErrorObj(201003, "Email or password error")
SIGNUP_ERR = ErrorObj(201004, "Please fill out the correct email or password")

# Activity
ACTIVITY_NOT_EXIST = ErrorObj(202000, "Activity {0} not exist")  
ACTIVITY_DETAIL_ERR = ErrorObj(202001, "Get activity {0} detail failed")   #获取活动详情错误
ACTIVITY_JOIN_ERR = ErrorObj(202002, "Joined into activity {0} failed")    #参加活动错误

# Profile
PROFILE_UPDATE_ERR = ErrorObj(203001, "Update profile failed:{msg}")      




