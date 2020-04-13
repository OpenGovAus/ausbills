from ausbills.federal_parliment import all_bills, Bill
import json

outlist = []

for bill in all_bills:
    b_data = Bill(bill["id"]).data
    print(b_data["short_title"])
    outlist.append(b_data)

with open('bill_data.json', 'w') as outfile:
    json.dump(outlist, outfile)
