import Users.models as user_models
from rest_framework import serializers


class MeSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%B %d, %Y at %I:%M %p (UTC)")
    date_of_birth = serializers.DateField(format="%B %d, %Y")

    class Meta:
        model = user_models.CustomUser
        exclude = ['password', 'last_login', 'groups', 'user_permissions', 'first_name', 'last_name']


class TargetSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y/%m/%d %d %I:%M %p (UTC)")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %d %I:%M %p (UTC)")

    class Meta:
        model = user_models.Targets
        exclude = ['id', 'user_id', 'company_id']

    def get_company_name(self, obj):
        return obj.company_id.name


class TestinomialSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = user_models.Testonomials
        exclude = ['id', 'user_id', 'created_at']

    def get_user_name(self, obj):
        return obj.user_id.name