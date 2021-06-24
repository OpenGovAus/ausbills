import dataclasses
from dataclasses import dataclass

from typing import List

from ausbills.util.consts import *
from ausbills.util import BillExtractor, BillListExtractor
from ausbills.models import Bill, BillMeta
from ausbills.types import House, Parliament, BillProgress, ChamberProgress

BASE = 'https://www.legislation.sa.gov.au/'


class SABillList(BillListExtractor):
    @property
    def all_bills(self):
        return self._get_all_bills()

    def _get_all_bills(self):
        table = self._download_html(
            BASE + 'listBills.aspx?key=').find('tbody')  # By providing a null key, the table returns all values.

        bills_list = []
        for bill_row in table.find_all('tr'):
            title_text = bill_row.find('a').text.strip().replace('\n', '')
            bill_title = title_text
            sponsor = str()
            if('—introduced by ' in title_text):
                sponsor = title_text.split('—introduced by ')[-1]
                bill_title = title_text.split('—introduced by ')[0]
            bill_url = BASE + bill_row.find('a')['href'].replace(' ', '%20')
            bills_list.append({
                TITLE: bill_title,
                URL: bill_url,
                SPONSOR: sponsor
            })
        return bills_list


@dataclass
class BillMetaSA(BillMeta):
    sponsor: str
    chamber_progress: int


def get_bills_metadata() -> List[BillMetaSA]:
    all_bills = SABillList().all_bills

    meta_list = []
    for bill_dict in all_bills:
        meta_list.append(BillMetaSA(
            title=bill_dict[TITLE],
            link=bill_dict[URL],
            parliament=Parliament.SA.value,
            sponsor=bill_dict[SPONSOR],
            chamber_progress=ChamberProgress.FIRST_READING.value
        ))
    return meta_list


@dataclass
class BillSA(Bill, BillMetaSA):
    pass


class SAHelper(BillExtractor):
    def __init__(self, bill_meta: BillMetaSA):
        self.url = bill_meta.link
        self.bill_soup = self._download_html(self.url).find('tbody')

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return ('<{}.{} : {} object at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.url,  # TODO There's no easily accessible bill number or ID so this seems like the best option, could be others though.
            hex(id(self))))

    @property
    def text_links(self):
        return self._get_text_links()

    def _get_text_links(self):
        links = []
        for index, row in enumerate(self.bill_soup.find_all('tr')):
            link = BASE + row.find_all('td')[1] \
                .find('a')['href'].replace(' ', '%20')

            house = House.LOWER.value if 'House of Assembly' \
                in row.text else House.UPPER.value

            links.append({
                API_ID: index,
                API_HOUSE: house,
                URL: link
            })
        return links

    @property
    def progress(self):
        return self._get_progress()

    def _get_progress(self):
        final_row = self.bill_soup.find_all('tr')[-1].find('td')
        prog_dict = {
            BillProgress.FIRST.value: True,
            BillProgress.SECOND.value: False,
            BillProgress.ASSENTED.value: False
        }
        if 'received' in final_row.text:  # This means that the bill has been moved from one house to another
            prog_dict = {
                BillProgress.FIRST.value: True,
                BillProgress.SECOND.value: True,
                BillProgress.ASSENTED.value: False
            }
        elif 'introduced' in final_row.text or 'restored' in final_row.text:
            if 'House of Assembly' not in final_row.text:
                prog_dict = {
                    BillProgress.FIRST.value: False,
                    BillProgress.SECOND.value: True,
                    BillProgress.ASSENTED.value: False
                }
        elif 'passed both' in final_row.text:
            prog_dict = {
                BillProgress.FIRST.value: True,
                BillProgress.SECOND.value: True,
                BillProgress.ASSENTED.value: True
            }
        else:
            raise self.ExtractorError(
                f'Could not accurately determine bill progress for {self.url} \
                    \n\n{self.__repr__()}')

        return prog_dict


def get_bill(bill_meta: BillMetaSA) -> BillSA:
    sa_helper = SAHelper(bill_meta)

    bill_data = BillSA(
        **dataclasses.asdict(bill_meta),
        bill_text_links=sa_helper.text_links,
        progress=sa_helper.progress
    )
    return bill_data
