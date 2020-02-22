from bs4 import BeautifulSoup
import requests
import pandas as pd
import asyncio


CHAMBER = "CHAMBER"
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


def get_table_data(tds, col):
    try:
        if tds[col].span:
            return(tds[col].span.string)
        else:
            return("")
    except Exception as e:
        print(e)
        return("")


def get_bill_summary(bill_url_string):
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


def get_bill_text_links(bill_url_string):
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


def get_bill_em_links(bill_url_string):
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


def get_sponsor(bill_url_string):
    try:
        bill_url = requests.get(bill_url_string).text
        bill_soup = BeautifulSoup(bill_url, 'lxml')
        tr = bill_soup.find("div", id='main_0_billSummary_sponsorPanel')
        return(tr.find_all('dd')[0].text.replace(' ', '').replace('\n', ''))
    except Exception as e:
        return('')


class lower_house_bills(object):
    LHB = []
    def __init__(self):

        try:
            website_url = requests.get(bills_legislation_url).text
            soup = BeautifulSoup(website_url, 'lxml')
            tables = soup.find_all('table')
            trs = tables[0].findAll('tr')
            trs.pop(0)

            for tr in trs:
                try:
                    bill_url_string = str(tr.a['href'])
                    title = get_table_data(tr.findAll('td'), 0)
                    intro_house = get_table_data(tr.findAll('td'), 1)
                    passed_house = get_table_data(tr.findAll('td'), 2)
                    intro_senate = get_table_data(tr.findAll('td'), 3)
                    passed_senate = get_table_data(tr.findAll('td'), 4)
                    assent_date = get_table_data(tr.findAll('td'), 5)
                    act_no = get_table_data(tr.findAll('td'), 6)
                    self.LHB.append(
                        {
                            CHAMBER: "House",
                            SHORT_TITLE: title,
                            INTRO_HOUSE: intro_house,
                            PASSED_HOUSE: passed_house,
                            INTRO_SENATE: intro_senate,
                            PASSED_SENATE: passed_senate,
                            ASSENT_DATE: assent_date,
                            URL: bill_url_string,
                            ACT_NO: act_no})
                except Exception as e:
                    print("Link broken:")

        except Exception as e:
            print("Link broken:")
            print(e)
            print(title)

    @property
    def data(self):
        return(self.LHB)


class upper_house_bills(object):
    UHB = []

    def __init__(self):
        try:
            website_url = requests.get(bills_legislation_url).text
            soup = BeautifulSoup(website_url, 'lxml')
            tables = soup.find_all('table')
            trs = tables[1].findAll('tr')
            trs.pop(0)

            for tr in trs:
                try:
                    bill_url_string = str(tr.a['href'])
                    title = get_table_data(tr.findAll('td'), 0)
                    intro_house = get_table_data(tr.findAll('td'), 3)
                    passed_house = get_table_data(tr.findAll('td'), 4)
                    intro_senate = get_table_data(tr.findAll('td'), 1)
                    passed_senate = get_table_data(tr.findAll('td'), 2)
                    assent_date = get_table_data(tr.findAll('td'), 5)
                    act_no = get_table_data(tr.findAll('td'), 6)
                    self.UHB.append(
                        {
                            CHAMBER: "Senate",
                            SHORT_TITLE: title,
                            INTRO_HOUSE: intro_house,
                            PASSED_HOUSE: passed_house,
                            INTRO_SENATE: intro_senate,
                            PASSED_SENATE: passed_senate,
                            ASSENT_DATE: assent_date,
                            URL: bill_url_string,
                            ACT_NO: act_no})
                except Exception as e:
                    print("Bad data")

        except Exception as e:
            print("Link broken:")
            print(e)
            print(title)

    @property
    def data(self):
        return(self.UHB)


lhb = lower_house_bills()
uhb = upper_house_bills()

print(lhb.data[2])
print()
print(uhb.data[2])
print()
print(get_sponsor('https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Search_Results/Result?bId=r6356'))
