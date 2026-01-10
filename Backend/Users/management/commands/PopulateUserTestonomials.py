import random
from Users.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        testonomials = [
            'Stock Vault simplified my investment tracking. I love the historical charts!',
            'As a BCA student, I built this to help others and it’s now used by 100+ users!',
            'Finally, an app that makes stock tracking easy for beginners like me.',
            'The portfolio insights are so clear—no more messy spreadsheets.',
            'I check my Stock Vault dashboard every morning before trading.',
            'The clean design and simple navigation make it perfect for busy students.',
            'I never realized how much I was over-investing until Stock Vault showed me trends.',
            'Historical charts helped me backtest my strategy—amazing feature!',
            'Being new to investing, Stock Vault gave me confidence to track my first portfolio.',
            'I shared this tool with my classmates—now half of them use it too.',
            'The export option saves me hours when preparing reports.',
            'It’s so lightweight but gives me all the data I need at a glance.',
            'Stock Vault is my go-to app for monitoring market moves daily.',
            'Even my parents, who aren’t tech savvy, use it to watch their stocks.',
            'It feels like Stock Vault was made for students—simple, reliable, and free.',
            'I used to forget when I bought certain stocks. Now, everything is organized.',
            'Stock Vault helped me cut my losses by tracking performance patterns.',
            'This project shows how powerful a student-built tool can be.',
            'I love how Stock Vault balances simplicity with professional-level features.',
            'From my first trade to my 100th, Stock Vault has been my companion.'
        ]

        users = list(CustomUser.objects.filter(is_superuser=False, is_active=True))
        random.shuffle(users)

        for user in users:
            testonomial = random.choice(testonomials)

            testonomial_for_user = Testonomials(user_id=user, message=testonomial)
            testonomial_for_user.save()

    def handle(self, *args, **options):
        self._create_tags()
