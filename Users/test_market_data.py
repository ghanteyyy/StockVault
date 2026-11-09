from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from Users.market_views import CACHE_KEY, LAST_GOOD_KEY


NEPSE_RESPONSE = {
    'index': [
        {'id': 57, 'index': 'Sensitive Index', 'currentValue': 503.25},
        {'id': 58, 'index': 'NEPSE Index', 'currentValue': 2635.40, 'change': -12.20,
         'perChange': -0.46, 'generatedTime': '2026-11-08T15:00:00'},
    ],
    'summary': [
        {'detail': 'Total Turnover Rs:', 'value': 1234567.89},
        {'detail': 'Total Traded Shares', 'value': 150000},
        {'detail': 'Total Transactions', 'value': 4200},
    ],
    'gainers': [{'symbol': 'RISE', 'securityName': 'Rising Company', 'ltp': 210.50,
                 'pointChange': 10.50, 'percentageChange': 5.25}],
    'losers': [{'symbol': 'FALL', 'securityName': 'Falling Company', 'ltp': 194.60,
                'pointChange': -5.40, 'percentageChange': -2.70}],
}


class MarketDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.member = users.create_user(email='market-member@example.test', name='Market Member')
        cls.staff = users.create_user(email='market-staff@example.test', name='Market Staff', is_staff=True)

    def setUp(self):
        self.url = reverse('market-data')
        cache.delete_many([CACHE_KEY, LAST_GOOD_KEY])
        self.addCleanup(cache.delete_many, [CACHE_KEY, LAST_GOOD_KEY])

    @patch('Users.market_views._fetch_sections')
    def test_market_data_uses_workspace_access_rules(self, fetch):
        self.assertRedirects(self.client.get(self.url), f"{reverse('login')}?next={self.url}", fetch_redirect_response=False)
        self.client.force_login(self.staff)
        self.assertRedirects(self.client.get(self.url), reverse('admin-index'), fetch_redirect_response=False)
        fetch.assert_not_called()

    @patch('Users.market_views._fetch_sections', return_value=NEPSE_RESPONSE)
    def test_market_snapshot_renders_main_index_and_movers_and_is_cached(self, fetch):
        self.client.force_login(self.member)
        response = self.client.get(self.url)
        self.assertContains(response, 'Market Data')
        self.assertContains(response, '2,635.40')
        self.assertContains(response, '12,34,567.89')
        self.assertContains(response, 'RISE')
        self.assertContains(response, 'FALL')
        self.assertEqual(response.context['index']['value'], Decimal('2635.40'))
        self.assertEqual(response.context['losers'][0]['percent'], Decimal('-2.70'))
        self.assertFalse(response.context['stale'])

        self.assertEqual(self.client.get(self.url).status_code, 200)
        fetch.assert_called_once()

    @patch('Users.market_views._fetch_sections', return_value=NEPSE_RESPONSE)
    def test_failed_section_can_show_the_last_available_snapshot(self, fetch):
        self.client.force_login(self.member)
        self.client.get(self.url)
        cache.delete(CACHE_KEY)
        fetch.return_value = {'index': [
            {'id': 58, 'index': 'NEPSE Index', 'currentValue': 2640, 'change': 4.60, 'perChange': 0.17},
        ], 'losers': []}

        response = self.client.get(self.url)
        self.assertTrue(response.context['stale'])
        self.assertEqual(response.context['index']['value'], Decimal('2640'))
        self.assertContains(response, 'RISE')
        self.assertEqual(response.context['losers'], [])

    @patch('Users.market_views._fetch_sections', return_value={})
    def test_market_page_is_available_when_the_exchange_feed_is_down(self, fetch):
        self.client.force_login(self.member)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['unavailable'])
        self.assertIsNone(response.context['index'])
