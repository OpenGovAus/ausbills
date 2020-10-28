from ausbills.qld_parliament import qld_all_bills, qld_Bill
import pytest
import random
import io

def test_qld():
    all_the_bills_mate = qld_all_bills
    file = open('qld_demo.txt', 'w')
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(10)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]
    for _bill in bills_sample:
        b = qld_Bill(_bill)
        file.write(b.short_title + ' - ' + b.url + ' - ' + b.date +'\n' +
        'Explanatory Note: ' + b.explanatory_note + '\n\n')
        print(b.url)