from bs4 import BeautifulSoup
import requests
import datetime

BASE_URL = 'https://www.parliament.wa.gov.au'
URL = f'{BASE_URL}/parliament/bills.nsf/WebAllBills?openview&start=1&count=3000'

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

        for row in rows:
            try:
                bill_link = f'{BASE_URL}{row.a["href"]}'
                bill = {
                    'chamber': self._get_origin_chamber(row.td),
                    'short_title': row.a.text.strip(),
                    'link': bill_link,
                    'ID': bill_link[-32:len(bill_link)]
                }

                self._bills_data.append(bill)

            except Exception as e:
                print(f' --- Bad Data --- \n {e}')

    def _get_origin_chamber(self, data):
        house = data.find('article', class_='la')
        senate = data.find('article', class_='lc')
        return('House' if house else 'Senate' if senate else None)


    @property
    def data(self):
        return(self._bills_data)


all_bills = All_Bills().data


class Bill(object):

    def __init__(self, input):
        pass

    def get_bill_summary(self):
        pass

    def get_sponsor(self):
        pass

    def get_bill_text_links(self):
        pass

    def explanatory_memoranda_links(self):
        pass

    @property
    def summary(self):
        return(self.get_bill_summary())

    @property
    def sponsor(self):
        return(self.get_sponsor())

    @property
    def bill_text_links(self):
        return(self.get_bill_text_links())

    @property
    def explanatory_memoranda_links(self):
        return(self.get_bill_em_links())

    @property
    def data(self):
        pass