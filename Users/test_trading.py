import csv
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from Shares.models import ListedCompanies, Portfolios, Transactions


class WorkspaceTradingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.member = users.create_user(email='trader@example.test', name='Demo Trader')
        cls.other = users.create_user(email='other@example.test', name='Other Trader')
        cls.company = ListedCompanies.objects.create(name='Demo Bank', abbreviation='DEMO')
        cls.other_company = ListedCompanies.objects.create(name='Other Company', abbreviation='OTHR')

    def setUp(self):
        self.trades = reverse('trades')
        self.history = reverse('transactions')
        self.client.force_login(self.member)

    def submit_trade(self, transaction_type, quantity, unit_price='', **fields):
        return self.client.post(self.trades, {
            'company': self.company.pk,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'unit_price': unit_price,
            'transaction_date': timezone.localdate().isoformat(),
            **fields,
        })

    def test_purchase_bonus_and_partial_sale_flow_through_the_workspace(self):
        key = self.client.get(self.trades).context['form_values']['idempotency_key']
        for _ in range(2):
            response = self.submit_trade('buy', 100, '100.25', purchase_type='ipo', idempotency_key=key)
            self.assertEqual(response.status_code, 302)
        self.assertEqual(self.submit_trade('buy', 50, '200.40').status_code, 302)
        self.assertEqual(self.submit_trade('bonus', 50, bonus_company=self.company.pk, company=self.other_company.pk).status_code, 302)
        self.assertEqual(Portfolios.objects.filter(user_id=self.member).count(), 1)

        response = self.client.get(self.trades, {
            'quote': '1', 'company': self.company.pk, 'transaction_type': 'sell', 'quantity': 25,
        })
        self.assertEqual(response.json()['holding'], {
            'quantity': 200,
            'total_cost': '20107.57',
            'average_cost': '100.54',
            'break_even_price': '101.96',
            'sell_quantity': 25,
            'allocated_cost': '2513.45',
        })

        response = self.submit_trade('sell', 25, '130.10', notes='Sample brokerage reference')
        self.assertEqual(response.status_code, 302)
        holding = Portfolios.objects.get(user_id=self.member, company_id=self.company)
        self.assertEqual((holding.number_of_shares, holding.total_cost), (175, Decimal('17594.12')))

        response = self.client.get(self.history)
        self.assertEqual(response.context['totals']['count'], 4)
        self.assertEqual(response.context['totals']['sales'], Decimal('3180.21'))
        self.assertContains(response, '666.76')
        self.assertContains(response, 'Sample brokerage reference')

    def test_invalid_trades_and_quotes_leave_the_holding_intact(self):
        self.assertEqual(self.submit_trade('buy', 10, '100.00', purchase_type='ipo').status_code, 302)
        for transaction_type, quantity, price in [('sell', 11, '101.00'), ('buy', 1, 'Infinity'), ('bonus', 0, '')]:
            with self.subTest(transaction_type=transaction_type):
                self.assertContains(self.submit_trade(transaction_type, quantity, price),
                                    'Check the transaction details.', status_code=400)
        self.assertContains(self.submit_trade('bonus', 1, bonus_company=self.other_company.pk),
                            'Bonus shares require an existing holding', status_code=400)
        response = self.client.get(self.trades, {
            'quote': '1', 'company': self.company.pk, 'transaction_type': 'sell', 'quantity': 11,
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('no-store', response.headers['Cache-Control'])
        holding = Portfolios.objects.get(user_id=self.member, company_id=self.company)
        self.assertEqual((holding.number_of_shares, holding.total_cost), (10, Decimal('1000.00')))
        self.assertEqual(Transactions.objects.filter(user_id=self.member).count(), 1)

    def test_history_export_and_quote_keep_other_accounts_private(self):
        Transactions.objects.create(
            user_id=self.member, company_id=self.company, transaction_type='SELL', number_of_shares=10,
            transacted_price=710, is_legacy=True, notes='  =SUM(1, 2)',
        )
        Transactions.objects.create(
            user_id=self.other, company_id=self.other_company, transaction_type='sell',
            transacted_price=900, is_legacy=True,
        )
        Portfolios.objects.create(
            user_id=self.other, company_id=self.other_company, number_of_shares=15, total_cost=750,
        )
        response = self.client.get(self.history, {'type': 'sell', 'q': 'DEMO'})
        self.assertContains(response, 'Historical record')
        self.assertContains(response, '710.00')
        self.assertNotContains(response, 'Other Company')
        self.assertIsNone(response.context['totals']['sales'])

        response = self.client.get(self.history, {'type': 'sell', 'export': 'csv'})
        records = list(csv.DictReader(StringIO(response.content.decode('utf-8-sig'))))
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['Company'], self.company.name)
        self.assertEqual(records[0]['Historical recorded total (NPR)'], '710.0')
        self.assertEqual(records[0]['Fees (NPR)'], '')
        self.assertEqual(records[0]['Net amount (NPR)'], '')
        self.assertEqual(records[0]['Notes'], "'  =SUM(1, 2)")

        response = self.client.get(self.trades, {'quote': '1', 'company': self.other_company.pk})
        self.assertEqual(response.json(), {'holding': None})
        self.assertIn('no-store', response.headers['Cache-Control'])

    def test_trade_post_requires_sign_in_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertRedirects(client.get(self.trades), f"{reverse('login')}?next={self.trades}", fetch_redirect_response=False)
        client.force_login(self.member)
        self.assertEqual(client.post(self.trades, {'company': self.company.pk}).status_code, 403)
        self.assertFalse(Transactions.objects.exists())
