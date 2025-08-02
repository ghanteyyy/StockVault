import random
import datetime
import Users.models as user_models
import Shares.models as share_models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def generate_random_date(self, start_date, end_date):
        """
        Generate a random date between start_date and end_date.
        """

        delta = end_date - start_date
        random_days = random.randint(0, delta.days)

        return start_date + datetime.timedelta(days=random_days)

    def _create_tags(self):
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.datetime.today().date()

        users = user_models.CustomUser.objects.filter(is_staff=False, is_superuser=False)
        companies = share_models.ListedCompanies.objects.all()

        for user in users:
            number_of_transactions = random.randint(30, 100)

            for _ in range(number_of_transactions):
                company = random.choice(companies)
                transacted_price = round(random.uniform(100.0, 500.0), 2)

                number_of_shares = random.randint(15, 100)
                transaction_type = random.choice(['buy', 'sell'])
                transaction_date = self.generate_random_date(start_date, end_date)

                share_models.Transactions.objects.create(
                                    user_id=user,
                                    company_id=company,
                                    number_of_shares=number_of_shares,
                                    transacted_price=transacted_price,
                                    transaction_type=transaction_type,
                                    transaction_date=transaction_date
                                )

    def handle(self, *args, **options):
        self._create_tags()
