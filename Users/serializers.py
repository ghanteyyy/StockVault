from . import models as user_models
from Shares import models as share_models
from rest_framework import serializers


class RecentActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.RecentActivities
        fields = ['id', 'activity', 'recorded_at']


class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = share_models.ListedCompanies
        fields = ['id', 'name', 'abbreviation']


class WishlistsSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = share_models.WishLists
        fields = ['id', 'user_email', 'company_name']

    def get_user_email(self, obj):
        return obj.user_id.email

    def get_company_name(self, obj):
        return obj.company_id.name
