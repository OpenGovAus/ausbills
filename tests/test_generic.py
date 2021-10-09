import os
import sys
import pytest
import random
import logging
import importlib
from dataclasses import dataclass

from ausbills.models import BillMeta, Bill

logging.basicConfig(level=logging.DEBUG)

parlname = ''

@pytest.fixture()
def parliament(pytestconfig):
    return pytestconfig.getoption("parl")

@pytest.fixture
def parl_module(parliament):
    spec = importlib.util.spec_from_file_location(
        'parl', f'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}/ausbills/parliament/{parliament}.py')
    parl = importlib.util.module_from_spec(spec)
    sys.modules['parl'] = parl
    spec.loader.exec_module(parl)
    return parl

@pytest.fixture
def bills_meta_sample(parl_module):
    bills_metadata = parl_module.get_bills_metadata()
    random_numbers = [int(random.random()*len(bills_metadata)) for i in range(5)]
    bills_meta_sample = [bills_metadata[i] for i in random_numbers]
    return(bills_meta_sample)


def test_get_bills_meta(bills_meta_sample):
    for b_m in bills_meta_sample:
        assert isinstance(b_m, BillMeta)
        print("test_get_bills_meta: "+str(b_m))


def test_get_bills(bills_meta_sample, parl_module):
    for b_m in bills_meta_sample:
        assert isinstance(b_m, BillMeta)
        bill_info = parl_module.get_bill(b_m)
        assert isinstance(bill_info, Bill)

def test_bill_dict(bills_meta_sample, parl_module):
    for b_m in bills_meta_sample:
        bill_info = parl_module.get_bill(b_m)
        b_dict =bill_info.asDict()
        assert isinstance(b_dict, dict)
        print("Bill Dict" + str(b_dict))

def test_bill_json(bills_meta_sample, parl_module):
    for b_m in bills_meta_sample:
        bill_info = parl_module.get_bill(b_m)
        b_json =bill_info.asJson()
        assert isinstance(b_json, str)
