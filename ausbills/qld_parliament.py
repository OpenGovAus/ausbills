from requests import get
import json

bill_list_url = 'https://www.legislation.qld.gov.au/projectdata?ds=OQPC-BrowseDataSource&start=1&count=9999&sortField=sort.title&sortDirection=asc&expression=Repealed%3DN+AND+PrintType%3D(%22bill.first%22+OR+%22bill.firstnongovintro%22)+AND+Title%3Da%20OR%20b%3F&subset=browse&collection=&_=1602801890379'

class qld_All_Bills(object):
    _bills_data = []

    def __init__(self):
        try:
            self._create_dataset()
        except:
            raise Exception('Error when scraping lists...')

    def _create_dataset(self):
        data = json.loads(get(bill_list_url).text)
        _bills_data = data
        for bill in range(len(data['data'])):
            if 'bill-' in data['data'][bill]['id']['__value__']:
                print('https://www.legislation.qld.gov.au/view/html/bill.first/' + data['data'][bill]['id']['__value__'])

    @property
    def data(self):
        return(self._bills_data)

qld_all_bills = qld_All_Bills().data