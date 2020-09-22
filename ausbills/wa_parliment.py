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
        self.bill = bill
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
    def dates(self):
        dates = {}

        # Get dates related to each chamber
        tables = []
        LA_table = self.soup.find('table', class_='bil_table_LA')
        LC_table = self.soup.find('table', class_='bil_table_LC')

        # We don't want to append None and cause the for loop to operate on this
        if LA_table:
            tables.append(LA_table)

        if LC_table:
            tables.append(LC_table)

        for table in tables:
            chamber = table.find('td').contents[0].replace(' ', '_').lower()
            dates[chamber] = {}

            rows = table.find_all('tr')
            rows.pop(0)

            for row in rows:
                col = row.find_all('td')
                status = col[0].contents[0].replace(' ', '_').lower()
                date = re.sub('[^a-zA-Z0-9 ]', '', col[1].contents[0])
                dates[chamber][status] = date

        # Get assent date and act number or False
        dates['assent'] = self.assent

        return(dates)

    @property
    def bill_number(self):
        return self.soup.find(text=re.compile('Bill No.')).parent.parent.findNext('td').contents[0]

    @property
    def assent(self):
        assent = {}

        assent_text = self.soup.find(text=re.compile('Royal Assent given'))

        if assent_text:
            assent_text = assent_text.split('Royal Assent given')
            # We use strip() here as where the date and act are in the text is varible,
            # so we cast a larger range and trim any white space that we get.
            assent['date'] = assent_text[1][0:12].strip()
            assent['act_number'] = assent_text[1][23:26].strip()

            return(assent)

        return False

    @property
    def data(self):
        self.bill['bill_number'] = self.bill_number
        self.bill['summary'] = self.summary
        self.bill['sponsor'] = self.sponsor
        self.bill['readings'] = self.bill_text_links
        self.bill['dates'] = self.dates
        return(self.bill)