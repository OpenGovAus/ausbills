from ausbills.tas_parliament import tas_all_bills, tas_Bill
import pytest
import random
import io

def test_tas():
    all_the_bills_mate = tas_all_bills
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(10)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]

    for _bill in bills_sample:
        b = tas_Bill(_bill)
        print(str(b.data) + '\n')