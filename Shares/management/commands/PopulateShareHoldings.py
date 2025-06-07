import random
from Users.models import *
from Shares.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        listed_companies = ListedCompanies.objects.all()
        user = input("Enter email for which you want to populate share holdings: ")
        number_of_shares_to_populate = int(input(f"Enter the number of shares holdings to populate for {user}: "))

        share_holdings = []
        user_id = CustomUser.objects.get(email=user)

        for _ in range(number_of_shares_to_populate):
            company_id = random.choice(listed_companies)
            quantity = random.randint(10, 200)
            price_per_share = random.randint(100, 200)

            share_holdings.append(ShareHoldings(user_id=user_id, company_id=company_id, quantity=quantity, price_per_share=price_per_share))

        ShareHoldings.objects.bulk_create(share_holdings)

    def handle(self, *args, **options):
        self._create_tags()
