import re
import json
from datetime import datetime
from requests import get

url_split_1 = 'https://www.legislation.qld.gov.au/projectdata?ds=OQPC-BrowseDataSource&start=1&count=9999&sortDirection=asc&expression=PrintType%3D(%22bill.first%22+OR+%22bill.firstnongovintro%22)+AND+Year%3D'
url_split_2 = '%3F&subset=browse&collection=&_=1603523834238'
current_year = datetime.today().year

ID = 'id'
URL = 'url'
PRINT_TYPE = 'print_type'
PARLIAMENT_NO = 'parliament_no'
DATE = 'date'
TITLE = 'title'
BILL_NUMBER = 'bill_number'

class qld_All_Bills(object):
    _bills_data = []

    def __init__(self):
        try:
            self._create_dataset()
        except:
            raise Exception('Error when scraping lists...')

    def _create_dataset(self):
        for year in range(current_year - (current_year - 1992), current_year + 1):
            bill_list = json.loads(get(url_split_1 + str(year) + url_split_2).text)
            for bill in bill_list['data']:
                _id = bill['id']['__value__']
                _print_type = bill['print.type']['__value__']
                _url = 'https://www.legislation.qld.gov.au/view/html/' + _print_type + '/' + _id
                _parliament_no = bill['parliament.no']['__value__']
                _date = bill['publication.date'][:-9]
                _title = bill['title']['__value__'].replace('’', '\'').replace('\u2014', ' - ').replace('\u2013', ' - ')
                _bill_number = bill['no']['__value__']
                _bill_dict = {ID: _id, PRINT_TYPE: _print_type, URL: _url, PARLIAMENT_NO: _parliament_no, DATE: _date, TITLE: _title, BILL_NUMBER: _bill_number}
                self._bills_data.append(_bill_dict)

    @property
    def data(self):
        return(self._bills_data)

qld_all_bills = qld_All_Bills().data