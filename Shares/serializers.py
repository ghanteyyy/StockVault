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


class PortfoliosSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    abbreviation = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = models.Portfolios
        fields = ['id', 'company_name', 'abbreviation', 'number_of_shares', 'total_cost', 'user_email']

    def get_company_name(self, obj):
        return obj.company_id.name

    def get_abbreviation(self, obj):
        return obj.company_id.abbreviation

    def get_user_email(self, obj):
        return obj.user_id.email


class TransactionsSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    transacted_price = serializers.SerializerMethodField()

    class Meta:
        model = models.Transactions
        fields = ['id', 'company_name', 'number_of_shares', 'transacted_price', 'transaction_type', 'transaction_date']

    def get_company_name(self, obj):
        return obj.company_id.name

    def get_transacted_price(self, obj):
        return round(obj.transacted_price, 2)


class FaqSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.FAQs
        fields = '__all__'
