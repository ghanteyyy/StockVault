import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from Shares.models import ListedCompanies, Portfolios, Transactions
from Shares.trading import record_transaction


@override_settings(RATELIMIT_ENABLE=False)
class PortfolioTradingIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = get_user_model().objects.create_user('portfolio@example.test', name='Portfolio Member')
        cls.company = ListedCompanies.objects.create(name='Ledger Bank', abbreviation='LGR', sector='Banking')

    def setUp(self):
        self.client.force_login(self.member)

    def buy(self, quantity=10):
        return record_transaction(
            user=self.member, company=self.company, transaction_type='buy',
            quantity=quantity, unit_price='100.25', purchase_type='ipo',
        )

    def test_existing_portfolio_purchase_posts_write_to_the_shared_ledger(self):
        self.buy()
        response = self.client.post(reverse('portfolio'), {
            'company': self.company.name, 'share_quantity': '5',
            'buying_rate': '115.50', 'buy-type': 'ipo',
        })
        self.assertRedirects(response, reverse('portfolio'), fetch_redirect_response=False)
        holding = Portfolios.objects.get(user_id=self.member, company_id=self.company)
        self.assertEqual(holding.number_of_shares, 15)
        self.assertEqual(holding.total_cost, Decimal('1580.00'))
        self.assertEqual(Transactions.objects.filter(user_id=self.member, is_legacy=False).count(), 2)

    @patch('Users.portfolio_views._market_quote', return_value=None)
    def test_portfolio_remains_readable_without_market_data_and_get_cannot_delete(self, quote):
        self.buy()
        holding = Portfolios.objects.get(user_id=self.member, company_id=self.company)
        response = self.client.get(reverse('portfolio'), {'action': 'delete', 'portfolio_id': holding.pk})
        self.assertContains(response, 'Market price is currently unavailable')
        self.assertContains(response, 'Break-even / share')
        self.assertContains(response, f'{reverse("trades")}?company={self.company.pk}')
        self.assertTrue(Portfolios.objects.filter(pk=holding.pk).exists())

    def test_portfolio_remove_endpoint_protects_ledger_balances(self):
        self.buy()
        response = self.client.post(reverse('portfolio-delete'), json.dumps({'company_id': self.company.pk}), content_type='application/json')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Portfolios.objects.get(user_id=self.member, company_id=self.company).number_of_shares, 10)
        self.assertEqual(Transactions.objects.filter(user_id=self.member).count(), 1)

    def test_dashboard_uses_recorded_net_sales_and_ignores_closed_holdings(self):
        self.buy()
        sale = record_transaction(
            user=self.member, company=self.company, transaction_type='sell',
            quantity=10, unit_price='150.50',
        )
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.context['total_sales']), sale.net_amount)
        self.assertEqual(Decimal(response.context['total_investment']), Decimal('0.00'))
        self.assertEqual(response.context['data_per_company_sector'], {})
