from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from Shares import trading
from Shares.models import ListedCompanies, Portfolios, Transactions


class TradeLedgerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = get_user_model().objects.create_user(email='ledger@example.test', name='Ledger Example')
        cls.company = ListedCompanies.objects.create(name='Ledger Example Ltd', abbreviation='LEDG', sector='Test')

    def trade(self, kind, quantity, price=0, **kwargs):
        return trading.record_transaction(
            user=self.member, company=self.company, transaction_type=kind,
            quantity=quantity, unit_price=price, **kwargs,
        )

    def holding(self):
        return Portfolios.objects.get(user_id=self.member, company_id=self.company)

    def test_purchases_bonus_and_partial_sale_share_one_weighted_balance(self):
        self.trade('buy', 100, 100, purchase_type='ipo')
        second_buy = self.trade('buy', 50, 200)
        bonus = self.trade('bonus', 50)
        before_sale = self.holding()
        self.assertEqual(second_buy.fees, Decimal('62.50'))
        self.assertEqual(bonus.net_amount, Decimal('0.00'))
        self.assertEqual(before_sale.number_of_shares, 200)
        self.assertEqual(before_sale.total_cost, Decimal('20062.50'))
        self.assertEqual(trading.holding_summary(before_sale)['average_cost'], Decimal('100.31'))

        sale = self.trade('sell', 40, 150)
        self.assertEqual(sale.cost_basis, Decimal('4012.50'))
        self.assertEqual(sale.fees, Decimal('47.50'))
        self.assertEqual(sale.capital_gains_tax, Decimal('97.00'))
        self.assertEqual(sale.net_amount, Decimal('5855.50'))
        self.assertEqual(sale.realized_gain, Decimal('1843.00'))
        self.assertEqual(self.holding().number_of_shares, 160)
        self.assertEqual(self.holding().total_cost, Decimal('16050.00'))

        closing_sale = self.trade('sell', 160, 200)
        self.assertEqual(closing_sale.cost_basis, Decimal('16050.00'))
        self.assertEqual(self.holding().number_of_shares, 0)
        self.assertEqual(self.holding().total_cost, Decimal('0.00'))

    def test_break_even_accounts_for_fee_slab_boundary(self):
        holding = Portfolios(number_of_shares=100, total_cost=Decimal('49795.00'))
        summary = trading.holding_summary(holding)
        price = summary['break_even_price']
        self.assertEqual(price, Decimal('500.01'))
        args = {'quantity': 100, 'total_cost': holding.total_cost}
        self.assertGreaterEqual(trading.sale_preview(selling_price=price, **args)['net_amount'], holding.total_cost)
        self.assertLess(trading.sale_preview(selling_price=price - Decimal('0.01'), **args)['net_amount'], holding.total_cost)

    def test_break_even_finds_first_penny_when_two_fees_round_up_together(self):
        holding = Portfolios(number_of_shares=1, total_cost=Decimal('1.24'))
        fees = {
            'broker': {'min_brokerage': Decimal('0'), 'slabs': [(Decimal('Infinity'), Decimal('0.004'))]},
            'sebon_fee_rate': Decimal('0.004'),
            'dp_charge': Decimal('0'),
        }
        with patch.dict(trading.calculator.charges, fees):
            summary = trading.holding_summary(holding)
            next_penny = trading.sale_preview(quantity=1, total_cost=holding.total_cost, selling_price='1.25')
        self.assertEqual(summary['break_even_price'], Decimal('1.24'))
        self.assertEqual(next_penny['net_amount'], Decimal('1.23'))

    def test_oversized_realized_loss_is_rejected_before_saving(self):
        # Use a smaller service limit to exercise the guard independently of
        # SQLite's precision for very large DecimalField values.
        with patch.object(trading, 'MAX_MONEY', Decimal('1000.00')):
            trading.set_opening_balance(user=self.member, company=self.company, quantity=1, total_cost=1000)
            preview = trading.sale_preview(quantity=1, total_cost=1000, selling_price='0.01')
            self.assertLess(preview['realized_gain'], Decimal('-1000.00'))
            with self.assertRaisesMessage(ValidationError, 'The sale result is outside the supported range.'):
                self.trade('sell', 1, '0.01')
        self.assertFalse(Transactions.objects.exists())
        self.assertEqual(self.holding().total_cost, Decimal('1000.00'))

    def test_admin_corrections_replay_later_sales_and_roll_back_impossible_edits(self):
        purchase = self.trade('buy', 50, 100, purchase_type='ipo')
        sale = self.trade('sell', 40, 150)
        with self.assertRaises(ValidationError):
            trading.update_transaction(purchase, quantity=39)
        with self.assertRaises(ValidationError):
            trading.delete_transaction(purchase)
        purchase.refresh_from_db()
        self.assertEqual(purchase.number_of_shares, 50)
        self.assertEqual(self.holding().number_of_shares, 10)

        trading.update_transaction(purchase, unit_price='110.25')
        sale.refresh_from_db()
        self.assertEqual(sale.cost_basis, Decimal('4410.00'))
        self.assertEqual(self.holding().total_cost, Decimal('1102.50'))
        trading.delete_transaction(sale)
        self.assertEqual(self.holding().number_of_shares, 50)
        self.assertEqual(self.holding().total_cost, Decimal('5512.50'))

    def test_invalid_entries_and_backdated_oversell_leave_ledger_unchanged(self):
        with self.assertRaises(ValidationError):
            self.trade('bonus', 10)
        with self.assertRaises(ValidationError):
            self.trade('buy', 10, 'NaN')
        with self.assertRaises(ValidationError):
            self.trade('buy', 10, '1.001')
        self.assertFalse(Portfolios.objects.exists())
        self.trade('buy', 10, 100, purchase_type='ipo')
        with self.assertRaises(ValidationError):
            self.trade('sell', 11, 100)
        with self.assertRaises(ValidationError):
            self.trade('sell', 1, 100, transaction_date=timezone.localdate() - timedelta(days=1))
        with self.assertRaises(ValidationError):
            self.trade('buy', 1, 100, transaction_date=timezone.localdate() + timedelta(days=1))
        self.assertEqual(Transactions.objects.count(), 1)
        self.assertEqual(self.holding().number_of_shares, 10)

    def test_retry_reuses_entry_and_conflicting_retry_is_rejected(self):
        first = self.trade('buy', 10, 100, purchase_type='ipo', idempotency_key='buy-request-123')
        repeated = self.trade('buy', 10, 100, purchase_type='ipo', idempotency_key='buy-request-123')
        self.assertEqual(first.pk, repeated.pk)
        with self.assertRaises(ValidationError):
            self.trade('buy', 11, 100, purchase_type='ipo', idempotency_key='buy-request-123')
        self.assertEqual(Transactions.objects.count(), 1)
        self.assertEqual(self.holding().number_of_shares, 10)

    def test_opening_balance_edits_replay_new_entries_without_changing_legacy_history(self):
        opening = trading.set_opening_balance(user=self.member, company=self.company, quantity=20, total_cost=2000, create_only=True)
        legacy = Transactions.objects.create(
            user_id=self.member, company_id=self.company, transaction_type='BUY',
            number_of_shares=20, transacted_price=2000, is_legacy=True,
        )
        sale = self.trade('sell', 10, 150)
        with self.assertRaises(ValidationError):
            trading.set_opening_balance(user=self.member, company=self.company, quantity=20, total_cost=2000, create_only=True)
        with self.assertRaises(ValidationError):
            trading.delete_holding(opening)
        corrected = trading.set_opening_balance(user=self.member, company=self.company, quantity=30, total_cost=2700, holding_id=opening.pk)
        trading.update_transaction(legacy, quantity=19, legacy_amount='1890.00')
        sale.refresh_from_db()
        self.assertEqual(sale.cost_basis, Decimal('900.00'))
        self.assertEqual(corrected.number_of_shares, 20)
        self.assertEqual(self.holding().total_cost, Decimal('1800.00'))


class OpeningBalanceMigrationTests(TransactionTestCase):
    before = ('Shares', '0009_alter_portfoliolots_options')
    after = ('Shares', '0011_trade_constraints')

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate([self.before])
        self.addCleanup(self.restore_schema)
        self.old_apps = executor.loader.project_state([self.before]).apps
        self.legacy_model = self.old_apps.get_model('Shares', 'PortfolioLots')
        # Model a deployment where the deprecated table was already dropped.
        if self.legacy_model._meta.db_table in connection.introspection.table_names():
            with connection.schema_editor() as editor:
                editor.delete_model(self.legacy_model)

        user = self.old_apps.get_model('Users', 'CustomUser').objects.create(email='migrate@example.test', name='Migrate Example')
        company = self.old_apps.get_model('Shares', 'ListedCompanies').objects.create(name='Migration Ltd', abbreviation='MIG')
        old_holdings = self.old_apps.get_model('Shares', 'Portfolios').objects
        self.keeper = old_holdings.create(user_id=user, company_id=company, number_of_shares=10, total_cost=100.10)
        self.duplicate = old_holdings.create(user_id=user, company_id=company, number_of_shares=5, total_cost=54.40)
        self.legacy_entry = self.old_apps.get_model('Shares', 'Transactions').objects.create(
            user_id=user, company_id=company, transaction_type='buy', number_of_shares=10, transacted_price=100.10,
        )

    def restore_schema(self):
        MigrationExecutor(connection).migrate([self.after])

    def assert_opening_balances(self):
        self.restore_schema()
        holding = Portfolios.objects.get(pk=self.keeper.pk)
        self.assertFalse(Portfolios.objects.filter(pk=self.duplicate.pk).exists())
        self.assertEqual(holding.number_of_shares, 15)
        self.assertEqual(holding.opening_number_of_shares, 15)
        self.assertEqual(holding.total_cost, Decimal('154.50'))
        self.assertEqual(holding.opening_total_cost, Decimal('154.50'))
        self.assertTrue(holding.ledger_initialized)
        entry = Transactions.objects.get(pk=self.legacy_entry.pk)
        self.assertTrue(entry.is_legacy)
        self.assertEqual(entry.transacted_price, 100.10)
        self.assertIsNone(entry.unit_price)

    def test_migrates_duplicates_when_old_lots_table_is_absent(self):
        self.assert_opening_balances()

    def test_migrates_duplicates_when_old_lots_reference_removed_holding(self):
        with connection.schema_editor() as editor:
            editor.create_model(self.legacy_model)
        lot = self.legacy_model.objects.create(portfolio_id=self.duplicate, number_of_shares=5, total_cost=54.40)
        self.assert_opening_balances()
        self.assertTrue(self.legacy_model.objects.filter(pk=lot.pk).exists())
