import datetime
from requests import get
from bs4 import BeautifulSoup
import io
import re

URL = 'url'
TITLE = 'title'
STATUS = 'status'
ORIGIN = 'origin'
ACT_NO = 'act_no'
YEAR = 'year'
TYPE = 'type'
CARRIAGE_MEMBER = 'carriage_member'
LONG_TITLE = 'long_title'
BILL_TEXT = 'text'

base_url = 'https://www.parliament.nsw.gov.au/bills/pages/all-bills-1997.aspx?session=0'

class nsw_All_Bills(object):
    _bills_data = []
    def __init__(self):
        self._create_dataset()

    def _create_dataset(self):
        _bill_titles = []
        _bill_origin = []
        _bill_urls = []

        soup = BeautifulSoup(get(base_url).text, 'lxml')
        table = soup.find('table', {'id': 'prlMembers'})
        rows = table.find_all('tr')
        rows.pop(0)
        for row in rows:
            _bill_titles.append(row.find_all('td')[0].text[5:-3])
            _bill_origin.append(row.find_all('td')[1].text[1:].replace('LA', 'Legislative Assembly').replace('LC', 'Legislative Council'))
            try:
                _bill_urls.append(('https://www.parliament.nsw.gov.au' + row.find('a', {'class': 'prl-name-link'})['href']))
            except:
                _bill_urls.append('')
        for bill in range(len(_bill_titles)):
            _bill_dict = {TITLE: _bill_titles[bill], URL: _bill_urls[bill], ORIGIN: _bill_origin[bill]}
            self._bills_data.append(_bill_dict)
    
    @property
    def data(self):
        return(self._bills_data)

nsw_all_bills = nsw_All_Bills().data

class nsw_Bill(object):
    _bill_data = dict()

    def __init__(self, bill_dict: dict = None):
        initial_data = bill_dict
        if initial_data is None:
            raise ValueError('This shouldn\'t even be possible yet...')

        try:
            self._bill_data = dict(**initial_data)
            self.url = initial_data[URL]
            self.title = initial_data[TITLE]
            self.origin = initial_data[ORIGIN]
            self.page_data = get(self.url).text
            self.bill_soup = BeautifulSoup(self.page_data, 'lxml')
        except KeyError as e:
            raise KeyError('Dict must have correct keys, missing key ' + e)
    
    @property
    def bill_text(self):
        try:
            text_url = self.bill_soup.find('td', {'class': 'bill-details-docs right'}).find('td', {'class': 'attachment'}).find('a', {'target': '_blank'})['href']
            return(text_url)
        except:
            return('')

    @property
    def bill_type(self):
        try:
            table = self.bill_soup.find('table', {'class': re.compile(r'(details green-table|details maroon-table)')})
            return(table.find('tr').find_all('td')[1].text)
        except:
            raise Exception('Couldn\'t find table in: ' + self.url)
        

    @property
    def status(self):
        table = self.bill_soup.find('table', {'class': re.compile(r'(details green-table|details maroon-table)')})
        return(table.find_all('tr')[1].find_all('td')[1].text)

    @property
    def carriage_member(self):
        member = None
        table = self.bill_soup.find('table', {'class': re.compile(r'(details green-table|details maroon-table)')})
        for td in table.find_all('td'):
            if('Member with Carriage:' in td.text):
                member = td.findNext('td').text
        if member == None:
            return ''
        else:
            return member

    @property
    def long_title(self):
        longtitle = None
        table = self.bill_soup.find('table', {'class': re.compile(r'(details green-table|details maroon-table)')})
        for td in table.find_all('td'):
            if('Long Title:' in td.text):
                longtitle = td.findNext('td').text
        if longtitle == None:
            return ''
        else:
            return longtitle

    @property
    def act_no(self):
        number = None
        table = self.bill_soup.find('table', {'class': re.compile(r'(details green-table|details maroon-table)')})
        for td in table.find_all('td'):
            if('Act number:' in td.text):
                number = td.findNext('td').text
        if number == None:
            return ''
        else:
            return number

    @property
    def data(self):
        self._bill_data[URL] = self.url
        self._bill_data[TYPE] = self.bill_type
        self._bill_data[ACT_NO] = self.act_no
        self._bill_data[LONG_TITLE] = self.long_title.replace('\r', '').replace('\n', '')
        self._bill_data[CARRIAGE_MEMBER] = self.carriage_member
        self._bill_data[STATUS] = self.status
        self._bill_data[ORIGIN] = self.origin
        self._bill_data[TITLE] = self.title
        self._bill_data[BILL_TEXT] = self.bill_text
        return(self._bill_data)