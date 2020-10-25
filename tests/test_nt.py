from ausbills.nt_parliament import nt_all_bills, nt_Bill
import pytest
import random
import io

def test_act():
    all_the_bills_mate = nt_all_bills
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(25)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]
    file = open('nt_demo.txt', 'w')

    for bill in bills_sample:
        b = nt_Bill(bill)
        print(b.data)
        file.write(b.short_title + ' - ' + b.sponsor + ' introduced bill on: ' + b.intro_date + ', current: ' + b.date + '\n\n')