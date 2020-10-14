import random
from act_legislative_assembly import act_all_bills as all_bills, act_Bill as Bill

all_the_bills_mate = all_bills
print('Found ' + str(len(all_the_bills_mate)) + ' bills.')
rand = [int(random.random()*len(all_the_bills_mate)) for i in range(5)]

for num in rand:
    the_current_bill_mate = Bill(all_the_bills_mate[num])
    print(the_current_bill_mate.title + ':')
    print(the_current_bill_mate.url)
    print('Presented by ' + the_current_bill_mate.presented_by + ' on ' + the_current_bill_mate.date)
    print(the_current_bill_mate.description + '\n\n')