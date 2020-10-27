import json
from requests import get
from bs4 import BeautifulSoup

base_url = 'https://www.legislation.vic.gov.au/'
api_url = base_url + 'app/api/search/title_content?from=0&size=9999&includeFilters[0][prefix][title_az]=&includeFilters[1][term][type]=bill&includeFields[0]=title&includeFields[1]=field_in_force_former_title&includeFields[2]=url&includeFields[3]=type&includeFields[4]=legislation_type&includeFields[5]=field_act_sr_number&includeFields[6]=legislation_year&includeFields[7]=field_act_sr_status_date&includeFields[8]=field_legislation_status&includeFields[9]=field_bill_pre_2004&includeFields[10]=field_bill_parliament_term&sort[0][_score]=desc&sort[1][title_az]=asc&aggregations[legislation_year][terms][field]=legislation_year&aggregations[legislation_year][terms][order][_key]=desc&aggregations[legislation_year][terms][size]=250&aggregations[field_legislation_status][terms][field]=field_legislation_status&aggregations[field_legislation_status][terms][order][_key]=asc&aggregations[field_legislation_status][terms][size]=250'

URL = 'url'
ID = 'id'
SHORT_TITLE = 'short_title'
STATUS = 'status'
YEAR = 'year'
BILL_TYPE = 'bill_type'

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