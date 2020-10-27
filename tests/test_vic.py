from ausbills.vic_parliament import vic_all_bills
import pytest
import random
import io

def test_vic():
    all_the_bills_mate = vic_all_bills
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(5)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]

    for bill in bills_sample:
        print(bill)