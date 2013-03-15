#coding=utf8

'''
Created on Oct 31, 2012

@author: junn
'''

"""
All constants put in here
"""

class Category:
    """操作结果信息,用于格式化操作结果成指定json对象
    """
    id = None
    label = None
    
    def __init__(self, id, label):
        self.id = id
        self.label = label
    
    def format(self, *args, **kwargs):
        return {
            "id":self.id, 
            "label":   self.label.format(*args, **kwargs)
        }
    
    def __unicode__(self):
        return {"id": self.id, "label":self.label}

CATEGORY_IT = Category(1, 'IT')
CATEGORY_STARTUP = Category(2, u'创业')
CATEGORY_COLLEGE = Category(3, u'大学生')
CATEGORY_OTHER = Category(99, u'其他')

def getActivityCategorys():
    return (
        CATEGORY_IT, CATEGORY_STARTUP, CATEGORY_COLLEGE, CATEGORY_OTHER,
    )
    
    