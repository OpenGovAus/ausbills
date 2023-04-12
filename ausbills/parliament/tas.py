from dataclasses import dataclass
import dataclasses
from typing import Dict, List

from ausbills.util.consts import *
from ausbills.util import BillExtractor, BillListExtractor

from ausbills.types import BillProgress, ChamberProgress, House, Parliament
from ausbills.log import get_logger
from ausbills.models import Bill, BillMeta


DOMAIN = "https://www.parliament.tas.gov.au"
BASE_URL = DOMAIN + "/Bills/current/"

tas_logger = get_logger(__file__)


class TasBillList(BillListExtractor):
    @property
    def all_bills(self):
        return self._get_bills()

    def _get_bills(self):
        bill_list = []
        table = (
            self._download_html(BASE_URL + "BillWeb.html")
            .find("table", {"class": "ui table"})
            .find("tbody")
        )
        for row in table.find_all("tr"):
            bill_title = row.find("a").text
            # bill_num =
            __base_str = row.find("td").contents[-1][2:-1].split(" of ")
            bill_num = f"{__base_str[1]}_{__base_str[0]}"
            bill_url = BASE_URL + row.find("a")["href"]
            bill_list.append(
                {
                    TITLE: bill_title,
                    URL: bill_url,
                    ID: bill_num,
                }
            )
        return bill_list


@dataclass
class BillMetaTas(BillMeta):
    id: str


def get_bills_metadata():
    compiled_list = []
    all_bills = TasBillList().all_bills
    for bill_dict in all_bills:
        compiled_list.append(
            BillMetaTas(
                title=bill_dict[TITLE],
                parliament=Parliament.TAS.value,
                link=bill_dict[URL],
                id=bill_dict[ID],
            )
        )
    return compiled_list


class TasBillHelper(BillExtractor):
    def __init__(self, bill_meta: BillMetaTas):
        self.url = bill_meta.link
        self.bill_soup = self._download_html(self.url)

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return "<{}.{} : {} object at {}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.url.split("current/")[-1].replace(".html", ""),
            hex(id(self)),
        )

    @property
    def sponsor(self):
        return self.__get_sponsor()

    def __get_sponsor(self):
        return (
            self.bill_soup.find("div", {"class": "ui blue segment"})
            .find("h2")
            .findNext("p")
            .text.split("Introduced by: ")[-1]
        )

    @property
    def parl_progress(self):
        return self.__get_progress()

    def __get_progress(self):
        def __get_table(index):
            return divtable.find_all("table")[index].find("tbody")

        def __get_first_reading(table):
            return __check_date(table.find("tr"))

        def __check_date(row):
            col = row.find_all("td")[-1]
            if not len(col.text.strip()) > 0:
                return 0
            else:
                return self._get_timestamp(col.text.strip(), "%d/%m/%Y")

        def __recent_reading(table):
            third_reading = self.bill_soup.find_all("tr")[-2]
            second_reading = self.bill_soup.find_all("tr")[2]
            if __check_date(third_reading) > 0:
                return ChamberProgress.THIRD_READING.value
            elif __check_date(second_reading) > 0:
                return ChamberProgress.THIRD_READING.value
            else:
                return ChamberProgress.FIRST_READING.value

        divtable = self.bill_soup.find("div", {"class": "ui two column stackable grid"})
        self._ha_table = __get_first_reading(__get_table(0))
        self._lc_table = __get_first_reading(__get_table(-1))

        # Getting the bill's chamber progress:
        prog_dict = {
            BillProgress.FIRST.value: True,
            BillProgress.SECOND.value: True,
            BillProgress.ASSENTED.value: False,
        }
        if self._ha_table > self._lc_table:
            # Tabled in the House of Assembly most recently
            if self._lc_table == 0:  # If the bill has never been read in the LC:
                prog_dict[BillProgress.SECOND.value] = False
            reading = __recent_reading(self._ha_table)
        else:
            # Tabled in the Legislative Council most recently
            if self._ha_table == 0:  # If the bill has never been read in the HA:
                prog_dict[BillProgress.FIRST.value] = False
            reading = __recent_reading(self._lc_table)
        return [reading, prog_dict]

    @property
    def text_links(self):
        return self.__get_text_links()

    def __get_text_links(self):
        div = self.bill_soup.find("div", {"class": "ui blue segment"})
        intro_text = div.find("a")
        if self._ha_table > self._lc_table or self._lc_table == 0:
            house = House.LOWER.value
            time = self._ha_table
        else:
            house = House.UPPER.value
            time = self._lc_table
        return [
            {
                API_ID: 0,
                API_TIME: time,
                API_HOUSE: house,
                URL: DOMAIN + intro_text["href"],
            }
        ]

    @property
    def em_links(self):
        return self.__get_em_links()

    def __get_em_links(self):
        em_list = []
        div = self.bill_soup.find("div", {"class": "ui three column grid"})
        ems = div.find_all("div", {"class": "ui column"})[1:]
        for index, em in enumerate(ems):
            try:
                em_url = DOMAIN + em.find("a")["href"].replace(" ", "%20")
            except Exception as e:
                index -= 1
                continue

            em_list.append({API_ID: index, API_HOUSE: House.LOWER.value, URL: em_url})
        return em_list


@dataclass
class BillTas(Bill, BillMetaTas):
    sponsor: str
    bill_em_links: List[Dict]


def get_bill(bill_meta: BillMetaTas) -> BillTas:
    tas_helper = TasBillHelper(bill_meta)
    return BillTas(
        **dataclasses.asdict(bill_meta),
        sponsor=tas_helper.sponsor,
        progress=tas_helper.parl_progress[1],
        chamber_progress=tas_helper.parl_progress[0],
        bill_text_links=tas_helper.text_links,
        bill_em_links=tas_helper.em_links,
    )
