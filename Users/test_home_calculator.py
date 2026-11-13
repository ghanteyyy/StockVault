from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomepageCalculatorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = get_user_model().objects.create_user(
            email='calculator@example.test', name='Calculator Member',
        )

    def test_visitors_can_open_the_calculator_on_the_homepage(self):
        homepage = reverse('index')
        response = self.client.get(homepage)

        self.assertTemplateUsed(response, 'users/index.html')
        self.assertTemplateUsed(response, 'users/calculator.html')
        self.assertContains(response, 'id="trade-calculator"', count=1)
        self.assertContains(response, 'id="trade-form"', count=1)
        self.assertContains(response, 'js/users/calculator.js', count=1)
        self.assertRedirects(self.client.get(reverse('trade-calculator')), f'{homepage}#trade-calculator')

    def test_dashboard_requires_sign_in(self):
        dashboard = reverse('dashboard')
        self.assertRedirects(
            self.client.get(dashboard), f"{reverse('login')}?next={dashboard}", fetch_redirect_response=False,
        )

    def test_signed_in_homepage_and_legacy_calculator_redirect(self):
        self.client.force_login(self.member)
        homepage = reverse('index')

        self.assertRedirects(self.client.get(homepage), reverse('dashboard'), fetch_redirect_response=False)
        self.assertRedirects(self.client.get(f'{homepage}?tool=trade-calculator'), reverse('trade-calculator'))

    def test_workspace_shortcut_opens_only_the_calculator(self):
        self.client.force_login(self.member)
        calculator = reverse('trade-calculator')
        response = self.client.get(calculator)

        self.assertTemplateUsed(response, 'users/trade_calculator.html')
        self.assertTemplateUsed(response, 'users/calculator.html')
        self.assertTemplateNotUsed(response, 'users/index.html')
        self.assertTemplateNotUsed(response, 'users/dashboard.html')
        self.assertContains(response, 'id="workspace-sidebar"')
        self.assertContains(response, f'href="{reverse("notifications")}"', count=1)
        self.assertNotContains(response, 'id="notification-panel"')
        self.assertContains(response, f'href="{calculator}"')
        self.assertContains(response, 'id="trade-calculator"', count=1)
        self.assertContains(response, 'id="trade-form"', count=1)
        self.assertContains(response, 'js/users/calculator.js', count=1)
