import dataclasses
from dataclasses import dataclass
from typing import Dict, List

from ausbills.models import BillMeta, Bill, PdfUrl, UrlStr
from ausbills.util import BillExtractor, BillListExtractor
from ausbills.types import BillProgress, Parliament, BillTypes, ChamberProgress
from ausbills.util.consts import *

BASE_URL = 'https://legislation.act.gov.au'


class ACTBillList(BillListExtractor):
    def __init__(self):
        bill_volume = self._download_html(
            'https://legislation.act.gov.au/results?category=cBil&status=Current&action=browse').find(
                'table', {'id': 'results-table-bill'}).find('tbody')
        self._bill_list = self._get_bill_list(bill_volume)

    def _get_bill_list(self, bill_volume):
        bill_list = []
        has_passed = False
        for row in bill_volume.find_all('tr', recursive=False):
            bill_intro_date = row.find('td')['data-order']
            __title_col = row.find_all('td')[1]
            bill_title = __title_col.text.strip()
            bill_url = BASE_URL + __title_col.find('a')['href']
            bill_intro = self._get_timestamp(bill_intro_date[:8], '%Y%m%d')

            __status_col = row.find_all('td')[-1]
            if __status_col['data-order'] == 'passed':
                has_passed = True
                passed_date = self._get_timestamp(
                    __status_col.contents[1], '%d %B %Y')
            else:
                passed_date = None
            bill_type = self._parse_type(row.find_all('td')[2].text)
            bill_id = bill_url[-6:-1]

            if has_passed:
                prog_dict = {BillProgress.FIRST.value: True, BillProgress.ASSENTED.value: True}
                chamber_progress = ChamberProgress.THIRD_READING.value
            else:        
                prog_dict = {BillProgress.FIRST.value: True, BillProgress.ASSENTED.value: False} # Bills will always remain in the first house in a unicameral parliament
                chamber_progress = ChamberProgress.FIRST_READING.value

            bill_list.append({
                TITLE: bill_title,
                URL: bill_url,
                BILL_TYPE: bill_type,
                INTRO_ASSEMBLY: bill_intro,
                PASSED_ASSEMBLY: passed_date,
                PASSED: prog_dict,
                CHAMBER_PROGRESS: chamber_progress,
                ID: bill_id,
            })
        return bill_list

    def _parse_type(self, type_string):
        if type_string == 'GOV':
            return BillTypes.GOVERNMENT.value
        elif type_string == 'PMB':
            return BillTypes.PRIVATE_MEMBER.value


@dataclass
class BillMetaACT(BillMeta):
    bill_type: str
    passed_assembly: int
    intro_assembly: int
    progress: Dict
    chamber_progress: int
    id: int


@dataclass
class BillACT(Bill, BillMetaACT):
    sponsor: str
    bill_em_links: List[Dict]
    scrutiny_report: PdfUrl
    intro_speech: UrlStr


class ACTBillObject(BillExtractor):
    _bill_data = dict()

    def __init__(self, bill_meta: BillMetaACT):
        self.bill_soup = self._download_html(bill_meta.link)
        self.bill_meta_list = self.bill_soup.find('dl').find_all('dd')
        self.url = bill_meta.link
        if(len(self.bill_meta_list) is None):
            raise self.ExtractorError(
                f'Could not find extra bill metadata:\n\n{self.bill_meta_list}')

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return ('<{}.{} : {} object at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.url.split('=')[-1],
            hex(id(self))))

    def _get_sponsor(self):
        return self.bill_meta_list[1].text.strip()

    def _get_text_links(self):
        urls = []
        table = self.bill_soup.find(
            'h3', {'tabindex': '0'}).findNext('table').find('tbody')
        for index, entry in enumerate(table.find_all('tr')):
            time = self._get_timestamp(
                table.find_all('td')[1]['data-order'][:8], '%Y%m%d')
            url = BASE_URL + entry.find(
                'a', {'class': 'button download pdf'})['href']

            urls.append({
                '__time': time,
                '__id': index,
                'url': url,
            })
        return urls

    def _get_em_links(self):
        urls = []
        table = self.bill_soup.find(
            'h3', {'tabindex': None}).findNext('table').find('tbody')
        for index, row in enumerate(table.find_all('tr')):
            time = self._get_timestamp(
                table.find_all('td')[1]['data-order'][:8], '%Y%m%d')
            url = BASE_URL + row.find(
                'a', {'class': 'button download pdf'})['href']
            urls.append({
                '__time': time,
                '__id': index,
                'url': url,
                'house': BillProgress.FIRST.value,
            })
        return urls

    def _get_scrutiny_link(self):
        notes_col = self.bill_soup.find(
            'h3', {'tabindex': '0'}).findNext(
                'table').find('tbody').find('td', {'class': 'notes'})
        if(notes_col is not None):
            for a in notes_col.find_all('a'):
                if(a.contents[0] == 'Scrutiny Committee report'):
                    return a['href']

    def _get_speech_link(self):
        notes_col = self.bill_soup.find(
            'h3', {'tabindex': '0'}).findNext(
                'table').find('tbody').find('td', {'class': 'notes'})
        if(notes_col is not None):
            for a in notes_col.find_all('a'):
                if(a.contents[0] == 'Presentation speech'):
                    return a['href']


def get_bills_metadata() -> List[BillMetaACT]:
    _all_bills = ACTBillList()._bill_list
    _bill_meta_list = []
    for bill_dict in _all_bills:
        bill_meta = BillMetaACT(
            parliament=Parliament.ACT.value,
            progress=bill_dict[PASSED],
            title=bill_dict[TITLE],
            link=bill_dict[URL],
            bill_type=bill_dict[BILL_TYPE],
            passed_assembly=bill_dict[PASSED_ASSEMBLY],
            intro_assembly=bill_dict[INTRO_ASSEMBLY],
            id=bill_dict[ID],
            chamber_progress=bill_dict[CHAMBER_PROGRESS]
        )
        _bill_meta_list.append(bill_meta)
    return(_bill_meta_list)


def get_bill(bill_meta: BillMetaACT) -> BillACT:
    act_helper = ACTBillObject(bill_meta)
    bill_act = BillACT(
        **dataclasses.asdict(bill_meta),  # Copy metadata we already got as separate instance.
        sponsor=act_helper._get_sponsor(),
        bill_text_links=act_helper._get_text_links(),
        bill_em_links=act_helper._get_em_links(),
        intro_speech=act_helper._get_speech_link(),
        scrutiny_report=act_helper._get_scrutiny_link()
    )
    return bill_act
