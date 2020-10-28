import re
import json
from requests import get
from bs4 import BeautifulSoup

base_url = 'https://www.legislation.vic.gov.au/'
api_url = base_url + 'app/api/search/title_content?from=0&size=9999&includeFilters[0][prefix][title_az]=&includeFilters[1][term][type]=bill&includeFields[0]=title&includeFields[1]=field_in_force_former_title&includeFields[2]=url&includeFields[3]=type&includeFields[4]=legislation_type&includeFields[5]=field_act_sr_number&includeFields[6]=legislation_year&includeFields[7]=field_act_sr_status_date&includeFields[8]=field_legislation_status&includeFields[9]=field_bill_pre_2004&includeFields[10]=field_bill_parliament_term&sort[0][_score]=desc&sort[1][title_az]=asc&aggregations[legislation_year][terms][field]=legislation_year&aggregations[legislation_year][terms][order][_key]=desc&aggregations[legislation_year][terms][size]=250&aggregations[field_legislation_status][terms][field]=field_legislation_status&aggregations[field_legislation_status][terms][order][_key]=asc&aggregations[field_legislation_status][terms][size]=250'

URL = 'url'
ID = 'id'
SHORT_TITLE = 'short_title'
STATUS = 'status'
STATUS_REPORT = 'status_report'
YEAR = 'year'
BILL_TYPE = 'bill_type'
EXPLANATORY_MEMORANDUM = 'explanatory_memorandum'
LOWER_SPONSOR = 'lower_sponsor'
CIRCULATION_PRINT = 'circulation_print'
UPPER_SPONSOR = 'upper_sponsor'

class vic_All_Bills(object):
    _bills_data = []

    def __init__(self):
        try:
            self.scrape_data()
        except Exception as e:
            raise Exception('Error when scraping bills:\n' + e)
    
    def scrape_data(self):
        data_json = json.loads(get(api_url).text)
        results = data_json['results']
        for result in range(len(results)):
            _result = results[result]
            _bill_url = base_url + _result['url'][0][8:]
            _bill_id = _result['_id'][12:-3]
            _bill_status = _result['field_legislation_status'][0]
            _bill_year = _result['legislation_year'][0]
            _bill_title = _result['title'][0]
            _bill_type = _result['type'][0]
            bill_dict = {URL: _bill_url, ID: _bill_id, STATUS: _bill_status, YEAR: _bill_year, SHORT_TITLE: _bill_title, BILL_TYPE: _bill_type}
            self._bills_data.append(bill_dict)

    @property
    def data(self):
        return(self._bills_data)
    
vic_all_bills = vic_All_Bills().data

class vic_Bill(object):
    def __init__(self, input):
        if(isinstance(input, dict)):
            try:
                self.create_vars(input)
            except Exception as e:
                raise Exception('Dict must have correct keys, missing key ' + e)
        else:
            raise ValueError('Input data must be valid vic_Bill dict data...')
    
    def create_vars(self, init_data):
        self._bill_data = init_data
        self.url = init_data[URL]
        self.id = init_data[ID]
        self.status = init_data[STATUS]
        self.year = init_data[YEAR]
        self.short_title = init_data[SHORT_TITLE]
        self.bill_type = init_data[BILL_TYPE]
        try:
            self.bill_soup = BeautifulSoup(get(self.url).text, 'lxml')
        except:
            raise Exception('Unable to scrape ' + self.url)
        
    @property
    def status_report(self):
        try:
            return(self.bill_soup.find('li', {'data-tid': 'Status Report'}).find('a')['href'].strip())
        except:
            return ''

    @property
    def explanatory_memorandum(self):
        try:
            return(self.bill_soup.find('li', {'data-tid': re.compile(r'(Introduction print – Explanatory Memorandum|Circulation print – Explanatory Memorandum)')}).find('a')['href'].strip())
        except:
            return ''

    @property
    def circulation_print(self):
        try:
            return(self.bill_soup.find('li', {'data-tid': 'Circulation print – Bill'}).find('a')['href'].strip())
        except:
            return ''
    
    @property
    def introduction_print(self):
        try:
            return(self.bill_soup.find('li', {'data-tid': 'Introduction print – Bill'}).find('a')['href'].strip())
        except:
            return ''

    @property
    def lower_sponsor(self):
        try:
            return(self.bill_soup.find_all('span', {'class': 'lgs-bill-table__term-title--bold'})[0].text.replace('Hon', '').replace('.', '').strip())
        except:
            return ''

    @property
    def upper_sponsor(self):
        try:
            return(self.bill_soup.find_all('span', {'class': 'lgs-bill-table__term-title--bold'})[-1].text.replace('Hon', '').replace('.', '').strip())
        except:
            return ''

    @property
    def data(self):
        self._bill_data[STATUS_REPORT] = self.status_report
        self._bill_data[EXPLANATORY_MEMORANDUM] = self.explanatory_memorandum
        self._bill_data[LOWER_SPONSOR] = self.lower_sponsor
        self._bill_data[CIRCULATION_PRINT] = self.circulation_print
        return(self._bill_data)