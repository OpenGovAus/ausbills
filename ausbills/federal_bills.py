from bs4 import BeautifulSoup
import requests
import pandas as pd
import asyncio
import datetime


CHAMBER = "Chamber"
SHORT_TITLE = "Short Title"
INTRO_HOUSE = "Intro House"
PASSED_HOUSE = "Passed House"
INTRO_SENATE = "Intro Senate"
PASSED_SENATE = "Passed Senate"
ASSENT_DATE = "Assent Date"
URL = "URL"
ACT_NO = "Act No."
SUMMARY = "Summary"

bills_legislation_url = "https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726"


class Federal_Bills(object):
    _bills_data = []
    chambers = ["House", "Senate"]
    this_year = datetime.datetime.now().year

    def __init__(self):
        self._build_dataset()

    def _build_dataset(self):
        try:
            for i in range(2):
                self._scrape_data(i)
        except Exception as e:
            print("Link broken:")
            print(e)

    def _scrape_data(self, table_no):
        website_url = requests.get(bills_legislation_url).text
        soup = BeautifulSoup(website_url, 'lxml')
        tables = soup.find_all('table')
        trs = tables[table_no].findAll('tr')
        tr = trs.pop(0)
        self.headings = self._get_row_data(tr.findAll('td'))

        for tr in trs:
            try:
                bill_url_string = str(tr.a['href'])
                row_data = self._get_row_data(tr.findAll('td'))
                row_dict = {CHAMBER: self.chambers[table_no]}
                for i in range(len(self.headings)):
                    row_dict[self.headings[i]] = row_data[i]
                row_dict[URL] = bill_url_string
                row_dict = self._convert_to_datetime(row_dict)
                self._bills_data.append(row_dict)
            except Exception as e:
                print("Bad data", e)

    def _get_row_data(self, tds):
        row_data = []
        for col in range(7):
            try:
                if tds[col].span:
                    row_data.append(tds[col].span.string)
                else:
                    row_data.append("")
            except Exception as e:
                print(e)
                row_data.append("")
        return(row_data)

    def _convert_to_datetime(self, bill_dict):
        bill_year = self.this_year
        for i in range(6):
            year = self.this_year - i
            if str(year) in bill_dict[SHORT_TITLE]:
                bill_year = year
        if bill_dict[INTRO_HOUSE] != "":
            intro_house = bill_dict[INTRO_HOUSE].split('/')
            bill_dict[INTRO_HOUSE] = datetime.date(
                bill_year, int(intro_house[1]), int(intro_house[0]))
        else:
            bill_dict[INTRO_HOUSE] = None

        passed_house = bill_dict[PASSED_HOUSE].split('/')
        into_senaet = bill_dict[INTRO_SENATE].split('/')
        passed_senate = bill_dict[PASSED_SENATE].split('/')
        print(bill_year, bill_dict[INTRO_HOUSE], bill_dict[SHORT_TITLE])
        return(bill_dict)

    @property
    def data(self):
        return(self._bills_data)


class Bill(object):

    def __init__(self, initial_data):
        self.initial_data = initial_data

    def get_bill_summary(self, bill_url_string):
        try:
            bill_url = requests.get(bill_url_string).text
            bill_soup = BeautifulSoup(bill_url, 'lxml')
            div = bill_soup.find("div", id='main_0_summaryPanel')
        except Exception as e:
            div = None
        if div:
            for span_tag in div.find_all('span'):
                span_tag.unwrap()
            summary = div.p.text.replace('\n', '').replace('    ', '')
        else:
            summary = ""
        return(summary)

    def get_bill_text_links(self, bill_url_string):
        try:
            bill_url = requests.get(bill_url_string).text
            bill_soup = BeautifulSoup(bill_url, 'lxml')
            tr = bill_soup.find(
                "tr", id='main_0_textOfBillReadingControl_readingItemRepeater_trFirstReading1_0')
            links = []
            for a in tr.find_all('td')[1].find_all('a'):
                links.append(a['href'])
            return(links)
        except Exception as e:
            return([])

    def get_bill_em_links(self, bill_url_string):
        try:
            bill_url = requests.get(bill_url_string).text
            bill_soup = BeautifulSoup(bill_url, 'lxml')
            tr = bill_soup.find(
                "tr", id='main_0_explanatoryMemorandaControl_readingItemRepeater_trFirstReading1_0')
            links = []
            for a in tr.find_all('td')[1].find_all('a'):
                links.append(a['href'])
            return(links)
        except Exception as e:
            return([])

    def get_sponsor(self, bill_url_string):
        try:
            bill_url = requests.get(bill_url_string).text
            bill_soup = BeautifulSoup(bill_url, 'lxml')
            tr = bill_soup.find("div", id='main_0_billSummary_sponsorPanel')
            return(tr.find_all('dd')[0].text.replace(' ', '').replace('\n', ''))
        except Exception as e:
            return('')

# for testing


fb = Federal_Bills()

print(fb.data[3])
print()
url = fb.data[3]["URL"]
print(url)
print()
