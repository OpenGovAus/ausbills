import re
import json
from bs4 import BeautifulSoup
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
SERIES_ID = 'series_id' #  These 2 variables (series/desc)_id are used by the QLD bill API to deliver specific HTML fragments.
DESC_ID = 'desc_id'     #  Without these, we'd need some funky JavaScript interpretation, and you know I'm too lazy to write that. 
EXPLANATORY_NOTE = 'explanatory_note'
RENDITIONS = 'renditions'
SPONSOR = 'sponsor'
LONG_TITLE = 'long_title'
BILL_TYPE = 'bill_type'

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
                _series_id = bill['version.series.id']['__value__']
                _desc_id = bill['version.desc.id']['__value__']
                _bill_dict = {ID: _id, PRINT_TYPE: _print_type, URL: _url, PARLIAMENT_NO: _parliament_no, DATE: _date, TITLE: _title, BILL_NUMBER: _bill_number, DESC_ID: _desc_id, SERIES_ID: _series_id}
                self._bills_data.append(_bill_dict)

    @property
    def data(self):
        return(self._bills_data)

qld_all_bills = qld_All_Bills().data

class qld_Bill(object):
    _all_bills = qld_all_bills

    def __init__(self, input):
        if(isinstance(input, dict)):
            try:
                self.create_vars(input)
            except Exception as e:
                raise Exception('Dict must have the correct keys. Missing key '
                                + str(e))
        else:
            raise TypeError('Input must be a valid QLD bill...')

    def create_vars(self, init_data):
        self._bill_data = init_data
        self.url = init_data[URL]
        self.id = init_data[ID]
        self.short_title = init_data[TITLE]
        self.date = init_data[DATE]
        self.print_type = init_data[PRINT_TYPE]
        self.parliament_no = init_data[PARLIAMENT_NO]
        self.bill_number = init_data[BILL_NUMBER]
        self.series_id = init_data[SERIES_ID]
        self.desc_id = init_data[DESC_ID]
        try:
            json_url = 'https://www.legislation.qld.gov.au/projectdata?ds=OQPC-TocDataSource&expression=view%2Fhtml%2Fbill.first%2F' + self.id + '&subset=search'
            self.bill_json = json.loads(get(json_url).text)
        except:
            raise Exception('Unable to scrape, ' + self.url)
        try:
            history_url = 'https://www.legislation.qld.gov.au/view/html/' + self.print_type + '/' + self.id + '/lh'
            self.bill_history_soup = BeautifulSoup(get(history_url).text, 'lxml')
        except:
            raise Exception('Unable to scrape bill history, ' + self.url)

    @property
    def renditions(self):
        try:
            renditions = []
            rendition_info = self.bill_json['version.info']
            rendition_info.pop(0)
            for version in rendition_info:
                rendition_dict = {ID: version['id']['__value__'], PRINT_TYPE: version['print.type']['__value__'], DATE: version['publication.date']}
                renditions.append(rendition_dict)
            return(renditions)
        except:
            return []

    @property
    def sponsor(self):
        try:
            bill_sponsor = self.bill_json['member.id']['__value__']
            return(bill_sponsor)
        except:
            return ''

    @property
    def long_title(self):
        try:
            html_data = BeautifulSoup(json.loads(get('https://www.legislation.qld.gov.au/projectdata?ds=OQPC-FragViewDataSource&expression=VersionDescId%3D%22' + self.desc_id + '%22+AND+VersionSeriesId%3D%22' + self.series_id + '%22+AND+PrintType%3D%22bill.first%22+AND+Id_p%3D%22frnt-lt%22%7C%7Cas.made&collection=OQPC.fragment&subset=search').text)['frag.html'], 'lxml')
            title_val = html_data.text.replace('\n', '').replace('\t', '')
            return(title_val)
        except:
            return ''

    @property
    def bill_type(self):
        try:
            div = self.bill_history_soup.find('div', {'id': 'parsewrapper'})
            table = div.find('table', {'class': 'table table-striped'})
            _type = table.find('tr').text.replace('\n', '')
            return(_type)
        except:
            return ''

    @property
    def explanatory_note(self):
        try:
            div = self.bill_history_soup.find('div', {'id': 'parsewrapper'})
            table = div.find('table', {'class': 'table table-striped'})
            td = table.find_all('tr')[1].find_all('td')[1]
            for paragraph in td.find_all('a'):
                if 'Explanatory Note' in paragraph.text.replace('\n', ' '):
                    return('https://www.legislation.qld.gov.au' + paragraph['href'])
            return ''
        except:
            return ''
    
    @property
    def data(self):
        self._bill_data[EXPLANATORY_NOTE] = self.explanatory_note
        self._bill_data[SPONSOR] = self.sponsor
        self._bill_data[RENDITIONS] = self.renditions
        self._bill_data[LONG_TITLE] = self.renditions
        self._bill_data[BILL_TYPE] = self.bill_type
        return(self._bill_data)