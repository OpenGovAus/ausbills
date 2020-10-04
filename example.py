import hashlib

from ausbills import json_encoder
from ausbills.federal_parliment import get_all_bills, Bill
import json
import random

out_list = []

for bill in get_all_bills():
    bill_obj = Bill(bill_id=bill["id"])
    b_data = bill_obj.data
    print(b_data["short_title"])
    print(bill_obj.data)
    print(dir(bill_obj))
    b_data["ballotspec_hash"] = hashlib.sha256(bill_obj.to_json().encode()).hexdigest()
    out_list.append(b_data)

with open('bill_data.json', 'w') as outfile:
    json.dump(out_list, outfile, cls=json_encoder.AusBillsJsonEncoder)
