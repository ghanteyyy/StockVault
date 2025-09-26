from rest_framework import serializers
from . import models
from rest_framework import serializers


class TargetsSerializer(serializers.ModelSerializer):
    abbreviation = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    company_id = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    class Meta:
        model = models.Targets
        fields = ['id', 'user_email', 'company_name', 'company_id', 'abbreviation', 'low_target', 'high_target', 'target_type', 'created_date']

    def get_company_name(self, obj):
        return obj.company_id.name

    def get_abbreviation(self, obj):
        return obj.company_id.abbreviation

    def get_company_id(self, obj):
        return obj.company_id.id

    def get_user_email(self, obj):
        return obj.user_id.email

    def get_created_date(self, obj):
        return obj.created_at.strftime("%b %e, %Y")

class TestonomialsSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Testonomials
        fields = ['id', 'user_name', 'message', 'created_at']

    def get_user_name(self, obj):
        return obj.user_id.name
