import requests
from Shares.models import *
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def _create_tags(self):
        contents = requests.get('https://merolagani.com/handlers/AutoSuggestHandler.ashx?type=Company').json()
        contents = sorted(contents, key=lambda e: e['d'])

        for content in contents:
            abbreviation = content['d']
            company_name = content['l']

            req = requests.get(f'https://merolagani.com/CompanyDetail.aspx?symbol={abbreviation}').content
            soup = BeautifulSoup(req, 'html.parser')

            sector_th = soup.find("th", string=lambda t: t and "Sector" in t)
            sector = sector_th.find_next("td").get_text(strip=True)

            if not ListedCompanies.objects.filter(name=company_name):
                ListedCompanies.objects.create(name=company_name, abbreviation=abbreviation, sector=sector)


    def handle(self, *args, **options):
        self._create_tags()
