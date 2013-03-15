#coding=utf8

'''
Created on Oct 31, 2012

@author: junn
'''

"""
All constants put in here
"""

CLIENT_KEY = "client_key"

def statusCode(status, msg):
    return {"status": status, "msg":msg}

#class ActionResult:
#    """操作结果信息,用于格式化操作结果成指定json对象
#    """
#    def __init__(self, status, msg):
#        self.id = status
#        self.label = msg
#    
#    def format(self, *args, **kwargs):
#        return {
#            "id":self.id, 
#            "label":   self.label.format(*args, **kwargs)
#        }
#    
#    def __unicode__(self):
#        return {"id": self.id, "label":self.label}
    
    