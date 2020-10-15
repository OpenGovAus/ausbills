from ausbills.nsw_parliament import nsw_all_bills, nsw_Bill
import random
import io
import pytest

def test_nsw():
    all_the_bills_mate = nsw_all_bills
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(5)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]

    file = open('nsw_demo2.txt', 'w')
    for bill in bills_sample:
        b = nsw_Bill(bill)
        file.write(str(b.data) + '\n')