from requests import get
import json

bill_list_url = 'https://www.legislation.qld.gov.au/projectdata?ds=OQPC-BrowseDataSource&start=1&count=99999&sortField=sort.title&sortDirection=asc&filterField=TitleWord&expression=Repealed=N%20AND%20PrintType=(%22bill.first%22%20OR%20%22bill.firstnongovintro%22)%20AND%20Title='

class qld_All_Bills(object):
    _bills_data = []

    def __init__(self):
        try:
            self._create_dataset()
        except:
            raise Exception('Error when scraping lists...')

    def _create_dataset(self):
        for number in range(26):
            alpha = chr(97 + number)
            data = json.loads(get(bill_list_url + str(alpha) + '?&subset=browse&collection=&_=1602753113638').text)
            print(data)