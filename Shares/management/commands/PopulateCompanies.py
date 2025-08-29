import requests
from Shares.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        contents = requests.get('https://merolagani.com/handlers/AutoSuggestHandler.ashx?type=Company').json()
        contents = sorted(contents, key=lambda e: e['d'])

        for content in contents:
            abbreviation = content['d']

            company_name = content['l']
            company_name = ' '.join(company_name.split()[1:])[1:-1].strip()

            if not ListedCompanies.objects.filter(name=company_name):
                ListedCompanies.objects.create(name=company_name, abbreviation=abbreviation)


    def handle(self, *args, **options):
        self._create_tags()
