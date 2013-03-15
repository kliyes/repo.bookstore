from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url(r"^create/$", "activity.views.createActivity", name="activity_create"),
    url(r"^(\d+)$", "activity.views.detailActivity", name="activity_detail"),   # check activity detail
    url(r"^join/(\d+)$", "activity.views.joinActivity", name="activity_join"),   
    url(r"^quit/(\d+)$", "activity.views.quitActivity", name="activity_quit"),   
    url(r"^like/(\d+)$", "activity.views.likeActivity", name="activity_like"),   
    url(r"^dislike/(\d+)$", "activity.views.dislikeActivity", name="activity_dislike"),
    url(r"^list/(\d+)$", "activity.views.getOnesActivities", name="activity_list"),
    

    #added by tom.jing for upload and cut post
    url(r"^upload_post/$", "activity.views.initPoster", name="activity_upload_poster"),
    url(r"^poster_set/$", "activity.views.setPoster", name="activity_set_poster"),
    url(r"^done_create/$", "activity.views.doneActivityCreating", name="activity_create_done"),
    url(r"^add_comment/(\d+)$", "activity.views.addComment", name="activity_add_comment"),
    url(r"^agree_comment/(\d+)$", "activity.views.agreeComment", name="activity_agree_comment"),
    url(r"^get_activities_on_terms/$", "activity.views.getActivitesByCityCategory", name="activity_get_on_terms"),
)