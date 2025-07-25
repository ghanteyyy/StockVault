import datetime as dt
from rest_framework import serializers
from . import models
from rest_framework import serializers


class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListedCompanies
        fields = ['id', 'name', 'abbreviation']


class WishlistsSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = models.WishLists
        fields = ['id', 'user_email', 'company_name']

    def get_user_email(self, obj):
        return obj.user_id.email

    def get_company_name(self, obj):
        return obj.company_id.name


class ShareHoldingsSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    abbreviation = serializers.SerializerMethodField()

    class Meta:
        model = models.ShareHoldings
        fields = ['id', 'company_name', 'abbreviation', 'number_of_shares', 'total_cost']

    def get_company_name(self, obj):
        return obj.company_id.name

    def get_abbreviation(self, obj):
        return obj.company_id.abbreviation


class HistoricalPricesSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = models.HistoricalPrices


class RecentActivitiesSerializer(serializers.ModelSerializer):
    recorded_at = serializers.SerializerMethodField()

    class Meta:
        model = models.RecentActivities
        fields = ['id', 'activity', 'recorded_at']


    def get_recorded_at(self, obj):
        formatted_dt = obj.recorded_at.strftime("%Y-%m-%d")

        return str(formatted_dt)
