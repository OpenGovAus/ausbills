import json
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from ausbills.util import BillExtractor, BillListExtractor
from ausbills.models import Bill, BillMeta
from ausbills.types import (
    Parliament,
    House,
    BillProgress,
    ChamberProgress,
    BillTypes,
    Timestamp,
)
from ausbills.util.consts import *
from ausbills.log import get_logger


nsw_logger = get_logger(__file__)


class NSWBillList(BillListExtractor):
    @property
    def bill_list(self) -> List[Dict]:
        return self.__get_bill_list()

    def __get_bill_list(self) -> List[Dict]:
        API_QUERY = (
            "https://legislation.nsw.gov.au/projectdata?"
            "ds=NSW_PCO-BillDataSource&start=1&count=100&sortFie"
            "ld=Title_Sort&sortDirection=asc&expression=%22Event"
            "+Name%22%3DIntroduced+AND+%22Parliament+Year%22%3E%"
            "3D{}0000000000+AND+Title_Phrase%3D'%3F&subset=F&c"
            "ollection=&_={}".format(
                self.__get_parl_year(), str(int(datetime.now().timestamp())) + "000"
            )
        )
        bills_json = self._download_json(API_QUERY)["data"]

        if len(bills_json) == 0:
            print(API_QUERY)
            print("\n\n" + json.dumps(bills_json, indent=2) + "\n\n")
            raise ValueError("Missing bills.")

        bills_list = []
        for bill_entry in bills_json:
            bill_title = bill_entry[TITLE][VALUE]
            bill_url = (
                "https://legislation.nsw.gov.au/view/html/bill/"
                + bill_entry["record-id"]
            )
            try:
                ceguid = bill_entry["Bill Stub"][VALUE][CHILDREN][3][CHILDREN][1][
                    CHILDREN
                ][CHILDREN][1]["@ceguid"]
            except Exception:
                ceguid = bill_entry["Bill Stub"][VALUE][CHILDREN][3][CHILDREN][1][
                    CHILDREN
                ][1][CHILDREN][1][
                    "@ceguid"
                ]  # Because the API provides some HTML info, this can sometimes include missing newlines, messing with the pattern.

            bill_text_url = [
                {
                    API_ID: 0,
                    URL: "https://legislation.nsw.gov.au/view/pdf/bill/" + ceguid,
                }
            ]

            bill_type = {
                "nongov": BillTypes.PRIVATE_MEMBER.value,
                "gov": BillTypes.GOVERNMENT.value,
            }[bill_entry["bill.type"]]

            # print(bill_text_url)
            bill_progress = self.__process_progress(
                bill_entry["Bill Stub"][VALUE][CHILDREN]
            )

            bills_list.append(
                {
                    URL: bill_url,
                    TITLE: bill_title,
                    BILL_TYPE: bill_type,
                    PROGRESS: bill_progress[0][0],
                    CHAMBER_PROGRESS: bill_progress[0][1],
                    INTRO_DATE: bill_progress[1][0],
                    ASSENT_DATE: bill_progress[1][1],
                    TEXT_LINK: bill_text_url,
                    EM_LINK: bill_text_url,  # NSW Bills include the explanatory statement in their prints.
                    ID: ceguid,
                }
            )
        return bills_list

    def __process_progress(self, events_object):
        def get_event(event_entry):
            if isinstance(event_entry, dict):  # Again, \n entries mess us up here
                if isinstance(event_entry[CHILDREN], dict):
                    split_lst = (
                        event_entry[CHILDREN][CHILDREN][0][CHILDREN]
                        .strip()
                        .split(":", 1)
                    )
                elif isinstance(event_entry[CHILDREN], list):
                    split_lst = (
                        event_entry[CHILDREN][1][CHILDREN][0][CHILDREN]
                        .strip()
                        .split(":", 1)
                    )
                else:
                    return []
                return split_lst

        # Find intro house
        intro_event = get_event(events_object[3][CHILDREN][1])
        intro_date = self._get_timestamp(
            intro_event[1].split("\n")[1].strip(), "%d/%m/%Y"
        )
        assent_date = None

        intro_house = {
            "LA": House.LOWER.value,
            "draft": House.LOWER.value,
            "LC": House.UPPER.value,
        }[intro_event[0].split(" ")[-1]]

        chamber_progress = ChamberProgress.FIRST_READING.value

        prog_dict = {BillProgress.ASSENTED.value: False}
        if intro_house == House.LOWER.value:
            prog_dict[BillProgress.FIRST.value] = True
            prog_dict[BillProgress.SECOND.value] = False
        else:
            prog_dict[BillProgress.SECOND.value] = True
            prog_dict[BillProgress.FIRST.value] = False

        try:
            most_recent = get_event(events_object[3][CHILDREN][-2])
        except KeyError:
            most_recent = None
            nsw_logger.info(
                f"Could not find event data for {events_object[3][CHILDREN][-2]}."
            )

        if most_recent is not None:
            if most_recent[0] == "Introduced LA":
                prog_dict[BillProgress.FIRST.value] = True
                chamber_progress = ChamberProgress.SECOND_READING.value
            elif most_recent[0] == "Introduced LC":
                prog_dict[BillProgress.SECOND.value] = True
                chamber_progress = ChamberProgress.SECOND_READING.value
            elif most_recent[0] == "Passed by both Houses":
                prog_dict = {
                    BillProgress.FIRST.value: True,
                    BillProgress.SECOND.value: True,
                    BillProgress.ASSENTED.value: True,
                }
                chamber_progress = ChamberProgress.THIRD_READING.value
                assent_date = self._get_timestamp(
                    most_recent[1].split("\n")[1].strip(), "%d/%m/%Y"
                )
            else:
                nsw_logger.warning(f"Unrecognised event status for {most_recent[0]}.")

        progress = [[prog_dict, chamber_progress], [intro_date, assent_date]]

        return progress

    def __get_parl_year(self):
        webpage = self._download_html("https://legislation.nsw.gov.au/browse/bills")

        return (
            webpage.find("div", {"class": "browse-panel"})
            .find("h2")
            .contents[0]
            .strip()[-4:]
        )


@dataclass
class BillMetaNSW(BillMeta):
    id: str
    bill_type: str
    bill_text_links: List[Dict]
    bill_em_links: List[Dict]
    progress: Dict
    chamber_progress: int
    bill_type: str
    intro_date: Timestamp
    assent_date: Timestamp


def get_bills_metadata() -> List[BillMetaNSW]:
    bills_list = []
    for bill_dict in NSWBillList().bill_list:
        bills_list.append(
            BillMetaNSW(
                parliament=Parliament.NSW.value,
                title=bill_dict[TITLE],
                link=bill_dict[URL],
                progress=bill_dict[PROGRESS],
                chamber_progress=bill_dict[CHAMBER_PROGRESS],
                bill_type=bill_dict[BILL_TYPE],
                bill_text_links=bill_dict[TEXT_LINK],
                bill_em_links=bill_dict[EM_LINK],
                intro_date=bill_dict[INTRO_DATE],
                assent_date=bill_dict[ASSENT_DATE],
                id=bill_dict[ID],
            )
        )
    return bills_list


@dataclass
class BillNSW(Bill, BillMetaNSW):
    sponsor: str


class NSWBillHelper(BillExtractor):
    def __init__(self, bill_meta: BillMetaNSW):
        self.url = bill_meta.link
        self.bill_soup = self._download_html(self.url)
        self.id = bill_meta.id

    def __str__(self):
        return f"<Bill | URL: '{self.url}'>"

    def __repr__(self):
        return "<{}.{} : {} object at {}>".format(
            self.__class__.__module__, self.__class__.__name__, self.id, hex(id(self))
        )

    @property
    def sponsor(self):
        return self._get_sponsor()

    def _get_sponsor(self):
        span = self.bill_soup.find("span", {"class": "bill-type"}).text
        if len(span.split(" - ")) > 1:
            return span.split(" - ")[-1].replace("introduced by ", "").title()
        else:
            return None


def get_bill(bill_meta: BillMetaNSW) -> BillNSW:
    nsw_helper = NSWBillHelper(bill_meta)

    bill_data = BillNSW(**dataclasses.asdict(bill_meta), sponsor=nsw_helper.sponsor)

    return bill_data
