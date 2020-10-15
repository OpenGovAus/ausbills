import datetime
from requests import get
from bs4 import BeautifulSoup
import io

URL = 'url'
TITLE = 'title'
STATUS = 'status'
ORIGIN = 'origin'
ACT_NO = 'act_no'
YEAR = 'year'
TYPE = 'type'

base_url = 'https://www.parliament.nsw.gov.au/bills/pages/all-bills-1997.aspx?letter='

class nsw_All_Bills(object):
    _bills_data = []
    def __init__(self):
        self._create_dataset()

    def _create_dataset(self):
        _bill_titles = []
        _bill_origin = []
        _bill_type = []
        _bill_status = []
        _bill_urls = []
        bill_statuses = ['Lapsed', 'Assented', 'Withdrawn', 'Negatived', 'Discharged']
        for number in range(26):
            alpha = chr(65 + number)
            soup = BeautifulSoup(get(base_url + alpha).text, 'lxml')
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
                
                base_data = row.find('span', {'class': 'filesize filesize-first'})
                try:
                    status = str(''.join(base_data.find('br').previous_siblings)[22:-37])
                    if(status in bill_statuses):
                        _bill_status.append(status)
                    else:
                        _bill_status.append('')
                except:
                    _bill_status.append('')

                try:
                    _bill_type.append(str(''.join(base_data.find('br').next_siblings)[36:-36]))
                except:
                    _bill_type.append('')
         
        for bill in range(len(_bill_titles)):
            _bill_dict = {TITLE: _bill_titles[bill], STATUS: _bill_status[bill], URL: _bill_urls[bill], TYPE: _bill_type[bill], ORIGIN: _bill_origin[bill]}
            self._bills_data.append(_bill_dict)
    
    @property
    def data(self):
        return(self._bills_data)

nsw_all_bills = nsw_All_Bills().data