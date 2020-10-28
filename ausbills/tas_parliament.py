from datetime import datetime
from requests import get
from bs4 import BeautifulSoup

current_year = datetime.today().year
url_split = ['https://www.parliament.tas.gov.au/bills/Bills', '/BillsWeb', '.htm']

URL = 'url'
TITLE = 'title'
YEAR = 'year'
PASSED_LOWER = 'passed_lower'
PASSED_UPPER = 'passed_upper'
SPONSOR = 'sponsor'
BILL_TEXT_URL = 'bill_text_url'
WAS_AMENDED_UPPER = 'was_amended_upper'
WAS_AMENDED_LOWER = 'was_amended_lower'
ASSENTED = 'assented'
ACT_NO = 'act_no'
LOWER_FIRST_READING = 'lower_first_reading'
LOWER_SECOND_READING = 'lower_second_reading'
LOWER_THIRD_READING = 'lower_third_reading'
UPPER_FIRST_READING = 'upper_first_reading'
UPPER_SECOND_READING = 'upper_second_reading'
UPPER_THIRD_READING = 'upper_third_reading'

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
                bill_dict = {URL: _bill_urls[bill], TITLE: _bill_titles[bill], YEAR: str(year)}
                self._bills_data.append(bill_dict)

    @property
    def data(self):
        return(self._bills_data)
    
tas_all_bills = tas_All_Bills().data

class tas_Bill(object):
    _all_bills = tas_all_bills

    def __init__(self, input):
        if(isinstance(input, dict)):
            try:
                self.create_vars(input)
            except Exception as e:
                raise Exception('Dict must have correct keys, missing key ' + e)
        else:
            raise ValueError('Input data must be valid tas_Bill dict data...')
    
    def create_vars(self, init_data):
        self._bill_data = init_data
        self.url = init_data[URL]
        self.title = init_data[TITLE]
        try:
            self.bill_soup = BeautifulSoup(get(self.url).text, 'lxml')
            table = self.bill_soup.find('table', {'bordercolor': '#CCCCCC'})
            self._rows = table.find_all('tr')
        except:
            raise Exception('Unable to scrape ' + self.url)
        self.get_first_readings()
        self.get_second_readings()
        self.get_third_readings()

    @property
    def sponsor(self):
        rows = self._rows
        try:
            return(rows[0].find('td', {'colspan': '4'}).text.replace(' Introduced by: ', '').strip())
        except:
            return ''

    @property
    def bill_text_url(self):
        try:
            return(url_split[0] + self._bill_data[YEAR] + '/' + self._rows[1].find('a')['href'])
        except:
            return ''

    @property
    def was_amended_upper(self):
        return(self.amended_check()[1])
    
    @property
    def was_amended_lower(self):
        return(self.amended_check()[0])

    @property
    def passed_lower(self):
        column = self._rows[12:][0].find('td')
        try:
            return(self.format_date(column.find('br').previousSibling.strip().replace('HA Agreed: ', '')))
        except:
            return False

    @property
    def passed_upper(self):
        column = self._rows[12:][0].find('td')
        try:
            return(self.format_date(column.find('br').nextSibling.strip().replace('Agreed Both: ', '')))
        except:
            return False

    @property
    def assented(self):
        column = self._rows[12:][0].find('td')
        try:
            return(self.format_date(column.find_all('br', limit=2)[-1].nextSibling.strip().replace('Royal Assent: ', '')))
        except:
            return False

    @property
    def act_no(self):
        column = self._rows[12:][0].find('td')
        try:
            return(column.find_all('br', limit=4)[-1].nextSibling.replace('Act Number:', '').strip())
        except:
            return ''

    def amended_check(self):
        columns = self._rows[9:][0].find_all('td')
        lower = columns[1].text.strip()
        upper = columns[3].text.strip()
        if(lower == 'Yes'):
            lower = True
        else:
            lower = False

        if(upper == 'Yes'):
            upper = True
        else:
            upper = False
        return[lower, upper]

    def get_first_readings(self):
        columns = self._rows[3:][0].find_all('td')
        try:
            self.lower_first_reading = self.format_date(columns[1].text.strip())
        except:
            self.lower_first_reading = ''

        try:
            self.upper_first_reading = self.format_date(columns[3].text.strip())
        except:
            self.upper_first_reading = ''

    def get_second_readings(self):
        columns = self._rows[5:][0].find_all('td')
        try:
            self.lower_second_reading = self.format_date(columns[1].text.strip())
        except:
            self.lower_second_reading = ''
        
        try:
            self.upper_second_reading = self.format_date(columns[3].text.strip())
        except:
            self.upper_second_reading = ''

    def get_third_readings(self):
        columns = self._rows[10:][0].find_all('td')
        try:
            self.lower_third_reading = self.format_date(columns[1].text.strip())
        except:
            self.lower_third_reading = ''
        
        try:
            self.upper_third_reading = self.format_date(columns[3].text.strip())
        except:
            self.upper_third_reading = ''

    def format_date(self, input_date):
        dateSplit = input_date.split('/', 2)
        return("{:0>2s}".format(dateSplit[0]) + '-' "{:0>2s}".format(dateSplit[1]) + '-' + dateSplit[2])

    @property
    def data(self):
        self._bill_data[PASSED_LOWER] = self.passed_lower
        self._bill_data[PASSED_UPPER] = self.passed_upper
        self._bill_data[LOWER_FIRST_READING] = self.lower_first_reading
        self._bill_data[LOWER_SECOND_READING] = self.lower_second_reading
        self._bill_data[LOWER_THIRD_READING] = self.lower_third_reading
        self._bill_data[UPPER_FIRST_READING] = self.upper_first_reading
        self._bill_data[UPPER_SECOND_READING] = self.upper_second_reading
        self._bill_data[UPPER_THIRD_READING] = self.upper_third_reading
        self._bill_data[SPONSOR] = self.sponsor
        self._bill_data[BILL_TEXT_URL] = self.bill_text_url
        self._bill_data[ASSENTED] = self.assented
        self._bill_data[WAS_AMENDED_LOWER] = self.was_amended_lower
        self._bill_data[WAS_AMENDED_UPPER] = self.was_amended_upper
        self._bill_data[ACT_NO] = self.act_no
        return(self._bill_data)