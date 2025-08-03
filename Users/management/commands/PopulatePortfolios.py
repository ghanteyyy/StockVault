import random
import datetime
import Users.models as user_models
import Shares.models as share_models
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def generate_random_date(self):
        start_date = datetime.date(2020, 1, 1)
        end_date = datetime.date.today()

        return start_date + (end_date - start_date) * random.random()

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
                portfolio = share_models.Portfolios.objects.filter(user_id=user, company_id=company)

                number_of_shares = random.randint(100, 300)
                rate = round(random.uniform(150.0, 700.0), 2)
                total_cost = number_of_shares * rate

                if portfolio.exists():
                    portfolio = portfolio.first()
                    portfolio.number_of_shares += number_of_shares
                    portfolio.total_cost += total_cost

                else:
                    portfolio = share_models.Portfolios(user_id=user, company_id=company, number_of_shares=number_of_shares, total_cost=total_cost)

                portfolio.save()

                # Create PortfolioLots
                portfolio_lot = share_models.PortfolioLots(
                    portfolio_id=portfolio,
                    total_cost=total_cost,
                    number_of_shares=number_of_shares,
                    purchased_date=self.generate_random_date()
                )
                portfolio_lot.save()

                # Create Transactions
                transaction = share_models.Transactions(
                    user_id=user,
                    company_id=company,
                    number_of_shares=number_of_shares,
                    transacted_price=total_cost,
                    transaction_type='buy',
                    transaction_date=self.generate_random_date()
                )

                transaction.save()


    def handle(self, *args, **options):
        self._create_tags()
