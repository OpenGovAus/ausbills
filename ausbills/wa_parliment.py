from dataclasses import dataclass
from multiprocessing import Pool
from typing import List, NewType, Tuple, Optional, TypedDict

from urlpath import URL
from bs4 import BeautifulSoup, ResultSet, Tag
import requests
from datetime import datetime

from ausbills.types_parliament import House
from ausbills.util.either import Either
from pymonad.either import Left, Right
from pymonad.maybe import Maybe, Just, Nothing

from ausbills import get_logger
from ausbills.util.attr_dict import AttrDict
from ausbills.util.funcs import chunks

DATE_FMT_WA = "%{0}d/%{0}m/%y".format('')  # '#' if sys.platform.startswith('win32') else '-')

PdfUrl = NewType('PdfUrl', str)
UrlStr = NewType('UrlStr', str)

log = get_logger(__file__)

# note: current_bills_url (when I tried it) had 1 bill on the "next page", which is annoying. all_bills_url didn't.
current_bills_url = "https://www.parliament.wa.gov.au/parliament/bills.nsf/" \
                    "screenWebCurrentBills?openform&start=1&count=30000"

all_bills_url = "https://www.parliament.wa.gov.au/parliament/bills.nsf/WebAllBills?openview&start=1&count=30000"
progress_of_bills_url = "https://www.parliament.wa.gov.au/Parliament/Bills.nsf/screenBillsProgress"

waph_base_url = URL("https://www.parliament.wa.gov.au/")


def reqs_get_wa_parli(url, *args, **kwargs):
    return requests.get(url, *args, verify='digicert_sha2_high_assurance_server_ca.pem', **kwargs)


class ScrapeBillProgressException(Exception):
    pass


class ScrapeBillPageException(Exception):
    pass


@dataclass
class BillProgress1House:
    house: House
    fst_read: Maybe[datetime]
    snd_read_hansard: Maybe[Tuple[datetime, str, UrlStr]]
    snd_read: Maybe[datetime]
    consid_detail: Maybe[datetime]
    amend: Maybe[datetime]
    thd_read: Maybe[datetime]

    @classmethod
    def from_tds(cls, house: House, tds: List[Tag]) -> 'BillProgress1House':
        _d = AttrDict(house=house)
        _d.fst_read = BillProgress.parse_date(tds[0].text)
        _d.snd_read_hansard = cls.read_snd_and_hansard(tds[1])
        _d.snd_read = BillProgress.parse_date(tds[2].text)
        _d.consid_detail = BillProgress.parse_date(tds[3].text)
        _d.amend = BillProgress.parse_date(tds[4].text)
        _d.thd_read = BillProgress.parse_date(tds[5].text)
        return BillProgress1House(**_d)

    @staticmethod
    def read_snd_and_hansard(td: Tag) -> Maybe[Tuple[datetime, str, UrlStr]]:
        font_t_children = "__UNSET__"
        try:
            font_t_children = list(td.children.__next__().children)
            if len(font_t_children) < 4:
                return Nothing
            if len(font_t_children) > 4:
                log.error(f"This is very unexpected: {font_t_children}")
            date_str, br, p_dot, hansard_link = font_t_children
            hansard_link: Tag
            date = BillProgress.parse_date(date_str)
            ref = p_dot + hansard_link.text
            url = UrlStr(str(waph_base_url / hansard_link['href']))
            if date.is_just():
                return Just((date.value, ref, url))
        except Exception as e:
            log.warning(f"Exception in read_snd_and_hansard: {e}\n\nfont_t_children: {font_t_children}")
        return Nothing


@dataclass
class BillProgress:
    name: str
    url: UrlStr
    bill_no: str
    la_progress: BillProgress1House
    lc_progress: BillProgress1House
    assent_date: Maybe[datetime]

    @classmethod
    def from_tds(cls, tds: List[Tag]):
        if len(tds) != 15:
            log.warning(f"Got a row in bills progress page that had length /= 15: [ {', '.join(map(str, tds))} ]")
            raise ScrapeBillProgressException(
                f"Got a row in bills progress page that had length /= 15: [ {', '.join(map(str, tds))} ]")
        _d = AttrDict()
        _d.name, _d.url = cls.read_bill_name_link(tds[0])
        _d.url = _d.url if _d.url.startswith('http') else str(waph_base_url / _d.url)
        _d.bill_no = tds[1].text.strip()
        _d.la_progress = BillProgress1House.from_tds(House.LOWER, tds[2:8])
        _d.lc_progress = BillProgress1House.from_tds(House.UPPER, tds[8:14])
        _d.assent_date = cls.parse_date(tds[14].text)
        return BillProgress(**_d)

    @staticmethod
    def read_bill_name_link(td: Tag) -> (str, UrlStr):
        a: Tag = td.children.__next__()
        return a.text, str(waph_base_url / a['href'])

    @staticmethod
    def parse_date(date_text: str) -> Maybe[datetime]:
        _date_text = date_text.strip()
        if _date_text == "":
            return Nothing
        try:
            d_parts = _date_text.split('/')
            extra_day = '0' if len(d_parts[0]) == 1 else ''
            extra_mon = '0' if len(d_parts[1]) == 1 else ''
            d_str = f"{extra_day}{d_parts[0]}/{extra_mon}{d_parts[1]}/{d_parts[2]}"
            dt = datetime.strptime(d_str, DATE_FMT_WA)
            return Just(dt)
        except ScrapeBillPageException as e:
            print(f"This branch never happened during testing. You should see why this prints if it ever does.")
            raise e
            return Nothing


@dataclass
class Bill:
    name: str
    bill_no: str
    url: str
    bill_progress: Maybe[BillProgress]
    # from the detailed page
    synopsis: str
    private_members_bill: Maybe[str]
    status: str
    bill_history: List[Tuple[str, PdfUrl]]
    acts_amended: List[Tuple[str, PdfUrl]]
    related_committee_activity: List[Tuple[str, PdfUrl]]
    lc_supplementary: List[Tuple[str, PdfUrl]]
    messages: List[Tuple[str, PdfUrl]]
    progress_la: List[Tuple[str, datetime]]
    progress_lc: List[Tuple[str, datetime]]
    superseded_lc_supplementary: List[Tuple[str, PdfUrl]]
    comparisons_between_version: Tuple[List[Tuple[str, PdfUrl]], List[Tuple[str, PdfUrl]]]
    conference_of_managers: List[Tuple[str, PdfUrl]]
    notes: List[str]


def scrape_all_bill_progs():
    progress_page_src = reqs_get_wa_parli(progress_of_bills_url).text
    page = BeautifulSoup(progress_page_src, 'lxml')
    prog_table = page.find("table", {'class': "bil_prog_table"})
    rows: ResultSet = prog_table.find("tbody").find_all("tr")
    bill_progs = list()
    for tr_row in rows:
        tds: List[Tag] = list(tr_row.find_all("td"))
        bill_progs.append(BillProgress.from_tds(tds))
    return bill_progs
    # except Exception as e:
    #     continue


def a_tag_to_pair(a_tag: Tag) -> Tuple[str, PdfUrl]:
    label: str = a_tag.text.strip()
    return label, PdfUrl(str(waph_base_url / a_tag['href']))


def li_extract(snd_in_main_pair: Tag) -> List[Tuple[str, PdfUrl]]:
    li_links = snd_in_main_pair.find_all('li', {'class': 'liLink'})
    a_links: List[Tag] = list([li.find('a') for li in li_links])
    r: List[Tuple[str, PdfUrl]] = list(a_tag_to_pair(a) for a in a_links)
    return r


def progress_extract(prog_table: Optional[Tag]) -> List[Tuple[str, datetime]]:
    if prog_table is None:
        return list()
    rows = list(prog_table.find_all('tr'))[1:]
    return list((r[0].text.strip(), datetime.strptime(r[2].text.strip(), "%d %b %Y")) for r in
                (list(row.find_all('td')) for row in rows))


def scrape_bill_from_in_prog(bill_p: BillProgress) -> Tuple[BillProgress, Either[str, Bill]]:
    try:
        _d: TypedDict[Bill] = AttrDict(name=bill_p.name, bill_no=bill_p.bill_no, url=bill_p.url,
                                       bill_progress=Just(bill_p))
        page = BeautifulSoup(reqs_get_wa_parli(bill_p.url).text, 'lxml')
        # name, bill_no, synopsys, status
        heading = page.find('table', {'class': 'billHeading'})
        if heading is None:
            print(heading)
            print(page)
        heading_tds = list(heading.find_all('td'))
        _d.name = heading_tds[0].text.strip()
        _d.bill_no = heading_tds[2].text.strip()
        _d.synopsis = heading_tds[4].text.strip()
        _d.private_members_bill = Just(heading_tds[5].text.strip()) if len(heading_tds) != 7 else Nothing
        _d.status = heading_tds[6 if _d.private_members_bill.is_nothing() else 7].text.strip()
        main_info = heading.find_next_sibling('table')
        top_level_trs = main_info.find_all('tr', recursive=False, )
        main_row_paris = chunks(top_level_trs, 2)
        _d.bill_history = li_extract(main_row_paris.__next__()[1])
        _d.acts_amended = li_extract(main_row_paris.__next__()[1])
        _d.related_committee_activity = li_extract(main_row_paris.__next__()[1])
        _d.lc_supplementary = li_extract(main_row_paris.__next__()[1])
        _d.messages = li_extract(main_row_paris.__next__()[1])
        progress_table = main_row_paris.__next__()[1].find('table')
        la_table = None if progress_table is None else progress_table.find('table', {'class': 'bil_table_LA'})
        lc_table = None if progress_table is None else progress_table.find('table', {'class': 'bil_table_LC'})
        _d.progress_la = progress_extract(la_table)
        _d.progress_lc = progress_extract(lc_table)
        superseded_pair = main_row_paris.__next__()
        _d.superseded_lc_supplementary = li_extract(superseded_pair[1])
        comparison_1: Tag = main_row_paris.__next__()[1]
        comparison_2: Tag = main_row_paris.__next__()[0]
        # we're now offset by 1 to account for an extra row
        _d.comparisons_between_version = (li_extract(comparison_1), li_extract(comparison_2))
        _d.conference_of_managers = li_extract(main_row_paris.__next__()[0])
        if len(_d.conference_of_managers) > 0:
            print(f"found conference_of_managers? {_d.conference_of_managers}")
        _d.notes = list(td.text for td in main_row_paris.__next__()[0].find_all('td'))
        return bill_p, Right(Bill(**_d))
    except Exception as e:
        import traceback
        log.error(f"scrape_bill_from_in_prog ({bill_p.name}) Error: {e}\n\n{traceback.format_tb(e.__traceback__)}")
        return bill_p, Left(str(e))


def scrape_all_bills(bills_progs=None, par_reqs=50) -> List[Tuple[BillProgress, Either[str, Bill]]]:
    bills_progs = bills_progs if bills_progs is not None else scrape_all_bill_progs()
    with Pool(par_reqs) as pool:
        log.info(f"Starting scrape of {len(bills_progs)} bills with {par_reqs} parallel workers.")
        return pool.map(scrape_bill_from_in_prog, bills_progs, par_reqs)
