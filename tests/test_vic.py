from ausbills.vic_parliament import vic_all_bills, vic_Bill
import pytest
import random
import json
import io

def test_vic():
    all_the_bills_mate = vic_all_bills
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(10)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]

    for bill in bills_sample:
        print(json.dumps(vic_Bill(bill).data, indent=2))