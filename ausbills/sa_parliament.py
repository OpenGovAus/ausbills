from requests import get
from bs4 import BeautifulSoup

bill_list_urls = ['https://legislation.sa.gov.au/listBills.aspx?key=', 'https://legislation.sa.gov.au/listAZBills.aspx?key=']
sa_base_url = 'https://legislation.sa.gov.au/'

URL = 'url'
SHORT_TITLE = 'short_title'
SPONSOR = 'sponsor'

class sa_All_Bills(object):
    _bills_data = []

    def __init__(self):
        try:
            self.create_dataset()
        except:
            raise Exception('An error ocurred when trying to scrape bills...')
    
    def create_dataset(self):
        _bill_titles = []
        _bill_urls = []
        for list_url in bill_list_urls:
            table = BeautifulSoup(get(list_url).text, 'lxml').find('table', {'summary': 'A List of the various versions of this Bills beginning with this letter'}).find('tbody')
            for row in table.find_all('tr'):
                _bill_urls.append(sa_base_url + row.find('a')['href'].replace(' ', '%20'))
                _bill_titles.append(row.find('a').text.replace('\n', '').replace('\r', ' ').replace('\xa0', ' ').replace('  ', ' '))
        for bill in range(len(_bill_titles)):
            if('—introduced by' in _bill_titles[bill]):
                title_split = _bill_titles[bill].split('—introduced by')
                bill_dict = {URL: _bill_urls[bill], SHORT_TITLE: title_split[0], SPONSOR: title_split[1]}
                self._bills_data.append(bill_dict)
            else:
                bill_dict = {URL: _bill_urls[bill], SHORT_TITLE: _bill_titles[bill], SPONSOR: ''}
                self._bills_data.append(bill_dict)

    @property
    def data(self):
        return(self._bills_data)

sa_all_bills = sa_All_Bills().data