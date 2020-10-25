from requests import get
from bs4 import BeautifulSoup

URL = 'url'
SHORT_TITLE = 'short_title'
EXPLANITORY_STATEMENT = 'explanatory_statement'
TEXT_URL = 'text_url'
STATUS = 'status'
SPONSOR = 'sponsor'
SERIAL_NO = 'serial_no'
PARLIAMENT_NO = 'parliament_no'
REMARKS = 'remarks'
INTRO_DATE = 'intro_date'
DATE = 'date'

nt_api_url = 'https://legislation.nt.gov.au/LegislationPortal/Bills/By-Title'
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
        parent_div = soup.find('div', {'class': 'panel panel-default'})
        bills = parent_div.find_all('a')
        for bill in bills:
            _bill_urls.append(nt_base_url + '/' + bill['href'][:-9].replace('\n', ''))
            if(bill.text[0] == ' '):
                _bill_titles.append(bill.text[1:])
            else:
                _bill_titles.append(bill.text)
        for entry in range(len(_bill_titles)):
            bill_dict = {URL: _bill_urls[entry], SHORT_TITLE: _bill_titles[entry]}
            self._bills_data.append(bill_dict)

    @property
    def data(self):
        return(self._bills_data)

nt_all_bills = nt_All_Bills().data

class nt_Bill(object):
    _nt_all_bills = nt_all_bills

    def __init__(self, input):
        if(isinstance(input, dict)):
            try:
                self.create_vars(input)
            except Exception as e:
                raise ValueError('Dict must have valid keys, missing key: ' + e)
        else:
            raise ValueError('Input must be valid nt_Bill data.')
    
    def create_vars(self, init_data):
        self._bill_data = init_data
        self.url = init_data[URL]
        self.short_title = init_data[SHORT_TITLE]
        try:
            self.bill_soup = BeautifulSoup(get(self.url).text, 'lxml')
        except:
            raise Exception('Unable to scrape ' + self.url)
    
    @property
    def explanatory_statement(self):
        try:
            a = self.bill_soup.find(text='Explanatory Statement:').findNext('a')['href']
            return(a)
        except:
            return ''

    @property
    def text_url(self):
        try:
            url = self.bill_soup.find_all('div', {'class': 'col-sm-6 text-center'})[1].find('a')['href']
            return(url)
        except:
            return ''

    @property
    def status(self):
        try:
            fieldset = self.bill_soup.find('fieldset', {'class': 'roundedWhiteBorders'})
            stat = fieldset.find(text='Status:').parent.findNext('span').text.replace('\n', '')
            return(stat)
        except:
            return ''

    @property
    def sponsor(self):
        return(self._get_span_text('Sponsor:'))

    @property
    def serial_no(self):
        return(self._get_span_text('Serial No:'))

    @property
    def parliament_no(self):
        return(self._get_span_text('Assembly:'))

    @property
    def remarks(self):
        return(self._get_span_text('Remarks:'))

    @property
    def intro_date(self):
        return(self._get_span_date('Introduced:'))

    @property
    def date(self):
        return(self._get_span_date('Date:'))

    def _get_span_text(self, input_text):
        try:
            span = self.bill_soup.find(text=input_text).findNext('span').text
            return(span)
        except:
            return ''

    def _get_span_date(self, input_text):
        try:
            span = self.bill_soup.find(text=input_text).findNext('span').text
            return(span.replace('/', '-'))
        except:
            return ''

    @property
    def data(self):
        self._bill_data[DATE] = self.date
        self._bill_data[INTRO_DATE] = self.intro_date
        self._bill_data[REMARKS] = self.remarks
        self._bill_data[PARLIAMENT_NO] = self.parliament_no
        self._bill_data[SERIAL_NO] = self.serial_no
        self._bill_data[SPONSOR] = self.sponsor
        self._bill_data[STATUS] = self.status
        self._bill_data[TEXT_URL] = self.text_url
        self._bill_data[EXPLANITORY_STATEMENT] = self.explanatory_statement
        return(self._bill_data)