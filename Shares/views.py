from django.shortcuts import render
from . import models as share_models
from Users import models as user_models


def AddToRecentActivities(request, company_id, activity_message):
    new_activity = share_models.RecentActivities(user_id=request.user, company_id=company_id, activity=activity_message)

    new_activity.save()
