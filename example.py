from ausbills.federal_parliment import all_bills, Bill
import json
import random

outlist = []

for bill in all_bills:
    b_data = Bill(bill["id"]).data
    print(b_data["short_title"])
    b_data["yes"] = 500 + int(random.random()*500)
    b_data["no"] = 500 + int(random.random()*500)
    b_data["ballotspec_hash"] = "blahblahblahblahblahblahblahblahblah"
    outlist.append(b_data)

with open('bill_data.json', 'w') as outfile:
    json.dump(outlist, outfile)
