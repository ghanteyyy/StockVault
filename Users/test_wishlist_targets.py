import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Shares.models import ListedCompanies, WishLists
from Users.models import Targets


class WishlistTargetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.member = users.create_user(email='wishlist-member@example.test', name='Wishlist Member')
        cls.other = users.create_user(email='wishlist-other@example.test', name='Other Member')
        cls.saved_company = ListedCompanies.objects.create(name='Saved Hydropower', abbreviation='SAVED')
        cls.target_company = ListedCompanies.objects.create(name='Target Bank', abbreviation='TARGET')
        cls.saved_item = WishLists.objects.create(user_id=cls.member, company_id=cls.saved_company)
        cls.target = Targets.objects.create(
            user_id=cls.member, company_id=cls.target_company, target_type='buy', low_target=100, high_target=150,
        )
        cls.other_target = Targets.objects.create(
            user_id=cls.other, company_id=cls.target_company, target_type='sell', low_target=200, high_target=250,
        )

    def setUp(self):
        self.wishlist = reverse('wishlist')
        self.create_target = reverse('create-target')
        self.edit_target = reverse('edit-target')
        self.delete_target = reverse('delete-target', args=[self.target_company.pk])
        self.target_values = {
            'company': self.target_company.name,
            'target_type': 'buy',
            'low_target': '100',
            'high_target': '150',
        }
        quotes = patch('Users.views._target_market_prices', return_value={self.target_company.abbreviation: 125})
        quotes.start()
        self.addCleanup(quotes.stop)

    def test_wishlist_and_target_routes_require_sign_in(self):
        for url in [self.wishlist, reverse('target')]:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}",
                                     fetch_redirect_response=False)
        for url in [self.create_target, self.edit_target, self.delete_target]:
            with self.subTest(url=url):
                self.assertRedirects(self.client.post(url), f"{reverse('login')}?next={url}",
                                     fetch_redirect_response=False)

    def test_old_target_page_opens_the_existing_targets_in_wishlist(self):
        self.client.force_login(self.member)
        self.assertRedirects(self.client.get(reverse('target')), f'{self.wishlist}#price-targets')

        response = self.client.get(self.wishlist)
        self.assertTemplateUsed(response, 'users/wishlist.html')
        self.assertContains(response, 'id="price-targets"', count=1)
        self.assertContains(response, f'data-target-id="{self.target.pk}"')
        self.assertNotContains(response, self.other_target.pk)
        self.assertNotContains(response, f'href="{reverse("target")}"')
        element_ids = re.findall(rb'\sid="([^"]+)"', response.content)
        self.assertCountEqual(element_ids, set(element_ids))
        self.assertEqual([item['id'] for item in response.context['saved_companies']], [self.saved_item.pk])
        self.assertEqual([target['id'] for target in response.context['targets']], [self.target.pk])
        self.assertTrue(response.context['targets'][0]['show_buy_sell'])

    def test_target_create_edit_and_delete_return_to_the_wishlist_section(self):
        self.client.force_login(self.member)
        response = self.client.post(self.create_target, {**self.target_values, 'target_type': 'sell'})
        self.assertRedirects(response, f'{self.wishlist}?target_notice=created#price-targets')
        created = Targets.objects.get(user_id=self.member, company_id=self.target_company, target_type='sell')

        response = self.client.post(self.edit_target, {
            'target_id': created.pk, 'company_abbr': self.target_company.abbreviation,
            'edit_low_target': '140', 'edit_high_target': '175',
        })
        self.assertRedirects(response, f'{self.wishlist}?target_notice=updated#price-targets')
        created.refresh_from_db()
        self.assertEqual((created.low_target, created.high_target), (140, 175))

        response = self.client.post(self.delete_target, {'target_id': created.pk})
        self.assertRedirects(response, f'{self.wishlist}?target_notice=deleted#price-targets')
        created.refresh_from_db()
        self.assertTrue(created.is_deleted)
        self.assertEqual([target['id'] for target in self.client.get(self.wishlist).context['targets']],
                         [self.target.pk])

    def test_invalid_and_duplicate_targets_show_errors_in_the_wishlist(self):
        self.client.force_login(self.member)
        for values, error in [
            (self.target_values, 'A buy target for Target Bank already exists.'),
            ({**self.target_values, 'low_target': '250'}, 'Low target must be less than high target.'),
        ]:
            with self.subTest(values=values):
                response = self.client.post(self.create_target, values)
                self.assertTemplateUsed(response, 'users/wishlist.html')
                self.assertContains(response, 'id="price-targets"')
                self.assertContains(response, error)
                self.assertTrue(response.context['focus_targets'])
                self.assertEqual(response.context['target_form']['low_target'], values['low_target'])
        self.assertEqual(Targets.objects.filter(user_id=self.member).count(), 1)

    def test_target_mutations_are_scoped_to_the_signed_in_member(self):
        self.client.force_login(self.member)
        edit_values = {
            'target_id': self.other_target.pk, 'company_abbr': self.target_company.abbreviation,
            'edit_low_target': '160', 'edit_high_target': '175',
        }
        for url, values in [(self.edit_target, edit_values), (self.delete_target, {'target_id': self.other_target.pk})]:
            with self.subTest(url=url):
                response = self.client.post(url, values)
                self.assertTemplateUsed(response, 'users/wishlist.html')
                self.assertContains(response, 'This target could not be found.')
                self.assertTrue(response.context['focus_targets'])

        self.other_target.refresh_from_db()
        self.assertEqual((self.other_target.low_target, self.other_target.high_target), (200, 250))
        self.assertFalse(self.other_target.is_deleted)

    def test_saving_and_removing_a_wishlist_company_preserves_its_targets(self):
        self.client.force_login(self.member)
        response = self.client.post(self.wishlist, {'action': 'add', 'company': self.target_company.name})
        self.assertRedirects(response, f'{self.wishlist}?notice=added')
        saved = WishLists.objects.get(user_id=self.member, company_id=self.target_company)

        response = self.client.post(self.wishlist, {'action': 'delete', 'wishlist_id': saved.pk})
        self.assertRedirects(response, f'{self.wishlist}?notice=removed')
        self.assertFalse(WishLists.objects.filter(pk=saved.pk).exists())
        self.assertTrue(Targets.objects.filter(pk=self.target.pk, is_deleted=False).exists())
