import dataclasses
from dataclasses import dataclass
from typing import List, Dict

from ausbills.util.consts import *
from ausbills.util import BillExtractor, BillListExtractor
from ausbills.log import get_logger
from ausbills.models import Bill, BillMeta
from ausbills.types import House, Parliament, ChamberProgress, \
    BillProgress, BillTypes

qld_logger = get_logger(__file__)


BASE = 'https://www.legislation.qld.gov.au/'
API_CALL = BASE + 'projectdata' \
    '?ds=OQPC-BrowseDataSource&start=1&cou' \
    'nt=9999&sortField=year&sortDirection' \
    '=asc&filterField=year&expression=Repealed%3DN+' \
    'AND+PrintType%3D(%22bill.first%2'\
    '2+OR+%22bill.firstnongovintro%22)+AND+'\
    'ParliamentNo%3D{}&subset=browse&collection=&_={}'


class QLDBillList(BillListExtractor):
    @property
    def all_bills(self):
        return self._get_all_bills()

    def _get_all_bills(self):
        landing_page = self._download_html(BASE + 'browse/bills')
        parl_number = landing_page.find(
            'table', {
                'class': 'table table-bordered table-condensed browse-table'
            }) \
            .find('td').text[:2]  # Current parliament's number

        api_json = self._download_json(
            API_CALL.format(parl_number, self._get_epoch())
        )

        bills_list = []
        for bill_data in api_json['data']:
            bill_title = bill_data[TITLE][VALUE].replace('\u2019', "'")
            bill_id = bill_data[ID][VALUE]
            intro_date = self._get_timestamp(
                bill_data['publication.date'], '%Y-%m-%dT00:00:00')
            bills_list.append({
                TITLE: bill_title,
                ID: bill_id,
                INTRO_ASSEMBLY: intro_date  # QLD is unicamaral
            })
        return bills_list


@dataclass
class BillMetaQLD(BillMeta):
    intro_assembly: int
    id: str


def get_bills_metadata() -> List[BillMetaQLD]:
    meta_list = []
    all_bills = QLDBillList().all_bills
    for bill_dict in all_bills:
        meta_list.append(BillMetaQLD(
            title=bill_dict[TITLE],
            id=bill_dict[ID],
            link=BASE + 'view/html/bill.first/' + bill_dict[ID],
            intro_assembly=bill_dict[INTRO_ASSEMBLY],
            parliament=Parliament.QLD.value
        ))
    return meta_list


@dataclass
class BillQLD(Bill, BillMetaQLD):
    bill_type: str
    bill_em_links: List[Dict]


class QLDBillHelper(BillExtractor):
    def __init__(self, bill_meta: BillMetaQLD):
        self.url = bill_meta.link
        self.bill_id = bill_meta.id
        self.history_page = self._download_html(
            self.url + '/lh').find('table', {'class': 'table table-striped'})
        self.intro_date = bill_meta.intro_assembly
        self.assent_date = None

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return ('<{}.{} : {} object at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.bill_id,
            hex(id(self))))

    @property
    def bill_type(self):
        return self._get_bill_type()

    def _get_bill_type(self):
        if(self.history_page.find('tr').text.strip() == 'Government Bill'):
            return BillTypes.GOVERNMENT.value
        else:
            return BillTypes.PRIVATE_MEMBER.value

    @property
    def em_links(self):
        return self._get_em_links()

    def _get_em_links(self):
        ret_dict = []
        index = 0
        links_column = self.history_page.find_all('tr')[1].find_all('td')[-1]
        em_tag = links_column.find('a', text='Explanatory Note')
        hr_compat_tag = links_column.find(
            'a', {'href': f'/view/pdf/bill.first.hrc/{self.bill_id}'}
        )
        if em_tag:
            ret_dict.append({
                API_ID: index,
                API_HOUSE: House.LOWER.value,
                API_TIME: self.intro_date,
                URL: BASE + em_tag['href']
            })
            index += 1

        if hr_compat_tag:
            ret_dict.append({
                API_ID: index,
                API_HOUSE: House.LOWER.value,
                API_TIME: self.intro_date,
                URL: BASE + hr_compat_tag['href']
            })
        return ret_dict

    @property
    def text_links(self):
        return self._get_text_links()

    def _get_text_links(self):
        pass

    @property
    def progress(self):
        return self._get_progress()

    def _get_progress(self):
        prog_dict = {
            BillProgress.FIRST.value: True,
            BillProgress.ASSENTED.value: False
        }
        final_stage = self.history_page.find_all('tr')[-1]
        if 'Assent' in final_stage.find('td').text:
            prog_dict[BillProgress.ASSENTED.value] = True
            chamb_progress = ChamberProgress.THIRD_READING.value
        elif '3rd' in final_stage.find('td').text:
            chamb_progress = ChamberProgress.THIRD_READING.value
        elif 'Indicative Reprint' in final_stage.find('td').text:
            chamb_progress = ChamberProgress.SECOND_READING.value
        else:
            chamb_progress = ChamberProgress.FIRST_READING.value

        return [prog_dict, chamb_progress]


def get_bill(bill_meta: BillMetaQLD) -> BillQLD:
    qld_helper = QLDBillHelper(bill_meta)

    bill_meta = BillQLD(
        **dataclasses.asdict(bill_meta),
        bill_type=qld_helper.bill_type,
        bill_em_links=qld_helper.em_links,
        bill_text_links=qld_helper.text_links,
        progress=qld_helper.progress[0],
        chamber_progress=qld_helper.progress[1]
    )
    return bill_meta
