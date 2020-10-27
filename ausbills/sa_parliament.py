from requests import get
from bs4 import BeautifulSoup

bill_list_urls = ['https://legislation.sa.gov.au/listBills.aspx?key=', 'https://legislation.sa.gov.au/listAZBills.aspx?key=']
sa_base_url = 'https://legislation.sa.gov.au/'

URL = 'url'
SHORT_TITLE = 'short_title'
SPONSOR = 'sponsor'
TEXTS = 'texts'

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

class sa_Bill(object):
    _all_bills = sa_all_bills

    def __init__(self, input):
        if(isinstance(input, dict)):
            try:
                self.create_vars(input)
            except Exception as e:
                raise ValueError('Dict must have correct keys, missing key ' + e)
        else:
            raise ValueError('Input must be valid sa_Bill dict data...')
    
    def create_vars(self, init_data):
        self._bill_data = init_data
        self.url = init_data[URL]
        self.short_title = init_data[SHORT_TITLE]
        try:
            self.bill_soup = BeautifulSoup(get(self.url).text, 'lxml')
        except:
            raise Exception('Unable to scrape ' + self.url)
    
    @property
    def sponsor(self):
        if(self._bill_data[SPONSOR] == ''):
            try:
                text = self.bill_soup.find('div', {'class': 'ItemIntroducedBy'}).find('p').text
                return(text)
            except:
                return ''
        else:
            return(self._bill_data[SPONSOR][1:])
    
    @property
    def texts(self):
        try:
            data_list = []
            table_body = self.bill_soup.find('table', {'summary': 'A List of the various stages of this Bill'}).find('tbody')
            links = table_body.find_all('a', {'title': 'View document in PDF in new window'})
            for link in links:
                data_url = sa_base_url + link['href'].replace(' ', '%20')
                data_text = link.parent.findPrevious('td').text
                data_dict = {data_text: data_url}
                data_list.append(data_dict)
            return(data_list)
        except:
            return []

    @property
    def data(self):
        self._bill_data[TEXTS] = self.texts
        self._bill_data[SPONSOR] = self.sponsor
        return(self._bill_data)