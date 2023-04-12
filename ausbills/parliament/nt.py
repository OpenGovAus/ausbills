import dataclasses
from dataclasses import dataclass
from typing import Dict, List


from ausbills.util.consts import *
from ausbills.util import BillExtractor, BillListExtractor
from ausbills.models import Bill, BillMeta
from ausbills.types import Parliament, House, BillProgress, ChamberProgress, Timestamp


BASE_URL = "https://legislation.nt.gov.au/en/LegislationPortal/Bills/"


class NTBillList(BillListExtractor):
    @property
    def all_bills(self):
        return self.__get_all_bills()

    def __get_all_bills(self):
        webpage = self._download_html(BASE_URL + "By-Session")

        table = webpage.find(
            "table", {"class": "table"}
        )  # Finds the first table on the page, which is the most recent (current) parliament session.
        table.find("thead").decompose()  # Remove the table's header

        bills_list = []
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            bill_no = int(cols[1].text)
            bill_title = cols[2].text.strip()
            bill_url = BASE_URL + cols[2].find("a")["href"]
            intro_date = self._get_timestamp(cols[3].text, "%d/%m/%Y")
            _passed = cols[4].text
            if len(_passed) > 0:
                passed_date = self._get_timestamp(_passed, "%d/%m/%Y")
            else:
                passed_date = None
            bills_list.append(
                {
                    URL: bill_url,
                    TITLE: bill_title,
                    ID: bill_no,
                    INTRO_ASSEMBLY: intro_date,
                    PASSED_ASSEMBLY: passed_date,
                }
            )
        return bills_list


@dataclass
class BillMetaNT(BillMeta):
    id: int
    passed_assembly: Timestamp
    intro_assembly: Timestamp


def get_bills_metadata() -> List[BillMetaNT]:
    bill_meta_list = []
    all_bills = NTBillList().all_bills
    for bill_dict in all_bills:
        bill_meta = BillMetaNT(
            id=bill_dict[ID],
            passed_assembly=bill_dict[PASSED_ASSEMBLY],
            intro_assembly=bill_dict[INTRO_ASSEMBLY],
            link=bill_dict[URL],
            title=bill_dict[TITLE],
            parliament=Parliament.NT.value,
        )
        bill_meta_list.append(bill_meta)
    return bill_meta_list


class BillNTHelper(BillExtractor):
    def __init__(self, bill_meta: BillMetaNT):
        self.bill_soup = self._download_html(bill_meta.link)
        self.billHash = bill_meta.link.split("id=")[1].replace("&amp;_z=z", "")
        self.intro_date = bill_meta.intro_assembly
        self.passed = True if bill_meta.passed_assembly else False

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return "<{}.{} : {} object at {}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.billHash,
            hex(id(self)),
        )

    @property
    def progress(self):
        return [self.__get_bill_progress(), self.__get_chamb_progress()]

    def __get_bill_progress(self):
        prog_dict = {BillProgress.FIRST.value: True}
        if self.passed:
            prog_dict[BillProgress.ASSENTED.value] = True
        else:
            prog_dict[BillProgress.ASSENTED.value] = False
        return prog_dict

    def __get_chamb_progress(self):
        return (
            ChamberProgress.SECOND_READING.value
            if not self.passed
            else ChamberProgress.THIRD_READING.value
        )

    @property
    def pdf(self):
        return self.__get_pdf()

    def __get_pdf(self):
        pdfURL = self.bill_soup.find("i", {"class": "fa fa-file-pdf-o fa-3x"}).parent[
            "href"
        ]
        return [
            {
                API_ID: 0,
                API_HOUSE: House.LOWER.value,
                API_TIME: self.intro_date,
                URL: pdfURL,
            }
        ]

    @property
    def em_links(self):
        return self.__get_em_links()

    def __get_em_links(self):
        try:
            pdfUrl = self.bill_soup.find(
                "i", {"class": "fa fa-file-pdf-o fa-2x"}
            ).parent["href"]
            return [
                {
                    API_ID: 0,
                    API_HOUSE: House.LOWER.value,
                    API_TIME: self.intro_date,
                    URL: pdfUrl,
                }
            ]
        except Exception:
            return []

    @property
    def sponsor(self):
        return self.__get_sponsor()

    def __get_sponsor(self):
        table = self.bill_soup.find("fieldset", {"class": "roundedWhiteBorders"})
        return table.find_all("div", {"class": "row"})[2].find("span").text


@dataclass
class BillNT(Bill, BillMetaNT):
    bill_em_links: List[Dict]
    sponsor: str


def get_bill(bill_meta: BillMetaNT) -> BillNT:
    nt_helper = BillNTHelper(bill_meta)
    _prog = nt_helper.progress
    bill_data = BillNT(
        **dataclasses.asdict(bill_meta),
        progress=_prog[0],
        chamber_progress=_prog[1],
        bill_text_links=nt_helper.pdf,
        bill_em_links=nt_helper.em_links,
        sponsor=nt_helper.sponsor,
    )
    return bill_data
