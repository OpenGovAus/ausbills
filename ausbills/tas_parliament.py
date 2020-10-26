from datetime import datetime
from requests import get
from bs4 import BeautifulSoup

current_year = datetime.today().year
url_split = ['https://www.parliament.tas.gov.au/bills/Bills', '/BillsWeb', '.htm']

URL = 'url'
TITLE = 'title'

class tas_All_Bills(object):
    _bills_data = []

    def __init__(self):
        try:
            self.create_dataset()
        except:
            raise Exception('Error when scraping bills...')

    def create_dataset(self):
        for year in range(current_year - (current_year - 2002), current_year + 1):
            soup = BeautifulSoup(get(url_split[0] + str(year) + url_split[1] + str(year) + url_split[2]).text, 'lxml')
            table = soup.find('table', {'bordercolor': '#CCCCCC'})
            bills = table.find_all('a')
            _bill_urls = []
            _bill_titles = []
            for bill in bills:
                _bill_titles.append(bill.text.strip())
                _bill_urls.append(url_split[0] + str(year) + '/' + bill['href'])
            for bill in range(len(_bill_titles)):
                bill_dict = {URL: _bill_urls[bill], TITLE: _bill_titles[bill]}
                self._bills_data.append(bill_dict)
            

    @property
    def data(self):
        return(self._bills_data)
    
tas_all_bills = tas_All_Bills().data