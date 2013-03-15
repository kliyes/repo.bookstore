from django.dispatch import Signal
 

profileUpdated = Signal(providing_args=["request", "profile"])
s_comment_success = Signal(providing_args=['comment'])
s_care_success = Signal(providing_args=['care'])
s_reply_success = Signal(providing_args=['reply'])
s_clear_session = Signal(providing_args=['request', 'dataKey'])