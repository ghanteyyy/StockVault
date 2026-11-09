'''
Reporting tests run against the isolated Admin.test_settings database
'''

import csv
from datetime import timedelta
from io import StringIO
from unittest.mock import patch
from urllib.parse import parse_qs

from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import ProgrammingError, connection
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils import timezone

from Shares.models import ListedCompanies, Portfolios, Transactions, WishLists
from Users.models import Targets
from . import operations_views as views


class AdminOperationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.staff = user_model.objects.create(email='admin@example.com', name='Admin Person', is_staff=True, password='!')
        cls.alice = user_model.objects.create(email='alice@example.com', name='Alice Member', password='!')
        cls.bob = user_model.objects.create(email='bob@example.com', name='Bob Member', is_active=False, password='!')
        cls.bank = ListedCompanies.objects.create(name='Alpine Bank', abbreviation='ALP', sector='Commercial Banks')
        cls.hydro = ListedCompanies.objects.create(name='River Hydro', abbreviation='RIV', sector='Hydro Power')
        cls.unclassified = ListedCompanies.objects.create(name='Unclassified Company', abbreviation='UNC', sector='')
        cls.holding_a = Portfolios.objects.create(user_id=cls.alice, company_id=cls.bank, number_of_shares=100, total_cost=25000)
        cls.holding_b = Portfolios.objects.create(user_id=cls.bob, company_id=cls.hydro, number_of_shares=50, total_cost=15000)
        cls.empty = Portfolios.objects.create(user_id=cls.alice, company_id=cls.unclassified, number_of_shares=0, total_cost=55)

        today = timezone.localdate()

        cls.buy = Transactions.objects.create(user_id=cls.alice, company_id=cls.bank, number_of_shares=20, transacted_price=5000, transaction_type='BUY', transaction_date=today, is_legacy=True)
        cls.sell = Transactions.objects.create(user_id=cls.bob, company_id=cls.hydro, number_of_shares=10, transacted_price=3200, transaction_type='sell', transaction_date=today - timedelta(days=35), is_legacy=True)
        cls.target = Targets.objects.create(user_id=cls.alice, company_id=cls.bank, target_type='buy', low_target=100, high_target=120)
        cls.invalid_target = Targets.objects.create(user_id=cls.alice, company_id=cls.hydro, target_type='sell', low_target=80, high_target=60)
        cls.removed_target = Targets.objects.create(user_id=cls.bob, company_id=cls.hydro, target_type='buy', low_target=50, high_target=70, is_deleted=True)
        cls.wishlist_a = WishLists.objects.create(user_id=cls.alice, company_id=cls.bank)
        cls.wishlist_b = WishLists.objects.create(user_id=cls.bob, company_id=cls.hydro)
        content_type = ContentType.objects.get_for_model(ListedCompanies)
        cls.add_log = LogEntry.objects.create(user=cls.staff, content_type=content_type, object_id=cls.bank.pk,
            object_repr=cls.bank.name, action_flag=ADDITION, change_message='Added company')
        cls.change_log = LogEntry.objects.create(user=cls.staff, content_type=content_type, object_id=cls.hydro.pk,
            object_repr=cls.hydro.name, action_flag=CHANGE, change_message='Corrected sector')

    def setUp(self):
        self.factory = RequestFactory()

    def request(self, params=None, user=None):
        request = self.factory.get('/admin/report', params or {})
        request.user = self.staff if user is None else user

        return request

    def context(self, view, params=None):
        with patch('Admin.operations_views.render', return_value=HttpResponse('report')) as render:
            response = view(self.request(params))

        self.assertEqual(response.status_code, 200)

        return render.call_args.args[2]

    def ids(self, context):
        return {row.pk for row in context['page_obj'].object_list}

    def csv_rows(self, view, params=None):
        response = view(self.request({'export': 'csv', **(params or {})}))

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('no-store', response['Cache-Control'])
        self.assertIn('private', response['Cache-Control'])

        return list(csv.reader(StringIO(response.content.decode('utf-8-sig'))))

    def test_all_report_views_require_active_staff(self):
        reports = [views.AdminOverview, views.AdminActivity, views.AdminPortfolios,
            views.AdminTransactions, views.AdminTargets, views.AdminWishlists]

        inactive_staff = get_user_model()(email='inactive@example.com', is_staff=True, is_active=False)

        for view in reports:
            with self.subTest(view=view.__name__, access='anonymous'):
                self.assertEqual(view(self.request(user=AnonymousUser())).status_code, 302)

            for user in (self.alice, self.bob, inactive_staff):
                with self.subTest(view=view.__name__, access=user.email), self.assertRaises(PermissionDenied):
                    view(self.request(user=user))

    def test_holdings_default_includes_accounts_and_empty_filter_is_real(self):
        context = self.context(views.AdminPortfolios)

        self.assertEqual(self.ids(context), {self.holding_a.pk, self.holding_b.pk, self.empty.pk})
        self.assertEqual(self.ids(self.context(views.AdminPortfolios, {'status': 'empty'})), {self.empty.pk})
        self.assertEqual(self.ids(self.context(views.AdminPortfolios, {'status': 'positive'})), {self.holding_a.pk, self.holding_b.pk})
        self.assertEqual(context['metrics'][2]['value'], 40055)

    def test_search_and_owner_company_filters_compose(self):
        params = {'q': 'alp', 'user': 'ALICE@EXAMPLE.COM', 'company': self.bank.pk}

        self.assertEqual(self.ids(self.context(views.AdminPortfolios, params)), {self.holding_a.pk})
        self.assertEqual(self.ids(self.context(views.AdminPortfolios, {'q': 'Bob'})), {self.holding_b.pk})
        self.assertEqual(self.ids(self.context(views.AdminPortfolios, {'user': 'missing@example.com'})), set())

    def test_related_record_data_is_loaded_without_row_queries(self):
        for view in (views.AdminPortfolios, views.AdminTransactions, views.AdminTargets, views.AdminWishlists):
            context = self.context(view)

            with self.subTest(view=view.__name__), self.assertNumQueries(1):
                rows = list(context['page_obj'].object_list)
                [(row.user_id.email, row.company_id.name) for row in rows]

    def test_transaction_type_filter_handles_legacy_case_and_date_bounds(self):
        self.assertEqual(self.ids(self.context(views.AdminTransactions, {'type': 'buy'})), {self.buy.pk})
        start = (timezone.localdate() - timedelta(days=5)).isoformat()
        context = self.context(views.AdminTransactions, {'date_from': start})

        self.assertEqual(self.ids(context), {self.buy.pk})
        self.assertEqual(context['metrics'][1]['value'], 1)
        self.assertEqual(context['metrics'][2]['value'], 0)

    def test_malformed_and_inverted_dates_report_errors_without_crashing(self):
        context = self.context(views.AdminTransactions, {'date_from': '2026-99-99'})

        self.assertIn('date_from', context['filter_errors'])
        self.assertEqual(len(self.ids(context)), 2)

        context = self.context(views.AdminTransactions, {'date_from': '2026-02-10', 'date_to': '2026-02-01'})
        self.assertIn('date_to', context['filter_errors'])
        self.assertEqual(len(self.ids(context)), 2)

    def test_target_state_defaults_hide_removed_records(self):
        self.assertEqual(self.ids(self.context(views.AdminTargets)), {self.target.pk, self.invalid_target.pk})
        self.assertEqual(self.ids(self.context(views.AdminTargets, {'state': 'removed'})), {self.removed_target.pk})
        self.assertEqual(self.ids(self.context(views.AdminTargets, {'state': 'invalid'})), {self.invalid_target.pk})
        self.assertEqual(len(self.ids(self.context(views.AdminTargets, {'state': 'all'}))), 3)

    def test_wishlists_filter_sector_and_use_honest_non_date_sort(self):
        context = self.context(views.AdminWishlists, {'sector': 'Hydro Power'})

        self.assertEqual(self.ids(context), {self.wishlist_b.pk})
        self.assertEqual(context['filters']['sort'], 'company')
        self.assertNotIn('newest', dict(context['sort_options']))

    def test_invalid_sort_cannot_become_a_database_order_expression(self):
        context = self.context(views.AdminPortfolios, {'sort': 'user_id__password'})

        self.assertEqual(context['filters']['sort'], 'newest')
        self.assertEqual(len(self.ids(context)), 3)

    def test_pagination_preserves_filters_and_exports_all_filtered_rows(self):
        companies = ListedCompanies.objects.bulk_create([
            ListedCompanies(name=f'Alpine listing {index}', abbreviation=f'ALP{index}') for index in range(23)
        ])
        Portfolios.objects.bulk_create([
            Portfolios(user_id=self.alice, company_id=company, number_of_shares=1, total_cost=10)
            for company in companies
        ])

        context = self.context(views.AdminPortfolios, {'q': 'ALP', 'page': '2', 'per_page': '20'})

        self.assertEqual(context['page_obj'].number, 2)
        self.assertEqual(len(context['page_obj'].object_list), 4)
        self.assertIn('q=ALP', context['query_string'])
        self.assertNotIn('page', parse_qs(context['query_string']))

        rows = self.csv_rows(views.AdminPortfolios, {'q': 'ALP', 'page': '2'})
        self.assertEqual(len(rows), 25)

    def test_csv_has_safe_text_and_correct_filtered_values(self):
        self.bank.name = '=HYPERLINK("bad")'
        self.bank.save(update_fields=['name'])

        rows = self.csv_rows(views.AdminPortfolios, {'company': self.bank.pk})
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], self.alice.email)
        self.assertEqual(rows[1][4], '\'=HYPERLINK("bad")')
        self.assertEqual(rows[1][6], '100')
        self.assertEqual(rows[1][7], '25000.00')

    def test_each_record_export_uses_the_filtered_queryset(self):
        cases = [(views.AdminTransactions, {'type': 'sell'}), (views.AdminTargets, {'state': 'removed'}),
            (views.AdminWishlists, {'sector': 'Hydro Power'})]

        for view, params in cases:
            with self.subTest(view=view.__name__):
                self.assertEqual(len(self.csv_rows(view, params)), 2)

    def test_activity_search_action_and_export_use_audit_records(self):
        context = self.context(views.AdminActivity, {'action': 'change'})

        self.assertEqual(self.ids(context), {self.change_log.pk})
        self.assertEqual(self.ids(self.context(views.AdminActivity, {'q': 'Alpine'})), {self.add_log.pk})

        rows = self.csv_rows(views.AdminActivity, {'q': 'Corrected'})
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][2], 'Change')
        self.assertEqual(rows[1][-1], 'Corrected sector')

    def test_overview_uses_real_counts_costs_and_actionable_quality_signals(self):
        context = self.context(views.AdminOverview)
        totals = context['totals']

        self.assertEqual(totals['users'], 3)
        self.assertEqual(totals['active_users'], 2)
        self.assertEqual(totals['admin_users'], 1)
        self.assertEqual(totals['companies'], 3)
        self.assertEqual(totals['positive_holdings'], 2)
        self.assertEqual(totals['recorded_capital'], 40000)
        self.assertEqual(totals['transactions_30d'], 1)
        self.assertEqual(totals['active_targets'], 2)
        self.assertEqual(totals['wishlist_entries'], 2)
        self.assertEqual(len(context['metrics']), 4)
        self.assertEqual(len(context['daily_signups']), 7)
        self.assertEqual(sum(day['count'] for day in context['daily_signups']), 3)
        self.assertEqual(sum(row['percentage'] for row in context['sector_breakdown']), 100)
        self.assertEqual([signal['value'] for signal in context['quality_signals']], [1, 1, 1])
        self.assertIn('sector=__missing__', context['quality_signals'][0]['url'])
        self.assertIn('state=invalid', context['quality_signals'][2]['url'])

    def test_reports_do_not_change_financial_records(self):
        original = (Portfolios.objects.count(), Transactions.objects.count(), Targets.objects.count(), WishLists.objects.count())

        for view in (views.AdminPortfolios, views.AdminTransactions, views.AdminTargets, views.AdminWishlists, views.AdminOverview):
            self.context(view)

        after = (Portfolios.objects.count(), Transactions.objects.count(), Targets.objects.count(), WishLists.objects.count())
        self.assertEqual(after, original)

    def test_overview_renders_without_a_purchase_lots_table(self):
        self.client.force_login(self.staff)

        def reject_removed_table(execute, sql, params, many, context):
            if 'shares_portfoliolots' in sql.casefold():
                raise ProgrammingError('relation "Shares_portfoliolots" does not exist')

            return execute(sql, params, many, context)

        with connection.execute_wrapper(reject_removed_table):
            response = self.client.get(reverse('admin-index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/dashboard.html')
        self.assertContains(response, 'Platform overview.')
        self.assertContains(response, 'Holdings by sector')
        self.assertContains(response, 'Recent management activity')
        self.assertContains(response, self.alice.email)
        self.assertNotContains(response, 'Purchase lots')
        self.assertNotContains(response, 'portfolioLots')

    def test_purchase_lot_admin_routes_are_not_available(self):
        for name in ('admin-portfolioLots', 'admin-lots'):
            with self.subTest(name=name), self.assertRaises(NoReverseMatch):
                reverse(name)
        for path in ('/admin/portfolioLots', '/admin/purchase-lots'):
            with self.subTest(path=path), self.assertRaises(Resolver404):
                resolve(path)
