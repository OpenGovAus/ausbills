import json

from bs4 import BeautifulSoup, ResultSet
import requests
import datetime

from pymonad.maybe import Maybe, Nothing, Just

from ausbills.json_encoder import AusBillsJsonEncoder
from ausbills.log import get_logger

log = get_logger(__file__)

CHAMBER = "chamber"
SHORT_TITLE = "short_title"
INTRO_HOUSE = "intro_house"
PASSED_HOUSE = "passed_house"
INTRO_SENATE = "intro_senate"
PASSED_SENATE = "passed_senate"
ASSENT_DATE = "assent_date"
URL = "url"
ACT_NO = "act_no"
DOC = "doc"
PDF = "pdf"
HTML = "html"
SUMMARY = "summary"
SPONSOR = "sponsor"
PORTFOLIO = "portfolio"
TEXT_LINK = "text_link"
EM_LINK = "em_link"
ID = "id"
CURRENT_READING = "current_reading"
READINGS = "readings"
bills_legislation_url = "https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page" \
                        "?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726"


class AllBills(object):
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
        markup = requests.get(bills_legislation_url).text
        soup = BeautifulSoup(markup, 'lxml')
        tables = soup.find_all('table')
        trs = tables[table_no].findAll('tr')
        tr = trs.pop(0)
        self.headings = self._get_row_data(tr.findAll('td'))

        for tr in trs:
            row_dict = dict()
            try:
                bill_url_string = str(tr.a['href'])
                row_data = self._get_row_data(tr.findAll('td'))
                row_dict[CHAMBER] = self.chambers[table_no]
                for i in range(len(self.headings)):
                    row_dict[self.headings[i].lower().replace(
                        " ", "_").replace(".", "")] = row_data[i]
                row_dict[URL] = bill_url_string
                row_dict[ID] = bill_url_string.split('?')[-1].split('=')[-1]
                # row_dict[SHORT_TITLE] = row_dict[SHORT_TITLE].replace('\n', '').replace('    ', '').replace(
                #     '\r', '').replace('\u2014\u0080\u0094', ' ').replace('\u00a0', ',').replace('$', 'AUD ')
                row_dict = self._convert_to_datetime(row_dict)
                self._bills_data.append(row_dict)
            except Exception as e:
                print("Bad data", e, ' - ', row_dict[SHORT_TITLE])
                raise e

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
        return row_data

    def _convert_to_datetime(self, bill_dict):
        bill_year = self.this_year

        def to_datetime(indate):
            outdate = None
            if indate is not None:
                if indate != "" and '/' in indate:
                    tempdate = indate.split('/')
                    outdate = datetime.date(
                        bill_year, int(tempdate[1]), int(tempdate[0]))
            return outdate

        for i in range(6):
            year = self.this_year - i
            if str(year) in bill_dict[SHORT_TITLE]:
                bill_year = year
        house_stages = [INTRO_HOUSE, PASSED_HOUSE,
                        INTRO_SENATE, PASSED_SENATE, ASSENT_DATE]
        senate_stages = [INTRO_SENATE, PASSED_SENATE,
                         INTRO_HOUSE, PASSED_HOUSE, ASSENT_DATE]

        for stage in house_stages:
            bill_dict[stage] = to_datetime(bill_dict[stage])

        if bill_dict[CHAMBER] == self.chambers[0]:
            for i in range(len(house_stages) - 1):
                if bill_dict[house_stages[i]] is not None and bill_dict[house_stages[i + 1]] is not None:
                    if bill_dict[house_stages[i]] > bill_dict[house_stages[i + 1]]:
                        d = bill_dict[house_stages[i + 1]]
                        bill_dict[house_stages[i + 1]] = datetime.date(d.year + 1, d.month, d.day)
        elif bill_dict[CHAMBER] == self.chambers[1]:
            for i in range(len(senate_stages) - 1):
                if bill_dict[senate_stages[i]] is not None and bill_dict[senate_stages[i + 1]] is not None:
                    if bill_dict[senate_stages[i]] > bill_dict[senate_stages[i + 1]]:
                        d = bill_dict[senate_stages[i + 1]]
                        bill_dict[senate_stages[i + 1]] = datetime.date(d.year + 1, d.month, d.day)

        return bill_dict

    @property
    def data(self):
        return self._bills_data


_all_bills_global = None


def get_all_bills():
    global _all_bills_global
    if _all_bills_global is None:
        _all_bills_global = AllBills().data
    return _all_bills_global


class Bill:
    _bill_data = dict()

    def __init__(self, bill_dict: dict = None, bill_url: str = None, bill_id: str = None, date_format="YYYY-MM-DD"):
        if all(i is None for i in {bill_id, bill_url, bill_dict}):
            raise ValueError("At least one of the arguments [bill_dict, bill_url, bill_id] must be provided.")

        initial_data = bill_dict
        if initial_data is None:
            try:
                # loop through all bills, if we something matches between the bill's URL or ID and the provided URL or
                # ID, then we have a match. We only care about the first one we find.
                bill = next(filter(
                    lambda b: b is not None,
                    (b if len({b[URL], b[ID]} & {bill_id, bill_url}) != 0 else None for b in get_all_bills())
                ), None)
            except Exception as e:
                log.error(f"Exception finding a matching bill. Exception: {e}")
                raise e
            if bill is None:
                err_source = f'URL: {bill_url}' if bill_url is not None else f'ID: {bill_id}'
                raise ValueError(f"Could not find bill matching {err_source}")
            initial_data = bill

        try:
            self._bill_data = dict(**initial_data)
            self.url = initial_data[URL]
            self.chamber = initial_data[CHAMBER]
            self.short_title = initial_data[SHORT_TITLE]
            self.intro_house = initial_data[INTRO_HOUSE]
            self.passed_house = initial_data[PASSED_HOUSE]
            self.intro_senate = initial_data[INTRO_SENATE]
            self.passed_house = initial_data[PASSED_SENATE]
            self.assent_date = initial_data[ASSENT_DATE]
            self.act_no = initial_data[ACT_NO]
            self.bill_url = requests.get(self.url).text
            self.bill_soup = BeautifulSoup(self.bill_url, 'lxml')
            # date stuff
            self.date_format = date_format
            house_stages = [INTRO_HOUSE, PASSED_HOUSE,
                            INTRO_SENATE, PASSED_SENATE, ASSENT_DATE]
            for stage in house_stages:
                self._bill_data[stage] = self._format_date(self._bill_data[stage])
        except KeyError as e:
            raise KeyError('(class Bill) bill_dict must have all keys. KeyError: ' + str(e))

    def _format_date(self, in_date):
        template = self.date_format
        if in_date is not None and not isinstance(in_date, str):
            out_date = template.replace("YYYY", str(in_date.year))\
                .replace("MM", f"{in_date.month:02d}").replace("DD", f"{in_date.day:02d}")
        else:
            out_date = ''
        return out_date

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return ('<{}.{} : {} object at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.url.split('=')[-1],
            hex(id(self))))

    @property
    def summary(self):
        return self.get_bill_summary()

    @property
    def sponsor(self):
        return self.get_sponsor()

    @property
    def portfolio(self):
        return self.get_portfolio()

    @property
    def bill_text_links(self):
        return self.get_bill_text_links()

    @property
    def explanatory_memoranda_links(self):
        return self.get_bill_em_links()

    def get_bill_summary(self):
        try:
            div = self.bill_soup.find("div", id='main_0_summaryPanel')
        except Exception as e:
            div = None
        if div:
            for span_tag in div.find_all('span'):
                span_tag.unwrap()
            return div.p.text
            summary = div.p.text.replace('\n', '').replace('    ', '').replace(
                '\r', '').replace('\u2014\u0080\u0094', ' ').replace('\u00a0', ',').replace('$', 'AUD ')
        else:
            summary = ""
        return summary

    def get_bill_text_links(self):
        empyt_link_dict = {DOC: '',
                           PDF: '',
                           HTML: ''}
        all_texts = []
        tr_code = 'main_0_textOfBillReadingControl_readingItemRepeater_trFirstReading1_'
        for code_n in range(3):
            try:
                tr = self.bill_soup.find(
                    "tr", id=tr_code + str(code_n))
                if tr is None:
                    continue
                links = []
                cells: ResultSet = tr.find_all('td')
                for a in cells[1].find_all('a') if len(cells) > 1 else list():
                    links.append(a['href'])
                if len(links) >= 3:
                    all_texts.append({DOC: links[0],
                                      PDF: links[1],
                                      HTML: links[2]})
            except Exception as e:
                log.warning(f"Exception during get_bill_text_links: {e}")
        reading_dict = {
            'first': empyt_link_dict.copy(),
            'third': empyt_link_dict.copy(),
            'aspassed': empyt_link_dict.copy(),
        }

        for text in all_texts:
            for typ in reading_dict.keys():
                if typ in text[PDF]:
                    reading_dict[typ] = text
        return reading_dict

    def get_bill_em_links(self) -> dict:
        tr = self.bill_soup.find(
            "tr", id='main_0_explanatoryMemorandaControl_readingItemRepeater_trFirstReading1_0')
        if tr is None:
            return dict()
        links = list(tr.find_all('td')[1].find_all('a'))
        return {DOC: links[0],
                PDF: links[1],
                HTML: links[2]}

    def get_sponsor(self) -> Maybe[str]:
        try:
            tr = self.bill_soup.find("div", id='main_0_billSummary_sponsorPanel')
            if tr is None:
                return ''
            return Just(tr.find('dd').text).value
            # return tr.find_all('dd')[0].text.replace('  ', '').replace('\n', '').replace('\r', '')
        except Exception as e:
            log.warning(e)
            return ''
            

    def get_portfolio(self) -> Maybe[str]:
        try:
            tr = self.bill_soup.find("div", id='main_0_billSummary_portfolioPanel')
            return '' if tr is None else Just(tr.find_all('dd')[0].text).value
            # return tr.find_all('dd')[0].text.replace('  ', '').replace('\n', '').replace('\r', '')
        except Exception as e:
            log.warning(e)
            return ''

    @property
    def data(self):
        self._bill_data[CURRENT_READING] = 'first'
        text_type = [DOC, PDF, HTML]
        self._bill_data[SUMMARY] = self.summary
        self._bill_data[SPONSOR] = self.sponsor
        self._bill_data[PORTFOLIO] = self.portfolio
        self._bill_data[READINGS] = self.bill_text_links
        for TEXT in text_type:
            for reading in ['first', 'third', 'aspassed']:
                if self.bill_text_links[reading][TEXT] != '':
                    self._bill_data[TEXT_LINK + '_' + TEXT] = self.bill_text_links[reading][TEXT]
                    self._bill_data[CURRENT_READING] = reading
            self._bill_data[EM_LINK + '_' + TEXT] = self.explanatory_memoranda_links[TEXT]
        return self._bill_data

    def to_json(self) -> str:
        return json.dumps(self._bill_data, cls=AusBillsJsonEncoder)
