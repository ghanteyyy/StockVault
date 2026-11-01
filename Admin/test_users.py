'''
Member-management behavior against an isolated test database
'''

from io import BytesIO
from unittest.mock import patch

from django.contrib.admin.models import ADDITION, LogEntry
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import path
from PIL import Image

from Shares.models import ListedCompanies, Portfolios, Transactions, WishLists
from Users.models import CustomUser, Targets
from . import user_views


def placeholder(request):
    return HttpResponse('Preview route')


urlpatterns = [
    path('login/', placeholder, name='login'),
    path('admin/', placeholder, name='admin-index'),
    path('admin/users', user_views.AdminPage, name='admin-users'),
    path('admin/profile', user_views.UserProfile, name='admin-user-profile'),
    path('admin/user/add', user_views.AddUser, name='admin-user-add'),
    path('admin/user/edit', user_views.EditUser, name='admin-user-edit'),
    path('admin/user/delete', user_views.DeleteUser, name='admin-user-delete'),
    path('admin/profile/change/password', user_views.UserChangePassword, name='admin-user-change-password'),
    path('admin/profile/change/profile-image', user_views.ChangeProfile, name='admin-user-change-profile-image'),
]


@override_settings(ROOT_URLCONF=__name__)
class AdminMemberTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user('admin@example.com', 'Initial-Admin28!', name='Admin User', gender='others', is_staff=True)
        self.member = CustomUser.objects.create_user('member@example.com', 'Initial-Member28!', name='Member User', gender='female')
        self.other_admin = CustomUser.objects.create_user('otheradmin@example.com', 'Initial-Admin28!', name='Other Admin', gender='male', is_staff=True)
        self.client.force_login(self.admin)

        self.valid = {'name': 'New Member', 'email': 'new@example.com', 'gender': 'others',
                      'dob': '2000-01-01', 'password': 'Canvas-Window28!'}

    def test_staff_required_for_directory_and_every_mutation(self):
        self.client.force_login(self.member)

        for url in ('/admin/users', '/admin/profile', '/admin/user/add', '/admin/user/edit', '/admin/user/delete',
                    '/admin/profile/change/password', '/admin/profile/change/profile-image'):
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 403)

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()
        response = self.client.get('/admin/users')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_get_cannot_mutate_accounts(self):
        for url in ('/admin/user/add', '/admin/user/edit', '/admin/user/delete', '/admin/profile/change/password', '/admin/profile/change/profile-image'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 405)

    def test_create_regular_member_and_audit(self):
        response = self.client.post('/admin/user/add', {**self.valid, 'is_staff': 'true', 'is_superuser': 'true'})
        self.assertEqual(response.status_code, 200)

        created = CustomUser.objects.get(email='new@example.com')

        self.assertFalse(created.is_staff)
        self.assertFalse(created.is_superuser)
        self.assertTrue(created.check_password(self.valid['password']))
        self.assertTrue(LogEntry.objects.filter(object_id=created.pk, action_flag=ADDITION, user=self.admin).exists())

    def test_incomplete_create_returns_errors_without_account(self):
        before = CustomUser.objects.count()
        response = self.client.post('/admin/user/add', {})

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json()['errors'])
        self.assertEqual(CustomUser.objects.count(), before)

    def test_duplicate_email_is_case_insensitive(self):
        response = self.client.post('/admin/user/add', {**self.valid, 'email': 'MEMBER@example.com'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json()['errors'])

    def test_invalid_dob_and_unsupported_gender_return_field_errors(self):
        response = self.client.post('/admin/user/add', {**self.valid, 'gender': 'prefer_not_to_say', 'dob': '2030-02-31'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('gender', response.json()['errors'])
        self.assertIn('dob', response.json()['errors'])

    def test_password_whitespace_is_preserved_on_create(self):
        password = '  Canvas-Window28!  '
        self.client.post('/admin/user/add', {**self.valid, 'password': password})
        created = CustomUser.objects.get(email='new@example.com')

        self.assertTrue(created.check_password(password))
        self.assertFalse(created.check_password(password.strip()))

    def test_edit_regular_member_ignores_role_and_password_flags(self):
        response = self.client.post('/admin/user/edit', {**self.valid, 'user_id': self.member.pk,
                                                       'email': 'updated@example.com', 'is_staff': 'true', 'password': 'Unexpected-change28!'})
        self.assertEqual(response.status_code, 200)

        self.member.refresh_from_db()

        self.assertEqual(self.member.email, 'updated@example.com')
        self.assertFalse(self.member.is_staff)
        self.assertTrue(self.member.check_password('Initial-Member28!'))
        self.assertTrue(LogEntry.objects.filter(object_id=self.member.pk, change_message__contains='Updated name').exists())

    def test_other_administrator_details_are_protected(self):
        response = self.client.post('/admin/user/edit', {**self.valid, 'user_id': self.other_admin.pk})
        self.assertEqual(response.status_code, 403)

        self.other_admin.refresh_from_db()
        self.assertEqual(self.other_admin.name, 'Other Admin')

    def test_current_administrator_can_edit_own_basic_details(self):
        response = self.client.post('/admin/user/edit', {**self.valid, 'user_id': self.admin.pk, 'email': self.admin.email})
        self.assertEqual(response.status_code, 200)

        self.admin.refresh_from_db()
        self.assertEqual(self.admin.name, 'New Member')
        self.assertTrue(self.admin.is_staff)

    def test_deactivation_and_reactivation_preserve_financial_records(self):
        company = ListedCompanies.objects.create(name='Example Bank', abbreviation='EXBK', sector='Commercial Banks')
        portfolio = Portfolios.objects.create(user_id=self.member, company_id=company, number_of_shares=10, total_cost=1000)

        response = self.client.post('/admin/user/delete', {'user_id': self.member.pk, 'active': 'false'})
        self.assertEqual(response.status_code, 200)

        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)
        self.assertTrue(Portfolios.objects.filter(pk=portfolio.pk).exists())

        response = self.client.post('/admin/user/delete', {'user_id': self.member.pk, 'active': 'true'})
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)
        self.assertEqual(LogEntry.objects.filter(object_id=self.member.pk).count(), 2)

    def test_status_change_rejects_self_staff_and_missing_choice(self):
        for member in (self.admin, self.other_admin):
            response = self.client.post('/admin/user/delete', {'user_id': member.pk, 'active': 'false'})
            self.assertEqual(response.status_code, 403)

        response = self.client.post('/admin/user/delete', {'user_id': self.member.pk})
        self.assertEqual(response.status_code, 400)

    def test_password_change_is_self_only_and_requires_current_password(self):
        response = self.client.post('/admin/profile/change/password', {'user_id': self.member.pk, 'new_password': 'Canvas-Window28!'})
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/admin/profile/change/password', {'user_id': self.admin.pk, 'old_password': 'wrong',
                                                                     'new_password1': 'Canvas-Window28!', 'new_password2': 'Canvas-Window28!'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('old_password', response.json()['errors'])

    def test_own_password_change_preserves_session_and_audits_without_secret(self):
        response = self.client.post('/admin/profile/change/password', {'user_id': self.admin.pk, 'old_password': 'Initial-Admin28!',
                                                                     'new_password1': 'Canvas-Window28!', 'new_password2': 'Canvas-Window28!'})
        self.assertEqual(response.status_code, 200)

        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password('Canvas-Window28!'))
        self.assertEqual(self.client.session['_auth_user_id'], self.admin.pk)

        entry = LogEntry.objects.get(object_id=self.admin.pk)
        self.assertNotIn('Canvas', entry.change_message)

    def test_photo_validation_handles_missing_and_disguised_files(self):
        response = self.client.post('/admin/profile/change/profile-image', {'user_id': self.member.pk})
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/admin/profile/change/profile-image', {'user_id': self.member.pk,
                    'profile_image': SimpleUploadedFile('fake.png', b'not an image', content_type='image/png')})

        self.assertEqual(response.status_code, 400)
        self.assertIn('profile_image', response.json()['errors'])

    def test_valid_profile_image_is_saved_and_audited(self):
        buffer = BytesIO()
        Image.new('RGB', (4, 4), '#aabbcc').save(buffer, format='PNG')

        response = self.client.post('/admin/profile/change/profile-image', {'user_id': self.member.pk,
                    'profile_image': SimpleUploadedFile('photo.png', buffer.getvalue(), content_type='image/png')})

        self.assertEqual(response.status_code, 200)

        self.member.refresh_from_db()
        self.assertTrue(self.member.profile_image.name.endswith('.png'))
        self.assertTrue(LogEntry.objects.filter(object_id=self.member.pk, change_message__contains='profile image').exists())

    def test_photo_for_another_administrator_is_rejected(self):
        response = self.client.post('/admin/profile/change/profile-image', {'user_id': self.other_admin.pk})
        self.assertEqual(response.status_code, 403)

    def test_directory_search_status_role_filters_apply_before_pagination(self):
        self.member.is_active = False
        self.member.save(update_fields=['is_active'])

        with patch('Admin.user_views.render', return_value=HttpResponse('directory')) as render:
            self.client.get('/admin/users', {'q': 'MEMBER', 'status': 'inactive', 'role': 'member', 'per_page': '20'})
            context = render.call_args.args[2]

            self.assertEqual(list(context['page_obj']), [self.member])
            self.assertEqual(context['user_stats']['total'], 3)
            self.assertIn('q=MEMBER', context['query_string'])

    def test_filtered_csv_exports_values_not_passwords(self):
        self.member.name = '=dangerous()'
        self.member.save(update_fields=['name'])

        response = self.client.get('/admin/users', {'role': 'member', 'export': 'csv'})
        self.assertEqual(response.status_code, 200)

        text = response.content.decode('utf-8-sig')
        self.assertIn("'=dangerous()", text)
        self.assertNotIn(self.admin.email, text)
        self.assertNotIn('Initial-Member', text)
        self.assertIn('attachment', response['Content-Disposition'])

    def test_profile_counts_and_unsupported_targets_are_not_leaked(self):
        company = ListedCompanies.objects.create(name='Example Bank', abbreviation='EXBK', sector='Commercial Banks')

        Targets.objects.create(user_id=self.member, company_id=company, target_type='buy', is_deleted=True)
        Targets.objects.create(user_id=self.member, company_id=company, target_type='sell', is_deleted=False)
        WishLists.objects.create(user_id=self.member, company_id=company)

        with patch('Admin.user_views.render', return_value=HttpResponse('profile')) as render:
            self.client.get('/admin/profile', {'id': self.member.pk})
            context = render.call_args.args[2]

            self.assertEqual(context['member_counts']['targets'], 1)
            self.assertEqual(context['member_counts']['wishlists'], 1)
            self.assertTrue(context['can_change_status'])

        self.assertEqual(self.client.get('/admin/profile', {'user': 'missing@example.com'}).status_code, 404)

    def test_mutation_rolls_back_when_auditing_fails(self):
        before = CustomUser.objects.count()

        with patch('Admin.user_views.record_admin_action', side_effect=RuntimeError('audit unavailable')):
            with self.assertRaises(RuntimeError):
                self.client.post('/admin/user/add', self.valid)

        self.assertEqual(CustomUser.objects.count(), before)

    def test_mutations_keep_csrf_protection(self):
        protected_client = Client(enforce_csrf_checks=True)
        protected_client.force_login(self.admin)

        self.assertEqual(protected_client.post('/admin/user/add', self.valid).status_code, 403)

    @override_settings(ROOT_URLCONF='core.urls')
    def test_real_user_directory_renders_filters_create_form_and_export(self):
        response = self.client.get('/admin/users')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'People behind the portfolios.')
        self.assertContains(response, 'data-admin-form')
        self.assertContains(response, 'id="create-user-dialog"')
        self.assertContains(response, 'name="role"')
        self.assertContains(response, 'Export CSV')

    @override_settings(ROOT_URLCONF='core.urls')
    def test_real_profile_exposes_appropriate_controls_and_stable_edit_destination(self):
        response = self.client.get('/admin/profile', {'id': self.member.pk})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'data-success-url="/admin/profile?id={self.member.pk}"')
        self.assertContains(response, 'Deactivate account')
        self.assertNotContains(response, 'name="old_password"')

        own = self.client.get('/admin/profile', {'id': self.admin.pk})
        self.assertContains(own, 'name="old_password"')
        self.assertNotContains(own, 'id="member-status-dialog"')

    @override_settings(ROOT_URLCONF='core.urls')
    def test_other_admin_profile_is_read_only_without_mutation_forms(self):
        response = self.client.get('/admin/profile', {'id': self.other_admin.pk})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'read-only')
        self.assertNotContains(response, 'data-admin-form')
