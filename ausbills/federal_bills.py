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


def get_house_bills():
    LOWER_HOUSE_BILLS = []
    try:
        website_url = requests.get(bills_legislation_url).text
        soup = BeautifulSoup(website_url, 'lxml')
        tables = soup.find_all('table')
        trs = tables[0].findAll('tr')
        trs.pop(0)

        for tr in trs:
            bill_url_string = str(tr.a['href'])
            title = get_table_data(tr.findAll('td'), 0)
            intro_house = get_table_data(tr.findAll('td'), 1)
            passed_house = get_table_data(tr.findAll('td'), 2)
            intro_senate = get_table_data(tr.findAll('td'), 3)
            passed_senate = get_table_data(tr.findAll('td'), 4)
            assent_date = get_table_data(tr.findAll('td'), 5)
            act_no = get_table_data(tr.findAll('td'), 6)
            bill_url = requests.get(bill_url_string).text
            bill_soup = BeautifulSoup(bill_url, 'lxml')
            div = bill_soup.find("div", id='main_0_summaryPanel')
            if div:
                for span_tag in div.find_all('span'):
                    span_tag.unwrap()
                summary = div.p.text.replace('\n', '').replace('    ', '')
            else:
                summary = ""
            LOWER_HOUSE_BILLS.append(
                {
                    CHAMBER: "House",
                    SHORT_TITLE: title,
                    INTRO_HOUSE: intro_house,
                    PASSED_HOUSE: passed_house,
                    INTRO_SENATE: intro_senate,
                    PASSED_SENATE: passed_senate,
                    ASSENT_DATE: assent_date,
                    SUMMARY: summary,
                    URL: bill_url_string,
                    ACT_NO: act_no})

        return(LOWER_HOUSE_BILLS)
    except Exception as e:
        print("Link broken:")
        print(e)
        return(None)


def get_senate_bills():
    UPPER_HOUSE_BILLS = []
    try:
        website_url = requests.get(bills_legislation_url).text
        soup = BeautifulSoup(website_url, 'lxml')
        tables = soup.find_all('table')
        trs = tables[1].findAll('tr')
        trs.pop(0)

        for tr in trs:
            bill_url_string = str(tr.a['href'])
            title = get_table_data(tr.findAll('td'), 0)
            intro_house = get_table_data(tr.findAll('td'), 3)
            passed_house = get_table_data(tr.findAll('td'), 4)
            intro_senate = get_table_data(tr.findAll('td'), 1)
            passed_senate = get_table_data(tr.findAll('td'), 2)
            assent_date = get_table_data(tr.findAll('td'), 5)
            act_no = get_table_data(tr.findAll('td'), 6)
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
            UPPER_HOUSE_BILLS.append(
                {
                    CHAMBER: "Senate",
                    SHORT_TITLE: title,
                    INTRO_HOUSE: intro_house,
                    PASSED_HOUSE: passed_house,
                    INTRO_SENATE: intro_senate,
                    PASSED_SENATE: passed_senate,
                    ASSENT_DATE: assent_date,
                    SUMMARY: summary,
                    URL: bill_url_string,
                    ACT_NO: act_no})

        return(UPPER_HOUSE_BILLS)
    except Exception as e:
        print("Link broken:")
        print(e)
        return(None)


# d = get_house_bills()
# df = pd.DataFrame(d)
# df.to_csv("lowerbills.csv")
