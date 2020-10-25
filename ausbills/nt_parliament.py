from requests import get
from bs4 import BeautifulSoup

URL = 'url'
SHORT_TITLE = 'short_title'

nt_api_url = 'https://legislation.nt.gov.au/api/sitecore/Legislation/'
nt_base_url = 'https://legislation.nt.gov.au'

class nt_All_Bills(object):
    _bills_data = []

    def __init__(self):
        try:
            self._scrape_data()
        except Exception as e:
            raise Exception('Could not create nt_all_bills, ' + e)

    def _scrape_data(self):
        _bill_titles = []
        _bill_urls = []
        soup = BeautifulSoup(get(nt_api_url).text, 'lxml')
        parent_div = soup.find('div', {'class': 'legislation-category-panel panel panel-default'})
        full_list = parent_div.find_all('div', {'class': 'panel-body'})
        for div in full_list:
            bills = div.find_all('p')
            for bill_num in range(len(bills)):
                _bill_titles.append(bills[bill_num].text.replace('\n', '')[2:])
                _bill_urls.append(nt_base_url + bills[bill_num].find('a')['href'])
        for bill in range(len(_bill_titles)):
            bill_dict = {URL: _bill_urls[bill], SHORT_TITLE: _bill_titles[bill]}
            self._bills_data.append(bill_dict)


    @property
    def data(self):
        return(self._bills_data)

nt_all_bills = nt_All_Bills().data 