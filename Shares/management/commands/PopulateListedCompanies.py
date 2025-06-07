import re
import requests
from Shares.models import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        contents = requests.get('https://merolagani.com/handlers/AutoSuggestHandler.ashx?type=Company').json()

        for content in contents:
            match = re.search(r"\((.*?)\)", content["l"])

            if match:
                company_name = match.group()[1:-1]

                if not ListedCompanies.objects.filter(name=company_name):
                    ListedCompanies.objects.create(name=company_name, abbreviation=content['d'])


    def handle(self, *args, **options):
        self._create_tags()
