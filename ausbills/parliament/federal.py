import json
import datetime
import requests


from typing import List, Dict
from pymonad.maybe import Maybe
from dataclasses import dataclass
from bs4 import BeautifulSoup, ResultSet


from ausbills.util import BillExtractor
from ausbills.util.consts import *

from ausbills.types import BillProgress, ChamberProgress, Parliament, Timestamp
from ausbills.models import BillMeta, Bill
from ausbills.json_encoder import AusBillsJsonEncoder
from ausbills.log import get_logger


log = get_logger(__file__)


DATE_FMT = "%{0}d/%{0}m/%y".format('')

bills_legislation_url = "https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page" \
                        "?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726"

this_year = datetime.datetime.now().year
chambers = ["House", "Senate"]


class AllBills(object):
    this_year = datetime.datetime.now().year
    _bills_data = []
    chambers = ["House", "Senate"]

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
                row_dict[SHORT_TITLE] = row_dict[SHORT_TITLE].replace('\n', '').replace('    ', '').replace('\r', '').replace('\u00a0', ',').replace(
                    '$', 'AUD ').replace('ia\u2014', 'ia\'').replace('rans\u2014', 'rans\'').replace('\x80', '').replace('\x99', '').replace('\x94', '')
                row_dict[SHORT_TITLE] = row_dict[SHORT_TITLE].replace(
                    '\u2014', '-')
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
                # print(e)
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
                        bill_dict[house_stages[i + 1]
                                  ] = datetime.date(d.year + 1, d.month, d.day)
        elif bill_dict[CHAMBER] == self.chambers[1]:
            for i in range(len(senate_stages) - 1):
                if bill_dict[senate_stages[i]] is not None and bill_dict[senate_stages[i + 1]] is not None:
                    if bill_dict[senate_stages[i]] > bill_dict[senate_stages[i + 1]]:
                        d = bill_dict[senate_stages[i + 1]]
                        bill_dict[senate_stages[i + 1]
                                  ] = datetime.date(d.year + 1, d.month, d.day)

        return bill_dict

    @property
    def data(self):
        return self._bills_data


_all_bills_global = None


def get_all_bills():
    log.warning("get_all_bills is depreciated")
    global _all_bills_global
    if _all_bills_global is None:
        _all_bills_global = AllBills().data
    return _all_bills_global


@dataclass
class BillMetaFed(BillMeta):
    house: str
    id: str
    intro_house: Timestamp
    passed_house: Timestamp
    intro_senate: Timestamp
    passed_senate: Timestamp
    assent_date: Timestamp
    act_no: int


@dataclass
class BillFed(Bill, BillMetaFed):
    text_link: str
    summary: str
    sponsor: str
    portfolio: str
    bill_em_links: List[Dict]


def dt_to_str(in_date, template="YYYY-MM-DD"):
    if in_date is not None and not isinstance(in_date, str):
        out_date = template.replace("YYYY", str(in_date.year))\
            .replace("MM", f"{in_date.month:02d}").replace("DD", f"{in_date.day:02d}")
    else:
        out_date = ''
    return out_date


def get_bills_metadata() -> List[BillMetaFed]:
    """Gets a list of all the federal bills metadata

    Returns:
        List[BillMetaFed]: BillMetaFed is to be used with get_bill(BillMetaFed) to get detailed data
    """
    _all_bills = AllBills().data
    _bill_meta_list = []
    for bill_dict in _all_bills:
        house = "LOWER" if bill_dict[CHAMBER] == "house" else "UPPER"
        bill_meta = BillMetaFed(
            parliament=Parliament.FEDERAL.value,
            house=house,
            id=bill_dict[ID],
            title=bill_dict[SHORT_TITLE],
            link=bill_dict[URL],
            intro_house=dt_to_str(bill_dict[INTRO_HOUSE]),
            passed_house=dt_to_str(bill_dict[PASSED_HOUSE]),
            intro_senate=dt_to_str(bill_dict[INTRO_SENATE]),
            passed_senate=dt_to_str(bill_dict[PASSED_SENATE]),
            assent_date=dt_to_str(bill_dict[ASSENT_DATE]),
            act_no=bill_dict[ACT_NO]
        )
        _bill_meta_list.append(bill_meta)
    return(_bill_meta_list)


class BillFedHelper(BillExtractor):
    _bill_data = dict()

    def __init__(self, bill_meta: BillMetaFed):
        self.url = bill_meta.link
        self.chamber = bill_meta.house
        self.short_title = bill_meta.title
        self.intro_house = bill_meta.intro_house
        self.passed_house = bill_meta.passed_house
        self.intro_senate = bill_meta.intro_senate
        self.passed_senate = bill_meta.passed_senate
        self.assent_date = bill_meta.assent_date
        self.act_no = bill_meta.act_no
        self.bill_url = requests.get(self.url).text
        self.bill_soup = self._download_html(self.url)

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
            summary = div.p.text.replace('\n', '').replace('    ', '').replace(
                '\r', '').replace('\u2014\u0080\u0094', ' ').replace('\u00a0', ',').replace('$', 'AUD ').strip()
        else:
            summary = ""
        return summary

    def get_bill_text_links(self):
        empyt_link_dict = {DOC: '',
                           PDF: '',
                           HTML: ''}
        all_texts = []
        tr_code = 'main_0_textOfBillReadingControl_readingItemRepeater_trFirstReading1_0'
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

    def get_bill_em_links(self) -> List[Dict[str, str]]:
        tr = self.bill_soup.find(
            "tr", id='main_0_explanatoryMemorandaControl_readingItemRepeater_trFirstReading1_0')
        if tr is None:
            return []
        links = list(tr.find_all('td')[1].find_all('a'))
        return [
            {
                API_ID: 0,
                URL: links[1]['href'],
            }
        ]
        

    def get_sponsor(self) -> Maybe[str]:
        try:
            tr = self.bill_soup.find(
                "div", id='main_0_billSummary_sponsorPanel')
            if tr is None:
                return ''
            # return Just(tr.find('dd').text).value
            return tr.find_all('dd')[0].text.replace('  ', '').replace('\n', '').replace('\r', '')
        except Exception as e:
            log.warning(e)
            return ''

    def get_portfolio(self) -> Maybe[str]:
        try:
            tr = self.bill_soup.find(
                "div", id='main_0_billSummary_portfolioPanel')
            # return '' if tr is None else Just(tr.find_all('dd')[0].text).value
            return tr.find_all('dd')[0].text.replace('  ', '').replace('\n', '').replace('\r', '')
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
                    self._bill_data[TEXT_LINK + '_' +
                                    TEXT] = self.bill_text_links[reading][TEXT]
                    self._bill_data[CURRENT_READING] = reading
            try:
                self._bill_data[EM_LINK + '_' +
                                TEXT] = self.explanatory_memoranda_links[TEXT]
            except Exception:
                self._bill_data[EM_LINK + '_' +
                                TEXT] = ''
        return self._bill_data

    def to_json(self) -> str:
        return json.dumps(self._bill_data, cls=AusBillsJsonEncoder)

    @property
    def chamber_progress(self):
        return self.get_chamber_progress()
    
    def get_chamber_progress(self):
        if len(self.passed_senate) > 0 and len(self.passed_house) > 0:
            _prog_dict = {
                BillProgress.FIRST.value: True,
                BillProgress.SECOND.value: True,
                BillProgress.ASSENTED.value: True
            }
        else:
            _prog_dict = None
        _house_timestamp = 0
        _senate_timestamp = 0
        if len(self.intro_house) > 0:
            _house_timestamp = self._get_timestamp(self.intro_house, '%Y-%m-%d')
        if len(self.intro_senate) > 0:
            _senate_timestamp = self._get_timestamp(self.intro_senate, '%Y-%m-%d')
        
        if _house_timestamp > _senate_timestamp:
            _chamber = 'House of Representatives'
            if _prog_dict is None:
                _prog_dict = {BillProgress.FIRST.value: True, BillProgress.SECOND.value: True, BillProgress.ASSENTED.value: False}
                if _senate_timestamp == 0:
                    _prog_dict[BillProgress.SECOND.value] = False
        else:
            _chamber = 'Senate'
            if _prog_dict is None:
                _prog_dict = {BillProgress.FIRST.value: True, BillProgress.SECOND.value: True, BillProgress.ASSENTED.value: False}
                if _house_timestamp == 0:
                    _prog_dict[BillProgress.FIRST.value] = False
        
        stage_text = self.bill_soup.find_all('th', string=_chamber)[0].parent.parent.parent.find('tbody').find_all('tr')[-1].text.strip()
        if 'First' in stage_text:
            _reading = ChamberProgress.FIRST_READING.value
        elif 'Second' in stage_text or 'Referred' in stage_text or 'Restored' in stage_text:
            _reading = ChamberProgress.SECOND_READING.value
        elif 'Third' in stage_text:
            _reading = ChamberProgress.THIRD_READING.value
        else:
            log.warning(
                'Could not identify reading stage, using second; \n' + stage_text)
            _reading = ChamberProgress.SECOND_READING.value

        return [_reading, _prog_dict]


def get_bill(bill_meta: BillMetaFed) -> BillFed:
    """Uses the bill metadata to scrape the rest of the bill info

    Args:
        bill_meta (BillMetaFed): Federal specific BillMeta

    Returns:
        BillFed: Including the federal specific information
        Note: use BillFed.asDict() and BillFed.asJson() to get the data
    """
    def stupid_timestamp_thing(input_date):
        try:
            return int(datetime.datetime.strptime(input_date, '%Y-%m-%d').timestamp())
        except ValueError:
            return ''
    fed_helper: BillFedHelper = BillFedHelper(bill_meta)
    progdata = fed_helper.chamber_progress
    bill_fed = BillFed(
        title=bill_meta.title,
        link=bill_meta.link,
        sponsor=fed_helper.sponsor
                if fed_helper.sponsor != "" else fed_helper.portfolio,
        text_link=fed_helper.data[CURRENT_READING],
        # From bill_meta
        parliament=str(bill_meta.parliament),
        house=bill_meta.house,
        id=bill_meta.id,
        intro_house=stupid_timestamp_thing(bill_meta.intro_house),
        passed_house=stupid_timestamp_thing(bill_meta.passed_house),
        intro_senate=stupid_timestamp_thing(bill_meta.intro_senate),
        passed_senate=stupid_timestamp_thing(bill_meta.passed_senate),
        assent_date=stupid_timestamp_thing(bill_meta.assent_date),
        act_no=bill_meta.act_no,
        # From fed_helper
        summary=fed_helper.summary,
        portfolio=fed_helper.portfolio,
        bill_text_links=fed_helper.bill_text_links,
        bill_em_links=fed_helper.explanatory_memoranda_links,
        progress=progdata[1],
        chamber_progress=progdata[0],
    )
    return(bill_fed)
