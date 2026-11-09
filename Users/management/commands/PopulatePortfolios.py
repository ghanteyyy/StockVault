import random
import datetime
import Users.models as user_models
import Shares.models as share_models
from Shares.trading import record_transaction
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def generate_random_date(self):
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date.today()

        delta = end_date - start_date
        random_days = random.randint(0, delta.days)

        return start_date + datetime.timedelta(days=random_days)

    def _create_tags(self):
        companies = share_models.ListedCompanies.objects.all()

        if not companies.exists():
            self.stdout.write(self.style.ERROR("No listed companies found. Please add companies first."))
            return

        number_of_portfolios_to_populate = int(input("Enter the number of portfolios to populate: "))
        users = input("Enter the user names to populate (comma-separated): ")

        if users == 'all':
            users = user_models.CustomUser.objects.filter(is_staff=False, is_superuser=False)

        else:
            users = [user.strip() for user in users.split(',')]
            users = user_models.CustomUser.objects.filter(email__in=users)

        for user in users:
            for i in range(number_of_portfolios_to_populate):
                company = random.choice(companies)
                number_of_shares = random.randint(100, 300)
                rate = round(random.uniform(150.0, 700.0), 2)

                record_transaction(
                    user=user, company=company, transaction_type='buy',
                    quantity=number_of_shares, unit_price=rate,
                    purchase_type=random.choice(['ipo', 'secondary']),
                    transaction_date=self.generate_random_date(),
                )

    def handle(self, *args, **options):
        self._create_tags()
