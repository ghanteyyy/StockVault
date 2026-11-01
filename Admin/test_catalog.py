'''
Catalogue and question-library behavior, exercised only in the test database
'''

import csv
from io import StringIO
from urllib.parse import parse_qs
from unittest.mock import patch

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.test import Client, TestCase
from django.urls import reverse

from Shares.models import FAQs, ListedCompanies, Portfolios, Transactions, WishLists
from Users.models import CustomUser, Targets


class CatalogManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = CustomUser.objects.create_user('catalog-admin@example.com', 'ExamplePassword1!', name='Catalogue Admin', is_staff=True)
        cls.member = CustomUser.objects.create_user('catalog-member@example.com', 'ExamplePassword1!', name='Member')
        cls.company = ListedCompanies.objects.create(name='Nabil Bank Limited', abbreviation='NABIL', sector='Commercial Banks')
        cls.faq = FAQs.objects.create(question='How do I add a holding?', answer='Choose a company and enter the purchase details.')

    def setUp(self):
        self.client.force_login(self.staff)

    def post(self, name, data=None):
        return self.client.post(reverse(name), data or {}, HTTP_ACCEPT='application/json')

    def company_values(self, **overrides):
        return {'company_name': 'Example Hydro Limited', 'company_abbreviation': 'EXHYD', 'company_sector': 'Hydro Power', **overrides}

    def faq_values(self, **overrides):
        return {'faq_question': 'Where can I review targets?', 'faq_answer': 'Open the price targets page.', **overrides}

    def test_non_staff_cannot_read_or_change_catalogue(self):
        endpoints = ['admin-companies', 'admin-faqs']

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                self.client.logout()
                self.assertEqual(self.client.get(reverse(endpoint)).status_code, 302)
                self.client.force_login(self.member)
                self.assertEqual(self.client.get(reverse(endpoint)).status_code, 403)

        for endpoint in ['admin-company-add', 'admin-company-edit', 'admin-company-delete', 'admin-faq-add', 'admin-faq-edit', 'admin-faq-delete']:
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.post(endpoint).status_code, 403)

        self.assertEqual(ListedCompanies.objects.count(), 1)
        self.assertEqual(FAQs.objects.count(), 1)

    def test_mutations_reject_get_and_preserve_records(self):
        for endpoint in ['admin-company-add', 'admin-company-edit', 'admin-company-delete', 'admin-faq-add', 'admin-faq-edit', 'admin-faq-delete']:
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.client.get(reverse(endpoint), {'company_id': self.company.pk, 'faq_id': self.faq.pk}).status_code, 405)

        self.assertTrue(ListedCompanies.objects.filter(pk=self.company.pk).exists())
        self.assertTrue(FAQs.objects.filter(pk=self.faq.pk).exists())

    def test_mutations_enforce_csrf(self):
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.staff)

        self.assertEqual(protected.post(reverse('admin-company-add'), self.company_values()).status_code, 403)
        self.assertEqual(protected.post(reverse('admin-faq-add'), self.faq_values()).status_code, 403)

    def test_company_creation_normalizes_and_is_audited(self):
        response = self.post('admin-company-add', self.company_values(company_name='  Example Hydro Limited  ', company_abbreviation=' exhyd '))
        self.assertEqual(response.status_code, 200)

        company = ListedCompanies.objects.get(abbreviation='EXHYD')
        self.assertEqual(company.name, 'Example Hydro Limited')

        event = LogEntry.objects.get(object_id=company.pk)
        self.assertEqual(event.action_flag, ADDITION)
        self.assertEqual(event.user_id, self.staff.pk)

    def test_company_required_and_length_errors_are_field_specific(self):
        response = self.post('admin-company-add', self.company_values(company_name=' ', company_abbreviation='X' * 256, company_sector=''))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()['errors']), {'company_name', 'company_abbreviation', 'company_sector'})
        self.assertEqual(ListedCompanies.objects.count(), 1)
        self.assertFalse(LogEntry.objects.exists())

    def test_case_insensitive_name_and_symbol_duplicates_are_rejected(self):
        for values, field in [(self.company_values(company_name='nabil bank limited'), 'company_name'),
                              (self.company_values(company_abbreviation='nabil'), 'company_abbreviation')]:

            with self.subTest(field=field):
                response = self.post('admin-company-add', values)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json()['errors'])

    def test_company_edit_preserves_identity_and_linked_holdings(self):
        portfolio = Portfolios.objects.create(user_id=self.member, company_id=self.company, number_of_shares=12, total_cost=5000)
        response = self.post('admin-company-edit', self.company_values(company_id=self.company.pk, company_name='Nabil Bank', company_abbreviation='NABIL', company_sector='Banks'))
        self.assertEqual(response.status_code, 200)

        self.company.refresh_from_db()
        portfolio.refresh_from_db()

        self.assertEqual(self.company.name, 'Nabil Bank')
        self.assertEqual(portfolio.company_id_id, self.company.pk)
        self.assertEqual(portfolio.number_of_shares, 12)
        self.assertEqual(LogEntry.objects.get(object_id=self.company.pk).action_flag, CHANGE)

    def test_conflicting_company_edit_is_not_saved(self):
        second = ListedCompanies.objects.create(name='Another Company', abbreviation='OTHER', sector='Other')
        response = self.post('admin-company-edit', self.company_values(company_id=second.pk, company_abbreviation='nabil'))
        self.assertEqual(response.status_code, 400)

        second.refresh_from_db()
        self.assertEqual(second.abbreviation, 'OTHER')
        self.assertFalse(LogEntry.objects.exists())

    def test_deleting_a_company_rejects_each_type_of_link(self):
        factories = [
            lambda company: Portfolios.objects.create(user_id=self.member, company_id=company, number_of_shares=0),
            lambda company: Transactions.objects.create(user_id=self.member, company_id=company, number_of_shares=1),
            lambda company: Targets.objects.create(user_id=self.member, company_id=company, target_type='buy', is_deleted=True),
            lambda company: WishLists.objects.create(user_id=self.member, company_id=company),
        ]

        for index, create_link in enumerate(factories):
            with self.subTest(index=index):
                company = ListedCompanies.objects.create(name=f'Linked company {index}', abbreviation=f'LINK{index}', sector='Banks')
                linked = create_link(company)
                response = self.post('admin-company-delete', {'company_id': company.pk})

                self.assertEqual(response.status_code, 409)
                self.assertTrue(ListedCompanies.objects.filter(pk=company.pk).exists())
                self.assertTrue(type(linked).objects.filter(pk=linked.pk).exists())

        self.assertFalse(LogEntry.objects.exists())

    def test_unused_company_can_be_removed_with_audit(self):
        key = self.company.pk
        response = self.post('admin-company-delete', {'company_id': key})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ListedCompanies.objects.filter(pk=key).exists())
        self.assertEqual(LogEntry.objects.get(object_id=key).action_flag, DELETION)

    def test_company_lists_filter_across_the_full_queryset(self):
        ListedCompanies.objects.bulk_create([ListedCompanies(name=f'Hydro company {index:02}', abbreviation=f'HYD{index:02}', sector='Hydro Power') for index in range(25)])
        response = self.client.get(reverse('admin-companies'), {'q': 'Hydro', 'per_page': '20', 'page': '2', 'sort': 'name'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 25)
        self.assertEqual(len(response.context['companies']), 5)
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertIn('q=Hydro', response.context['query_string'])
        self.assertNotIn('page', parse_qs(response.context['query_string']))

    def test_company_missing_sector_and_usage_filters(self):
        missing = ListedCompanies.objects.create(name='Unclassified Company', abbreviation='UNCLASS', sector='')
        Portfolios.objects.create(user_id=self.member, company_id=self.company)

        response = self.client.get(reverse('admin-companies'), {'sector': '__missing__'})
        self.assertEqual(list(response.context['companies'].object_list), [missing])

        response = self.client.get(reverse('admin-companies'), {'usage': 'in_use'})
        self.assertEqual([company.pk for company in response.context['companies']], [self.company.pk])

        response = self.client.get(reverse('admin-companies'), {'usage': 'unused'})
        self.assertEqual([company.pk for company in response.context['companies']], [missing.pk])

    def test_company_invalid_sort_and_pagination_are_safe(self):
        response = self.client.get(reverse('admin-companies'), {'sort': 'unknown__column', 'page': 'nonsense', 'per_page': '-100'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 1)
        self.assertEqual(response.context['page_obj'].paginator.per_page, 20)

    def test_company_export_respects_filters_and_neutralizes_formula_text(self):
        ListedCompanies.objects.create(name='=Formula company', abbreviation='FORMULA', sector='Other')
        response = self.client.get(reverse('admin-companies'), {'q': 'Formula', 'export': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/csv'))

        rows = list(csv.reader(StringIO(response.content.decode('utf-8-sig'))))

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][0], 'FORMULA')
        self.assertEqual(rows[1][1], "'=Formula company")

    def test_company_write_rolls_back_if_auditing_fails(self):
        with patch('Admin.catalog_views.record_admin_action', side_effect=RuntimeError('Audit unavailable')):
            with self.assertRaises(RuntimeError):
                self.post('admin-company-add', self.company_values())

        self.assertFalse(ListedCompanies.objects.filter(abbreviation='EXHYD').exists())

    def test_faq_creation_and_edit_are_audited(self):
        response = self.post('admin-faq-add', self.faq_values())
        self.assertEqual(response.status_code, 200)

        faq = FAQs.objects.get(question='Where can I review targets?')
        self.assertEqual(LogEntry.objects.get(object_id=faq.pk).action_flag, ADDITION)

        response = self.post('admin-faq-edit', self.faq_values(faq_id=faq.pk, faq_answer='Open your price targets workspace.'))
        self.assertEqual(response.status_code, 200)

        faq.refresh_from_db()
        self.assertEqual(faq.answer, 'Open your price targets workspace.')
        self.assertEqual(LogEntry.objects.filter(object_id=faq.pk).count(), 2)

    def test_faq_blank_long_and_duplicate_questions_are_rejected(self):
        response = self.post('admin-faq-add', self.faq_values(faq_question='', faq_answer='A' * 256))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()['errors']), {'faq_question', 'faq_answer'})

        response = self.post('admin-faq-add', self.faq_values(faq_question='HOW DO I ADD A HOLDING?'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('faq_question', response.json()['errors'])
        self.assertEqual(FAQs.objects.count(), 1)

    def test_faq_edit_cannot_duplicate_another_entry(self):
        other = FAQs.objects.create(question='Another question?', answer='An answer.')
        response = self.post('admin-faq-edit', self.faq_values(faq_id=other.pk, faq_question=self.faq.question.lower()))

        self.assertEqual(response.status_code, 400)
        other.refresh_from_db()

        self.assertEqual(other.question, 'Another question?')

    def test_faq_delete_is_audited(self):
        key = self.faq.pk

        self.assertEqual(self.post('admin-faq-delete', {'faq_id': key}).status_code, 200)
        self.assertFalse(FAQs.objects.filter(pk=key).exists())
        self.assertEqual(LogEntry.objects.get(object_id=key).action_flag, DELETION)

    def test_faq_filters_search_answers_and_find_incomplete_entries(self):
        missing = FAQs.objects.create(question='Needs an answer', answer='')

        response = self.client.get(reverse('admin-faqs'), {'q': 'purchase'})
        self.assertEqual([faq.pk for faq in response.context['faqs']], [self.faq.pk])

        response = self.client.get(reverse('admin-faqs'), {'content': 'incomplete'})
        self.assertEqual([faq.pk for faq in response.context['faqs']], [missing.pk])
        self.assertEqual(response.context['incomplete_faqs'], 1)

    def test_faq_multiline_export_and_safe_edit_payload(self):
        question = '<script>alert("test")</script>'
        answer = 'First line\nSecond line'

        faq = FAQs.objects.create(question=question, answer=answer)
        response = self.client.get(reverse('admin-faqs'), {'q': 'First line'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, question)
        self.assertEqual(response.context['faq_records'][faq.pk]['answer'], answer)

        exported = self.client.get(reverse('admin-faqs'), {'q': 'First line', 'export': 'csv'})
        rows = list(csv.reader(StringIO(exported.content.decode('utf-8-sig'))))

        self.assertEqual(rows[1][1], answer)

    def test_missing_records_return_not_found(self):
        for endpoint, payload in [('admin-company-edit', {'company_id': 'missing'}), ('admin-company-delete', {'company_id': 'missing'}),
                                  ('admin-faq-edit', {'faq_id': 'missing'}), ('admin-faq-delete', {'faq_id': 'missing'})]:
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.post(endpoint, payload).status_code, 404)
