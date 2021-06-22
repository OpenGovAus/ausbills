from ausbills.parliament.nt import *
import pytest
import random
import io
import logging

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def bills_meta_sample():
    bills_metadata = get_bills_metadata()
    random_numbers = [int(random.random()*len(bills_metadata)) for i in range(5)]
    bills_meta_sample = [bills_metadata[i] for i in random_numbers]
    return(bills_meta_sample)

def test_get_bills_meta(bills_meta_sample):
    for b_m in bills_meta_sample:
        assert isinstance(b_m, BillMeta)
        print("test_get_bills_meta: "+str(b_m))

def test_get_bills(bills_meta_sample):
    for b_m in bills_meta_sample:
        assert isinstance(b_m, BillMeta)
        bill_info = get_bill(b_m)
        assert isinstance(bill_info, Bill)

def test_bill_dict(bills_meta_sample):
    for b_m in bills_meta_sample:
        bill_info = get_bill(b_m)
        b_dict =bill_info.asDict()
        assert isinstance(b_dict, dict)
        print("Bill Dict" + str(b_dict))

def test_bill_json(bills_meta_sample):
    for b_m in bills_meta_sample:
        bill_info = get_bill(b_m)
        b_json =bill_info.asJson()
        assert isinstance(b_json, str)