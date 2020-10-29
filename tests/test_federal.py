from ausbills.federal_parliment import get_all_bills, get_bills_metadata
import datetime
import random

import logging

# from ausbills.util.digicert_certs import *

logging.basicConfig(level=logging.INFO)

import pytest
import requests

CHAMBER = "chamber"
SHORT_TITLE = "short_title"
INTRO_HOUSE = "intro_house"
PASSED_HOUSE = "passed_house"
INTRO_SENATE = "intro_senate"
PASSED_SENATE = "passed_senate"
ASSENT_DATE = "assent_date"
URL = "url"
ACT_NO = "act_no"
ID = "id"


def test_get_bills_meta():
    bills_metadata =get_bills_metadata()
    random_numbers = [int(random.random()*len(bills_metadata)) for i in range(5)]
    bills_meta_sample = [bills_metadata[i] for i in random_numbers]
    for b_m in bills_meta_sample:
        print(b_m)

def test_federal_all_bills():
    all_bills = get_all_bills()
    random_numbers = [int(random.random()*len(all_bills)) for i in range(5)]

    bills_sample = [all_bills[i] for i in random_numbers]

    NoneType = type(None)

    assert isinstance(all_bills, list)

    for bd in bills_sample:
        assert isinstance(bd[URL], str)
        print(bd[ID] + " - " + bd[SHORT_TITLE])
        print(bd.keys())
        assert '=' in bd[URL]
        assert bd[URL].split(':')[0] in ['http', 'https']
        assert bd[CHAMBER] in ["House", "Senate"]
        assert isinstance(bd[SHORT_TITLE], str)
        assert isinstance(bd[INTRO_HOUSE], (datetime.date, NoneType))
        assert isinstance(bd[PASSED_HOUSE], (datetime.date, NoneType))
        assert isinstance(bd[INTRO_SENATE], (datetime.date, NoneType))
        assert isinstance(bd[PASSED_SENATE], (datetime.date, NoneType))
        assert isinstance(bd[ASSENT_DATE], (datetime.date, NoneType))
        # assert isinstance(bd[ACT_NO], (int, NoneType))

        # Do the bill tests better

        # b = Bill(bill_id=bd[ID])
        # assert isinstance(b.summary, str)
        # assert isinstance(b.url, str)
        # assert isinstance(b.intro_house, (datetime.date, NoneType))
        # assert isinstance(b.sponsor, str)
        # assert isinstance(b.bill_text_links, dict)
        # assert isinstance(b.explanatory_memoranda_links, dict)
        # assert isinstance(b.data, dict)
        # assert isinstance(b.data[INTRO_HOUSE], str)
        # assert isinstance(b.portfolio, str)
        # print(b.portfolio, b.sponsor)