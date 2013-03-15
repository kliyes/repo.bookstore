from profiles.models import Profile

def get_profile(request):
    user = request.user
    if user.is_authenticated():
        try:
            profile  = user.get_profile()
        except Profile.DoesNotExist:    
            profile = Profile(user=user, name=user.username)
            profile.save()
    else:
        profile = "Anonymous"    
    
    return {
        "profile": profile,
    }    
    
def getNoticeCount(request):
    return  {}