import re
import requests
from bs4 import BeautifulSoup


def get_market_data(company_symbol):
    '''
    Get market data of the given company symbol
    '''

    url = f'https://merolagani.com/CompanyDetail.aspx?symbol={company_symbol}'

    page = requests.get(url)  # Getting information of the given company
    soup = BeautifulSoup(page.content, "html.parser")

    company_name = soup.find_all(id="ctl00_ContentPlaceHolder1_CompanyDetail1_companyName")[0].text  # Extracting company name

    if company_name:
        share_value = soup.find_all(id="ctl00_ContentPlaceHolder1_CompanyDetail1_lblMarketPrice")[0].text  # Extracting market price
        sector = soup.find_all("td", {"class": "text-primary"})[0].text.strip()  # Extracting sector of the company
        change = soup.find_all(id="ctl00_ContentPlaceHolder1_CompanyDetail1_lblChange")[0].text  # Extracting percentage change of the company

        # Extracting date of transaction done by the company
        date_pattern = re.compile(r'\d+/\d+/\d+ \d+:\d+:\d+')
        date = re.search(date_pattern, page.text)
        date = date.group() if date else ''

        # Extracting high and low value of the company
        high_low_pattern = re.compile(r'\d+[,\d+]\d+[.\d+]\d+-\d+[,\d+]\d+[.\d+]\d+')
        high_low = re.search(high_low_pattern, page.text)
        high_low = high_low.group(0) if high_low else '0.00-0.00'

        index = page.text.index('120 Day Average')
        average_value = page.text[index: index + 200].split()[6]

        profit_loss = soup.find_all(id="ctl00_ContentPlaceHolder1_CompanyDetail1_lblMarketPrice")[0].prettify()

        return {'company_name': company_name,
                'sector': sector,
                'profit_loss': profit_loss,
                'market_price': share_value,
                'change': change,
                'last_traded_on': date,
                'high_low': high_low,
                'average': average_value
            }
