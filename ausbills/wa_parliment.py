from bs4 import BeautifulSoup
import requests
import datetime
import re

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
                    'title': row.a.text.strip(),
                    'origin': self._get_origin_chamber(row.td),
                    'link': bill_link,
                    'id': bill_link[-32:len(bill_link)]
                }

                self._bills_data.append(bill)

            except Exception as e:
                print(f' --- Bad Data --- \n {e}')

    def _get_origin_chamber(self, data):
        assembly = data.find('article', class_='la')
        council = data.find('article', class_='lc')
        return('Legislative Assembly' if assembly else 'Legislative Council' if council else None)


    @property
    def data(self):
        return(self._bills_data)


all_bills = All_Bills().data


class Bill(object):

    def __init__(self, bill):
        self.url = bill['link']
        self.page = requests.get(self.url, verify=False)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

    @property
    def summary(self):
        return(self.soup.findAll('td')[4].text)

    @property
    def sponsor(self):
        sponsor = self.soup.find(text=re.compile('Private Members Bill introduced by'))
        return sponsor.replace('Private Members Bill introduced by ', '') if sponsor else None

    @property
    def bill_text_links(self):
        links = {'as_introduced': BASE_URL + self.soup.find(text=re.compile('Download the Bill as Introduced')).parent.get('href')}
        return(links)

    @property
    def explanatory_memoranda_links(self):
        pass

    @property
    def number(self):
        return self.soup.find(text=re.compile('Bill No.')).parent.parent.findNext('td').contents[0]

    @property
    def data(self):
        pass