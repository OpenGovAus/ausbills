import dataclasses
from dataclasses import dataclass
from typing import Dict, List


from ausbills.log import get_logger
from ausbills.util.consts import *
from ausbills.util import BillListExtractor, BillExtractor
from ausbills.models import Bill, BillMeta
from ausbills.types import BillProgress, ChamberProgress, Parliament


vic_logger = get_logger(__file__)


BASE = 'https://www.legislation.vic.gov.au/'
API_CALL = BASE + 'app/api/search/title_content?from=0&size=999&include' \
                  'Filters%5B0%5D%5Bprefix%5D%5Btitle_az%5D=&includeFil' \
                  'ters%5B1%5D%5Bterm%5D%5Bfield_bill_parliament_curren' \
                  't%5D=true&includeFilters%5B2%5D%5Bterm%5D%5Btype%5D=' \
                  'bill&includeFields%5B0%5D=title&includeFields%5B1%5D' \
                  '=field_in_force_former_title&includeFields%5B2%5D=ur' \
                  'l&includeFields%5B3%5D=type&includeFields%5B4%5D=leg' \
                  'islation_type&includeFields%5B5%5D=field_act_sr_numb' \
                  'er&includeFields%5B6%5D=legislation_year&includeFiel' \
                  'ds%5B7%5D=field_act_sr_status_date&includeFields%5B8' \
                  '%5D=field_legislation_status&includeFields%5B9%5D=fi' \
                  'eld_bill_pre_2004&includeFields%5B10%5D=field_bill_p' \
                  'arliament_term&sort%5B0%5D%5B_score%5D=desc&sort%5B1' \
                  '%5D%5Btitle_az%5D=asc&aggregations%5Blegislation_yea' \
                  'r%5D%5Bterms%5D%5Bfield%5D=legislation_year&aggregat' \
                  'ions%5Blegislation_year%5D%5Bterms%5D%5Border%5D%5B_' \
                  'key%5D=desc&aggregations%5Blegislation_year%5D%5Bter' \
                  'ms%5D%5Bsize%5D=250&aggregations%5Bfield_legislation' \
                  '_status%5D%5Bterms%5D%5Bfield%5D=field_legislation_s' \
                  'tatus&aggregations%5Bfield_legislation_status%5D%5Bt' \
                  'erms%5D%5Border%5D%5B_key%5D=asc&aggregations%5Bfiel' \
                  'd_legislation_status%5D%5Bterms%5D%5Bsize%5D=250'


@dataclass
class BillMetaVic(BillMeta):
    progress: Dict
    chamber_progress: int


class VicBillList(BillListExtractor):
    @property
    def all_bills(self):
        return self._get_all_bills()

    def _get_all_bills(self):
        json_bills = self._download_json(API_CALL)['results']

        bills_list = []
        for bill_dict in json_bills:
            bill_title = bill_dict['title'][0]
            bill_url = bill_dict['url'][0].replace('/site-6/', BASE)
            bill_progress = self._parse_progress(
                bill_dict['field_legislation_status'][0])
            bills_list.append({
                TITLE: bill_title,
                URL: bill_url,
                PROGRESS: bill_progress
            })
        return bills_list

    def _parse_progress(self, stattext):
        readings = {
            'first reading': ChamberProgress.FIRST_READING.value,
            'second reading': ChamberProgress.SECOND_READING.value,
            'third reading': ChamberProgress.THIRD_READING.value,
            'first reading passed': ChamberProgress.FIRST_READING.value,
            'second reading passed': ChamberProgress.SECOND_READING.value,
            'third reading passed': ChamberProgress.THIRD_READING.value,
            'first reading (passed Council)': ChamberProgress.FIRST_READING.value,
            'second reading (passed Council)': ChamberProgress.SECOND_READING.value,
            'third reading (passed Council)': ChamberProgress.THIRD_READING.value,
            'first reading (passed Assembly)': ChamberProgress.FIRST_READING.value,
            'second reading (passed Assembly)': ChamberProgress.SECOND_READING.value,
            'third reading (passed Assembly)': ChamberProgress.THIRD_READING.value,
            'Passed and Assented to': ChamberProgress.THIRD_READING.value,
            'Amendments under consideration': ChamberProgress.SECOND_READING.value
        }

        if stattext == 'Passed both Houses' \
                or stattext == 'Passed and Assented to':
            prog_dict = {
                BillProgress.FIRST.value: True,
                BillProgress.SECOND.value: True,
                BillProgress.ASSENTED.value: True
            }
            chamber_progress = ChamberProgress.THIRD_READING.value
        else:
            chamber_split = stattext.split('reading ')[0]
            stat_split = stattext.split('reading ')[-1]

            if 'Council' in chamber_split:
                if '(passed Assembly)' in stat_split:
                    prog_dict = {
                        BillProgress.FIRST.value: True,
                        BillProgress.SECOND.value: True,
                        BillProgress.ASSENTED.value: False
                    }
                else:
                    prog_dict = {
                        BillProgress.FIRST.value: False,
                        BillProgress.SECOND.value: True,
                        BillProgress.ASSENTED.value: False
                    }
            else:
                if '(passed Council)' in stat_split:
                    prog_dict = {
                        BillProgress.FIRST.value: True,
                        BillProgress.SECOND.value: True,
                        BillProgress.ASSENTED.value: False
                    }
                else:
                    prog_dict = {
                        BillProgress.FIRST.value: True,
                        BillProgress.SECOND.value: False,
                        BillProgress.ASSENTED.value: False
                    }

            chamber_progress = readings[stattext.split(' - ')[-1]]
        return [prog_dict, chamber_progress]


def get_bills_metadata() -> List[BillMetaVic]:
    all_bills = VicBillList().all_bills

    meta_list = []

    for bill_dict in all_bills:
        meta_list.append(BillMetaVic(
            title=bill_dict[TITLE],
            link=bill_dict[URL],
            parliament=Parliament.VIC.value,
            progress=bill_dict[PROGRESS][0],
            chamber_progress=bill_dict[PROGRESS][1]
        ))
    return meta_list


@dataclass
class BillVic(Bill, BillMetaVic):
    bill_em_links: List[Dict]
    sponsor: str


class VicBillHelper(BillExtractor):
    def __init__(self, bill_meta: BillMetaVic):
        self.url = bill_meta.link
        self.bill_soup = self._download_html(self.url)

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return ('<{}.{} : {} object at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.url,
            hex(id(self))))

    @property
    def sponsor(self):
        return self._get_sponsor()

    def _get_sponsor(self):
        first_table = self.bill_soup.find('div', {'class': 'lgs-bill-table'})
        sponsor_tag = first_table.find(
            'span', {'class': 'lgs-bill-table__term-title--bold'})
        if sponsor_tag is not None:
            return sponsor_tag.text
        else:
            return None

    @property
    def em_links(self):
        return self._get_doc_url('Introduction print – Explanatory Memorandum')

    @property
    def text_links(self):
        return self._get_doc_url('Introduction print – Bill')

    def _get_doc_url(self, data_tid):
        header = self.bill_soup.find(
            'li',
            {
                'data-tid': data_tid
            })
        if header is not None:
            for link in header.find_all('a'):
                if '.pdf' in link['href'] or '.PDF' in link['href']:
                    doc_url = link['href']

            return [{
                URL: doc_url,
                API_ID: 0
            }]
        else:
            return [{}]


def get_bill(bill_meta: BillMetaVic) -> BillVic:
    vic_helper = VicBillHelper(bill_meta)
    bill_data = BillVic(
        **dataclasses.asdict(bill_meta),
        sponsor=vic_helper.sponsor,
        bill_em_links=vic_helper.em_links,
        bill_text_links=vic_helper.text_links
    )
    return bill_data
