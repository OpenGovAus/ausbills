import dataclasses
from dataclasses import dataclass
from typing import Dict, List

from ausbills.util import BillExtractor, BillListExtractor
from ausbills.util.consts import *
from ausbills.models import BillMeta, Bill
from ausbills.types import BillProgress, ChamberProgress, Parliament
from ausbills.log import get_logger


CURRENT_BILLS = 'https://www.parliament.wa.gov.au/parliament/bills.nsf/screenWebCurrentBills?OpenForm&Start=1&Count=-1'
# The single bill appearing on the 2nd page mentioned in the old extractor
# is a duplicate of the final bill on the first page, so there's no issue. 
BASE_URL = 'https://www.parliament.wa.gov.au'

wa_logger = get_logger(__file__)


@dataclass
class BillMetaWA(BillMeta):
    progress: Dict
    assent_date: int
    intro_date: int


class WABillList(BillListExtractor):
    def __init__(self):
        self._get_bills()
    def _get_bills(self):
        bill_list = []
        bill_volume = self._download_html(CURRENT_BILLS, verify=False)
        table = bill_volume.find('table').find('tbody')
        for row in table.find_all('tr'):
            bill_intro = self._get_timestamp(row.find_all('td')[2].text.strip(), '%d %b %Y')
            bill_title = row.find_all('td')[1].text.strip()
            assent_date = None
            bill_url = BASE_URL + row.find_all('td')[1].find('a')['href']

            __bill_legend = row.find('td').find('article')['class']
            if len(__bill_legend) == 1:
                assent_date = self._get_col_date(row.find_all('td')[-1])
                prog_dict = {BillProgress.FIRST.value: True, BillProgress.SECOND.value: True, BillProgress.ASSENTED.value: True}
            else:
                prog_dict = self._generate_prog(__bill_legend)
            bill_list.append({
                TITLE: bill_title,
                URL: bill_url,
                INTRO_DATE: bill_intro,
                ASSENT_DATE: assent_date,
                PROGRESS: prog_dict,
            })
        return bill_list
            
    def _generate_prog(self, legend):
        if legend[0] == 'lc' and legend[1] == 'lc2':
            return {BillProgress.FIRST.value: False, BillProgress.SECOND.value: False, BillProgress.ASSENTED.value: False}
        elif legend[0] == 'lc' and legend[1] == 'la2':
            return {BillProgress.FIRST.value: False, BillProgress.SECOND.value: True, BillProgress.ASSENTED.value: False}
        elif legend[0] == 'la' and legend[1] == 'lc2':
            return {BillProgress.FIRST.value: True, BillProgress.SECOND.value: False, BillProgress.ASSENTED.value: False}        
        else:
            return {BillProgress.FIRST.value: False, BillProgress.SECOND.value: False, BillProgress.ASSENTED.value: False}
    def _get_col_date(self, row):
        return self._get_timestamp(row.text.strip().split('- ')[-1], '%d %b %Y')


def get_bills_metadata() -> List[BillMetaWA]:
    _all_bills = WABillList()._get_bills()
    _bill_meta_list = []
    for bill_dict in _all_bills:
        bill_meta = BillMetaWA(
            parliament=Parliament.WA.value,
            progress=bill_dict[PROGRESS],
            title=bill_dict[TITLE],
            link=bill_dict[URL],
            assent_date=bill_dict[ASSENT_DATE],
            intro_date=bill_dict[INTRO_DATE]
        )
        _bill_meta_list.append(bill_meta)
    return _bill_meta_list


@dataclass
class BillWA(Bill, BillMetaWA):
    bill_no: int
    summary: str
    bill_em_links: List[Dict]
    bill_speech_links: List[Dict]


class WABillHelper(BillExtractor):

    class ExplanatoryStatementError(Exception):
        pass

    _bill_data = dict()

    def __init__(self, bill_meta: BillMetaWA):
        self.bill_soup = self._download_html(bill_meta.link, verify=False)
        self.table = self.bill_soup.find_all('table')

    def _get_bill_no(self):
        return int(self.table[0].find_all(
            'tr')[1].find_all('td')[-1].text.strip())

    def _get_summary(self):
        return self.table[0].find_all('tr')[2].find_all('td')[1].text.strip().replace('\n', ' ')

    def _get_text_links(self, timestamp):
        try:
            url_list = []
            url_list.append({
                '__id': 0,
                '__time': timestamp,
                'url': self._get_pdf('Bill as Introduced')
            })
            return url_list
        except Exception as e:
            wa_logger.warn('An error occurred when obtaining the bill introduction text;\n ' + str(e))
            return [{}]

    def _get_pdf(self, event_label):
        return BASE_URL + self.bill_soup.find('a', {'ga-event-label': event_label})['href']

    def _get_speech(self):
        speeches = []
        try:
            speeches.append({
                URL: self._get_pdf('Second Reading LA'),
                API_HOUSE: BillProgress.FIRST.value
            })
        except Exception as e:
            wa_logger.debug('No Legislative Asembly second reading speech found.\n' + str(e))

        try:
            speeches.append({
                URL: self._get_pdf('Second Reading LC'),
                API_HOUSE: BillProgress.SECOND.value
            })
        except Exception as e:
            wa_logger.debug('No Legislative Council second reading speech found.\n' + str(e))

        _compiled_list = []
        for index,speech in enumerate(speeches):
            _compiled_list.append({
                API_ID: index,
                URL: speech[URL].replace(' ', '%20'),
                API_HOUSE: speech[API_HOUSE]
            })
        return _compiled_list

    def _get_em_statement(self):
        statements = []
        try:
            statements.append({URL: self._get_pdf('Explanatory Memorandum LA'), API_HOUSE: BillProgress.FIRST.value})
        except Exception as e:
            wa_logger.debug('No Legislative Asembly EM found.\n' + str(e))
        
        try:
            statements.append({URL: self._get_pdf('Explanatory Memorandum LC'), 'house': BillProgress.SECOND.value})
        except Exception as e:
            wa_logger.debug('No Legislative Council EM found.\n' + str(e))

        _compiled_list = []
        for index,statement in enumerate(statements):
            _compiled_list.append({
                API_ID: index,
                URL: statement[URL],
                API_HOUSE: statement[API_HOUSE]
            })
        return _compiled_list

    def _get_reading(self):
        def __get_num(text):
            if 'First' in text:
                return ChamberProgress.FIRST_READING.value
            elif 'Second' in text or 'Referred' in text:
                return ChamberProgress.SECOND_READING.value
            else:
                return ChamberProgress.THIRD_READING.value  # Even if the bill has passed, we should return that the third reading was reached.

        return __get_num(self.table[0].find_all('tr')[-1].find_all('td')[-1].contents[0])


def get_bill(bill_meta: BillMetaWA) -> BillWA:
    wa_helper = WABillHelper(bill_meta)
    bill_wa = BillWA(
        **dataclasses.asdict(bill_meta),
        bill_no=wa_helper._get_bill_no(),
        summary=wa_helper._get_summary(),
        bill_text_links=wa_helper._get_text_links(bill_meta.intro_date),
        bill_em_links=wa_helper._get_em_statement(),
        bill_speech_links=wa_helper._get_speech(),
        chamber_progress=wa_helper._get_reading()
    )
    return bill_wa
