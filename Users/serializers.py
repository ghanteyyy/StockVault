from rest_framework import serializers
from . import models
from rest_framework import serializers


class TargetsSerializer(serializers.ModelSerializer):
    abbreviation = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    company_id = serializers.SerializerMethodField()

    class Meta:
        model = models.Targets
        fields = ['id', 'company_name', 'company_id', 'abbreviation', 'low_target', 'high_target', 'target_type']

    def get_company_name(self, obj):
        return obj.company_id.name

    def get_abbreviation(self, obj):
        return obj.company_id.abbreviation

    def get_company_id(self, obj):
        return obj.company_id.id


class TestonomialsSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Testonomials
        fields = ['id', 'user_name', 'message', 'created_at']

    def get_user_name(self, obj):
        return obj.user_id.name
