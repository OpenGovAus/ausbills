from ausbills.act_parliament import act_all_bills, act_Bill
import pytest
import random
import io

def test_act():
    all_the_bills_mate = act_all_bills
    random_numbers = [int(random.random()*len(all_the_bills_mate)) for i in range(5)]
    bills_sample = [all_the_bills_mate[i] for i in random_numbers]
    file = open('act_demo.txt', 'w')

    file.write('Found ' + str(len(all_the_bills_mate)) + ' bills:\n\n')
    for bill in bills_sample:
        write_text = []
        bill_data = act_Bill(bill)
        write_text.append('Bill Title: ' + bill_data.title + ', ' + bill_data.date)
        write_text.append('\nBill URL: ' + bill_data.url)
        write_text.append('\nBill Text URL: ' + bill_data.bill_text_url)
        write_text.append('\nBill Presentation Speech URL: ' + bill_data.presentation_speech)
        write_text.append('\nBill Type: ' + bill_data.bill_type)
        write_text.append('\nBill Presenter: ' + bill_data.presented_by)
        for text in write_text:
            file.writelines(text)
        file.writelines('\n\n')