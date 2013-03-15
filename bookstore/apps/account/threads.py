'''
Created on Nov 2, 2012

@author: junn
'''

import threading, logging
logger = logging.getLogger("mysite")

from django.core.mail import send_mail

from common import utils

class EmailSendThread(threading.Thread):
    """Use many-threads to send email """
    
    def __init__(self, subject, message, from_email, recipient_list):
        threading.Thread.__init__(self)
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        
    def run(self):
        logger.debug("Email sending thread started...")
        print "Email sending thread started..."
        
        try:
            send_mail(self.subject, self.message, self.from_email, self.recipient_list)
        except:
            print utils.traceBack()  # use loger later TODO 
            
        logger.debug("Email sending thread end")
        print("Email sending end")

def startEmailSendThread(subject, message, from_email, recipient_list):
    EmailSendThread(subject, message, from_email, recipient_list).start()