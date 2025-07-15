import random
from Shares.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        number_of_days_to_populate = int(input("Enter the number of days for which you want to generate historical prices: "))
        listed_companies = ListedCompanies.objects.all()

        historical_prices = []

        for days in range(number_of_days_to_populate):
            for company_id in listed_companies:
                opening_price = random.randint(200, 800)
                closing_price = random.randint(100, 800)
                historical_prices.append(HistoricalPrices(company_id=company_id, opening_price=opening_price, closing_price=closing_price, recorded_at=now()))

        HistoricalPrices.objects.bulk_create(historical_prices)

    def handle(self, *args, **options):
        self._create_tags()
