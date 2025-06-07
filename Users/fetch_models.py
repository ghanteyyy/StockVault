from . import models
from .serializers import *


def fetch_recent_activities(request):
    activities = models.RecentActivities.objects.filter(user_id=request.user)

    return RecentActivitiesSerializer(activities, many=True).data
