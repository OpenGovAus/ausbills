import os
import sys
import pytest
import random
import logging
import importlib

from types import ModuleType
from typing import (
    Union,
    List
)
from ausbills.models import BillMeta, Bill

logging.basicConfig(level=logging.DEBUG)

parlname = ''

'''
This is the generic test. It can be used to test an individual
parliament by running:

    python -m pytest -s tests/test_generic.py --parl PARLIAMENT

Where PARLIAMENT would be the file name of the parliament's module without
".py", e.g to test the ACT, you would run:

    python -m pytest -s tests/test_generic.py --parl act

You can also pass "_test_all" to import every module in the parliament folder
and test each one.
'''


@pytest.fixture()
def parliament(pytestconfig) -> str:
    return pytestconfig.getoption("parl")


@pytest.fixture
def parl_module(parliament: str) -> Union[ModuleType, List[ModuleType]]:
    mods = f'{os.path.dirname(os.path.dirname(os.path.realpath(__file__)))}' \
           '/ausbills/parliament/'
    if parliament == '_test_all':
        modules = []
        for i in os.listdir(mods):
            if '.py' in i:
                mod_name = f'{i.replace(".py", "")}_parl'
                spec = importlib.util.spec_from_file_location(mod_name, mods + i)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)
                modules.append(mod)
        return modules
    else:
        spec = importlib.util.spec_from_file_location(
            'parl', f'{mods}{parliament}.py')
        parl = importlib.util.module_from_spec(spec)
        sys.modules['parl'] = parl
        spec.loader.exec_module(parl)
        return parl


@pytest.fixture
def bills_meta_sample(parl_module):
    def get_sample(parl):
        bills_metadata = parl.get_bills_metadata()
        random_numbers = [int(random.random()*len(bills_metadata)) for i in range(5)]
        bills_meta_sample = [bills_metadata[i] for i in random_numbers]
        return bills_meta_sample
    if isinstance(parl_module, list):
        return ([(get_sample(module), module) for module in parl_module], 'all')
    else:
        return (get_sample(parl_module), 'ind')


def test_get_bills_meta(bills_meta_sample):
    def actual_test(sample_list):
        for b_m in sample_list:
            assert isinstance(b_m, BillMeta)
            print("test_get_bills_meta: " + str(b_m))
    if bills_meta_sample[1] == 'ind':
        actual_test(bills_meta_sample[0])
    elif bills_meta_sample[1] == 'all':
        for parl_sample in bills_meta_sample[0]:
            actual_test(parl_sample[0])


def test_get_bills(bills_meta_sample, parl_module):
    def actual_test(sample_list, parl):
        for b_m in sample_list:
            assert isinstance(b_m, BillMeta)
            bill_info = parl.get_bill(b_m)
            assert isinstance(bill_info, Bill)
    if bills_meta_sample[1] == 'all':
        for parl_sample, module in bills_meta_sample[0]:
            actual_test(parl_sample, module)
    elif bills_meta_sample[1] == 'ind':
        actual_test(bills_meta_sample[0], parl_module)


def test_bill_dict(bills_meta_sample, parl_module):
    def actual_test(sample_list, parl):
        for b_m in sample_list:
            bill_info = parl.get_bill(b_m)
            b_dict = bill_info.asDict()
            assert isinstance(b_dict, dict)
            print("Bill Dict" + str(b_dict))
    if bills_meta_sample[1] == 'all':
        for parl_sample, module in bills_meta_sample[0]:
            actual_test(parl_sample, module)
    elif bills_meta_sample[1] == 'ind':
        actual_test(bills_meta_sample[0], parl_module)


def test_bill_json(bills_meta_sample, parl_module):
    def actual_test(sample_list, parl):
        for b_m in sample_list:
            bill_info = parl.get_bill(b_m)
            b_json = bill_info.asJson()
            assert isinstance(b_json, str)
    if bills_meta_sample[1] == 'all':
        for parl_sample, module in bills_meta_sample[0]:
            actual_test(parl_sample, module)
    elif bills_meta_sample[1] == 'ind':
        actual_test(bills_meta_sample[0], parl_module)
