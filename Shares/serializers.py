import Users.models as user_models
import Shares.models as share_models
from rest_framework import serializers


class PortfolioSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = share_models.Portfolios
        exclude = ['id', 'portfolio_id']

    def get_company_name(self, obj):
        return obj.company_id.name


class WishlistSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = share_models.WishLists
        exclude = ['id', 'user_id', 'company_id']

    def get_company_name(self, obj):
        return obj.company_id.name


class TargetSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y/%m/%d %d %I:%M %p (UTC)")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %d %I:%M %p (UTC)")

    class Meta:
        model = user_models.Targets
        exclude = ['id', 'user_id', 'company_id']

    def get_company_name(self, obj):
        return obj.company_id.name


class ListedCompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = share_models.ListedCompanies
        exclude = ['id']


class NepseIndicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = share_models.NepseIndices
        exclude = ["id"]
