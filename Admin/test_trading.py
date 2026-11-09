from decimal import Decimal

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from Shares.models import ListedCompanies, Portfolios, Transactions


class AdminTradingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.staff = users.create(email='trade-admin@example.test', name='Trade Admin', is_staff=True)
        cls.member = users.create(email='trader@example.test', name='Member Trader')
        cls.company = ListedCompanies.objects.create(name='Alpine Listing', abbreviation='ALP')

    def setUp(self):
        self.client.force_login(self.staff)

    def post(self, route, **values):
        return self.client.post(reverse(route), values)

    def trade(self, transaction_type='buy', **values):
        return {
            'user_id': self.member.pk,
            'company_id': self.company.pk,
            'transaction_type': transaction_type,
            'quantity': 10,
            'unit_price': '100.00',
            'purchase_type': 'ipo',
            'transaction_date': timezone.localdate().isoformat(),
            **values,
        }

    def holding(self):
        return Portfolios.objects.get(user_id=self.member, company_id=self.company)

    def test_management_requires_active_staff_post_and_csrf(self):
        endpoints = (
            'admin-transaction-add', 'admin-transaction-edit', 'admin-transaction-delete',
            'admin-holding-save', 'admin-holding-delete',
        )
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.client.get(reverse(endpoint)).status_code, 405)

        self.client.force_login(self.member)
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.post(endpoint).status_code, 403)

        guarded = Client(enforce_csrf_checks=True)
        guarded.force_login(self.staff)
        response = guarded.get(reverse('admin-transactions'))
        self.assertContains(response, 'Record transaction')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertEqual(guarded.post(reverse('admin-transaction-add'), self.trade()).status_code, 403)
        self.assertFalse(Transactions.objects.exists())
        response = guarded.post(
            reverse('admin-transaction-add'), self.trade(),
            HTTP_X_CSRFTOKEN=guarded.cookies['csrftoken'].value,
        )
        self.assertEqual(response.status_code, 200)

    def test_record_edit_and_delete_replay_holding_and_log_once(self):
        buy_data = self.trade(idempotency_key='admin-test-transaction')
        for _ in range(2):
            self.assertEqual(self.post('admin-transaction-add', **buy_data).status_code, 200)
        buy = Transactions.objects.get()
        self.assertEqual(self.holding().number_of_shares, 10)
        self.assertEqual(LogEntry.objects.filter(object_id=buy.pk, action_flag=ADDITION).count(), 1)

        self.assertEqual(self.post('admin-transaction-add', **self.trade('bonus', quantity=5, unit_price='')).status_code, 200)
        self.assertEqual(self.holding().number_of_shares, 15)
        self.assertEqual(self.holding().total_cost, Decimal('1000.00'))
        response = self.client.get(reverse('admin-transactions'), {'type': 'bonus'})
        self.assertContains(response, 'Bonus shares')
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

        sell_data = self.trade('sell', quantity=12, unit_price='150.00')
        self.assertEqual(self.post('admin-transaction-add', **sell_data).status_code, 200)
        sale = Transactions.objects.get(transaction_type='sell')
        self.assertEqual(self.holding().number_of_shares, 3)
        self.assertEqual(sale.cost_basis, Decimal('800.00'))

        response = self.post('admin-transaction-edit', **self.trade(transaction_id=buy.pk, quantity=5))
        self.assertEqual(response.status_code, 400)
        response = self.post('admin-transaction-delete', transaction_id=buy.pk, confirm='yes')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.holding().number_of_shares, 3)
        self.assertEqual(Transactions.objects.get(pk=buy.pk).number_of_shares, 10)
        self.assertFalse(LogEntry.objects.filter(object_id=buy.pk).exclude(action_flag=ADDITION).exists())

        response = self.post('admin-transaction-edit', **self.trade(transaction_id=buy.pk, quantity=15))
        self.assertEqual(response.status_code, 200)
        sale.refresh_from_db()
        self.assertEqual(sale.cost_basis, Decimal('900.00'))
        self.assertEqual(self.holding().number_of_shares, 8)
        self.assertEqual(self.holding().total_cost, Decimal('600.00'))

        self.assertEqual(self.post('admin-transaction-delete', transaction_id=sale.pk).status_code, 400)
        self.assertEqual(self.post('admin-transaction-delete', transaction_id=sale.pk, confirm='yes').status_code, 200)
        self.assertEqual(self.holding().number_of_shares, 20)
        self.assertEqual(self.holding().total_cost, Decimal('1500.00'))
        self.assertTrue(LogEntry.objects.filter(object_id=buy.pk, action_flag=CHANGE).exists())
        self.assertTrue(LogEntry.objects.filter(object_id=sale.pk, action_flag=DELETION).exists())

    def test_opening_balance_crud_preserves_historical_records(self):
        opening = {'user_id': self.member.pk, 'company_id': self.company.pk, 'quantity': 8, 'total_cost': '400.00'}
        self.assertEqual(self.post('admin-holding-save', **opening).status_code, 200)
        self.assertEqual(self.post('admin-holding-save', **opening).status_code, 400)
        holding = self.holding()
        history = Transactions.objects.create(
            user_id=self.member, company_id=self.company, number_of_shares=8,
            transacted_price=400.00, transaction_type='BUY', is_legacy=True,
        )
        response = self.client.get(reverse('admin-portfolios'))
        self.assertContains(response, 'Edit opening')
        response = self.client.get(reverse('admin-transactions'))
        self.assertContains(response, 'Historical record')
        correction = self.trade(transaction_id=history.pk, quantity=9, legacy_amount='450.00')
        correction.pop('unit_price')
        self.assertEqual(self.post('admin-transaction-edit', **correction).status_code, 200)
        history.refresh_from_db()
        self.assertEqual(history.transacted_price, 450)
        self.assertEqual(self.holding().number_of_shares, 8)

        self.assertEqual(self.post('admin-holding-save', holding_id=holding.pk, quantity=10, total_cost='500.00').status_code, 200)
        self.assertEqual(self.holding().number_of_shares, 10)
        self.assertEqual(self.post('admin-holding-delete', holding_id=holding.pk, confirm='yes').status_code, 200)
        self.assertFalse(Portfolios.objects.filter(pk=holding.pk).exists())
        self.assertTrue(Transactions.objects.filter(pk=history.pk).exists())

    def test_holding_with_active_ledger_cannot_be_deleted(self):
        self.assertEqual(self.post('admin-transaction-add', **self.trade()).status_code, 200)
        holding = self.holding()
        response = self.post('admin-holding-delete', holding_id=holding.pk, confirm='yes')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Portfolios.objects.filter(pk=holding.pk).exists())
        self.assertFalse(LogEntry.objects.filter(object_id=holding.pk, action_flag=DELETION).exists())
