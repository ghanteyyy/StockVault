from . import models
from rest_framework import serializers



class RecentActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RecentActivities
        fields = ['id', 'activity', 'recorded_at']
