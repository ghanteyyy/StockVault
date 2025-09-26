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


class PortfolioLotsSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    purchased_date = serializers.SerializerMethodField()

    class Meta:
        model = models.PortfolioLots
        fields = ['id', 'company_name', 'number_of_shares', 'total_cost', 'user_email', 'purchased_date']

    def get_company_name(self, obj):
        return obj.portfolio_id.company_id.name

    def get_user_email(self, obj):
        return obj.portfolio_id.user_id.email

    def get_purchased_date(self, obj):
        return obj.purchased_date.strftime("%b %e, %Y")


class TransactionsSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    transacted_price = serializers.SerializerMethodField()
    transacted_date = serializers.SerializerMethodField()

    class Meta:
        model = models.Transactions
        fields = ['id', 'company_name', 'number_of_shares', 'user_email', 'transacted_price', 'transaction_type', 'transacted_date']

    def get_user_email(self, obj):
        return obj.user_id.email

    def get_company_name(self, obj):
        return obj.company_id.name

    def get_transacted_price(self, obj):
        return round(obj.transacted_price, 2)

    def get_transacted_date(self, obj):
        return obj.transaction_date.strftime("%b %e, %Y")


class FaqSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.FAQs
        fields = '__all__'
