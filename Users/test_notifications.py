from unittest.mock import patch

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from Shares.models import ListedCompanies, Transactions
from Users.models import Notification, Targets


class NotificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.member = users.create_user(email='notifications@example.test', name='Member')
        cls.other = users.create_user(email='other-notifications@example.test', name='Other Member')
        cls.staff = users.create_user(email='staff-notifications@example.test', name='Staff', is_staff=True)
        cls.company = ListedCompanies.objects.create(name='Notification Bank', abbreviation='NBNK')

    def setUp(self):
        self.feed_url = reverse('notification-feed')
        self.read_url = reverse('notification-read')

    def notification(self, user, key, *, read=False):
        return Notification.objects.create(
            user=user, event_key=key, title=f'Update {key}', detail=f'Details for {key}',
            read_at=timezone.now() if read else None,
        )

    def read_through(self, notification_id):
        return self.client.post(
            self.read_url, {'through_id': notification_id}, content_type='application/json',
        )

    def test_notifications_page_uses_workspace_access_rules(self):
        page_url = reverse('notifications')
        self.assertRedirects(
            self.client.get(page_url), f"{reverse('login')}?next={page_url}", fetch_redirect_response=False,
        )
        self.client.force_login(self.staff)
        self.assertRedirects(self.client.get(page_url), reverse('admin-index'), fetch_redirect_response=False)

    def test_notifications_page_keeps_sidebar_and_renders_history_in_main_content(self):
        self.client.force_login(self.member)
        page_url = reverse('notifications')
        response = self.client.get(page_url)

        self.assertEqual(response.status_code, 200)
        document = BeautifulSoup(response.content, 'html.parser')
        self.assertIsNotNone(document.select_one(
            f'#workspace-sidebar a.notification-bell[href="{page_url}"][aria-current="page"]',
        ))
        self.assertIsNone(document.select_one('#workspace-sidebar #notification-panel'))
        panel = document.select_one('main#workspace-content #notification-panel')
        self.assertIsNotNone(panel)
        self.assertEqual(panel.h1.get_text(strip=True), 'Notifications')
        self.assertIsNotNone(panel.select_one('.notification-list'))

    def test_notification_endpoints_require_sign_in_and_read_requires_csrf(self):
        self.assertEqual(self.client.get(self.feed_url).status_code, 401)
        self.assertEqual(self.read_through(1).status_code, 401)

        notification = self.notification(self.member, 'trade:csrf')
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        self.assertEqual(client.get(self.feed_url).status_code, 200)
        self.assertEqual(client.post(
            self.read_url, {'through_id': notification.pk}, content_type='application/json',
        ).status_code, 403)
        notification.refresh_from_db()
        self.assertIsNone(notification.read_at)

    def test_feed_is_private_and_lists_latest_twenty_with_full_unread_count(self):
        oldest = self.notification(self.member, 'trade:old')
        self.notification(self.other, 'trade:private')
        entries = [self.notification(self.member, f'trade:{index}') for index in range(21)]
        newest = self.notification(self.member, 'trade:read', read=True)
        self.client.force_login(self.member)

        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response.headers['Cache-Control'])
        payload = response.json()
        self.assertEqual(payload['unread_count'], 22)
        self.assertEqual(
            [item['id'] for item in payload['items']],
            [newest.pk] + [entry.pk for entry in reversed(entries[-19:])],
        )
        self.assertEqual(payload['items'][0]['title'], newest.title)
        self.assertEqual(payload['items'][0]['detail'], newest.detail)
        self.assertTrue(payload['items'][0]['created_at'])
        self.assertFalse(payload['items'][0]['unread'])
        self.assertTrue(payload['items'][1]['unread'])
        self.assertEqual(payload['next_before'], entries[2].pk)

        older = self.client.get(self.feed_url, {'before': payload['next_before']}).json()
        self.assertEqual([item['id'] for item in older['items']], [entries[1].pk, entries[0].pk, oldest.pk])
        self.assertEqual(older['unread_count'], 22)
        self.assertIsNone(older['next_before'])

        empty = self.client.get(self.feed_url, {'before': oldest.pk}).json()
        self.assertEqual(empty, {'items': [], 'unread_count': 22, 'next_before': None})
        oldest.refresh_from_db()
        self.assertIsNone(oldest.read_at)

    def test_feed_rejects_invalid_cursors(self):
        self.client.force_login(self.member)
        for cursor in ('', '0', '-1', '1.5', '123x', '９', str(2**63), '9' * 100):
            with self.subTest(cursor=cursor):
                response = self.client.get(self.feed_url, {'before': cursor})
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json())

    def test_read_through_marks_only_the_current_members_seen_updates(self):
        first = self.notification(self.member, 'trade:first')
        other = self.notification(self.other, 'trade:other')
        through = self.notification(self.member, 'trade:through')
        newer = self.notification(self.member, 'trade:newer')
        self.client.force_login(self.member)

        self.assertEqual(self.read_through(other.pk).status_code, 404)
        self.assertEqual(self.read_through(True).status_code, 400)
        for _ in range(2):
            response = self.read_through(through.pk)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['unread_count'], 1)

        for notification in (first, other, through, newer):
            notification.refresh_from_db()
        self.assertIsNotNone(first.read_at)
        self.assertIsNotNone(through.read_at)
        self.assertIsNone(other.read_at)
        self.assertIsNone(newer.read_at)
        self.assertEqual(self.client.get(self.feed_url).json()['unread_count'], 1)

    def test_trade_receipt_is_created_once_and_only_for_successful_trades(self):
        self.client.force_login(self.member)
        trades_url = reverse('trades')
        buy = {
            'company': self.company.pk,
            'transaction_type': 'buy',
            'quantity': 10,
            'unit_price': '100.00',
            'purchase_type': 'ipo',
            'transaction_date': timezone.localdate().isoformat(),
            'idempotency_key': 'notification-trade',
        }

        for _ in range(2):
            self.assertEqual(self.client.post(trades_url, buy).status_code, 302)
        entry = Transactions.objects.get(user_id=self.member)
        receipt = Notification.objects.get(
            user=self.member, event_key=f'trade:{entry.pk}', read_at__isnull=True,
        )
        self.assertEqual(receipt.title, 'Purchase recorded')
        self.assertIn('10 shares of Notification Bank (NBNK)', receipt.detail)
        self.assertIn('Total cost Rs. 1,000.00', receipt.detail)

        invalid_sale = {**buy, 'transaction_type': 'sell', 'quantity': 11, 'idempotency_key': 'invalid-sale'}
        self.assertEqual(self.client.post(trades_url, invalid_sale).status_code, 400)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Transactions.objects.filter(user_id=self.member).count(), 1)

    @patch('Users.views._target_market_prices')
    def test_wishlist_notifies_once_per_observed_matching_target_range(self, quotes):
        target = Targets.objects.create(
            user_id=self.member, company_id=self.company, target_type='buy', low_target=100, high_target=150,
        )
        Targets.objects.create(
            user_id=self.other, company_id=self.company, target_type='buy', low_target=100, high_target=150,
        )
        Targets.objects.create(
            user_id=self.member, company_id=self.company, target_type='sell', low_target=100, high_target=150,
            is_deleted=True,
        )
        self.client.force_login(self.member)
        wishlist = reverse('wishlist')

        for prices in ({}, {self.company.abbreviation: 90}):
            quotes.return_value = prices
            self.assertEqual(self.client.get(wishlist).status_code, 200)
            self.assertFalse(Notification.objects.exists())

        quotes.return_value = {self.company.abbreviation: 125}
        for _ in range(2):
            self.assertEqual(self.client.get(wishlist).status_code, 200)
        alerts = Notification.objects.filter(user=self.member, event_key__startswith='target:')
        alert = alerts.get()
        self.assertEqual(alert.title, 'Buy target in range')
        self.assertIn('NBNK', alert.detail)
        self.assertIn('Rs. 125.00', alert.detail)
        self.assertFalse(Notification.objects.filter(user=self.other).exists())

        response = self.client.post(reverse('edit-target'), {
            'target_id': target.pk, 'company_abbr': self.company.abbreviation,
            'edit_low_target': '120', 'edit_high_target': '160',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get(wishlist).status_code, 200)
        self.assertEqual(alerts.count(), 2)
