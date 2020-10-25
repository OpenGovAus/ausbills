from ausbills.sa_parliament import sa_all_bills, sa_Bill
import pytest
import random

def test_sa():
    all_the_bills_mate = sa_all_bills
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(5)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]

    for bill in bills_sample:
        b = sa_Bill(bill)
        print(b.short_title)
        print(b.data)