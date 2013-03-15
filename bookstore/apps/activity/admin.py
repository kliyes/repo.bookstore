from django.contrib import admin

from activity.models import Activity
from activity.models import City
from activity.models import Comment
from profiles.models import Profile


admin.site.register(Activity)
admin.site.register(City)
admin.site.register(Comment)
