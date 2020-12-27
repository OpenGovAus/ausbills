import logging

from ausbills.util.digicert_certs import *

logging.basicConfig(level=logging.INFO)

import pytest
import requests

from ausbills.wa_parliament import *
from tests.utils import read_data


def test_wa_bill_prog_1_house():
    page = BeautifulSoup(reqs_get_wa_parli(progress_of_bills_url).text, 'lxml')
    tds = page.find_all('td')
    b1 = BillProgress1House.from_tds(House.LOWER, tds[2:8])
    b2 = BillProgress1House.from_tds(House.UPPER, tds[8:14])
    assert b1 is not None and b2 is not None and isinstance(b1, BillProgress1House) and isinstance(b2,
                                                                                                   BillProgress1House)


def test_read_snd_and_hansard():
    tr: Tag = BeautifulSoup(read_data("test_read_snd_and_hansard_tr_1.txt"), 'lxml').find('tr')
    r1 = BillProgress1House.read_snd_and_hansard(tr.find_all('td')[3])
    r2 = BillProgress1House.read_snd_and_hansard(tr.find_all('td')[9])
    assert r1.is_just() and r2.is_just()


def test_scrape_all_bills():
    bs = scrape_all_bill_progs()
    assert isinstance(bs, list) and len(bs) > 50 and all(isinstance(b, BillProgress) for b in bs)
