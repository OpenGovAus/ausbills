from bs4 import BeautifulSoup
import requests
import datetime

URL = "https://www.parliament.wa.gov.au/parliament/bills.nsf/WebAllBills?openview&start=1&count=3000"

class All_Bills(object):
    _bills_data = []

    def __init__(self):
        self._build_dataset()

    def _build_dataset(self):
        try:
            self._scrape_data()

        except Exception as e:
            print(f'Link broken: {e}')

    def _scrape_data(self):
        page = requests.get(URL, verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table')
        rows = table.findAll('tr')
        # Remove table heading
        rows.pop(0)

        print(rows)

    @property
    def data(self):
        return(self._bills_data)


all_bills = All_Bills().data


class Bill(object):

    def __init__(self, input):
        pass
