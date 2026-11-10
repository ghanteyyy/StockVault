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
        self.assertContains(response, 'id="trade-calculator"', count=1)
        self.assertContains(response, 'id="trade-form"', count=1)
        self.assertContains(response, 'js/users/calculator.js', count=1)
        self.assertRedirects(self.client.get(reverse('trade-calculator')), f'{homepage}#trade-calculator')

    def test_workspace_shortcut_opens_the_same_calculator(self):
        self.client.force_login(self.member)
        homepage = reverse('index')
        calculator = f'{homepage}?tool=trade-calculator'

        self.assertRedirects(self.client.get(homepage), reverse('dashboard'), fetch_redirect_response=False)
        self.assertRedirects(self.client.get(reverse('trade-calculator')), f'{calculator}#trade-calculator')

        response = self.client.get(calculator)
        self.assertTemplateUsed(response, 'users/index.html')
        self.assertContains(response, 'id="workspace-sidebar"')
        self.assertContains(response, 'id="trade-form"', count=1)
