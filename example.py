import hashlib

from ausbills import json_encoder
from ausbills.federal_parliment import get_bills_metadata
from ausbills.wa_parliment import Bill, scrape_all_bill_progs, scrape_all_bills, BillProgress
from ausbills.wa_parliment import *
import json
import random
import os

out_list = []

for bill in get_bills_metadata():
    print(bill)

# with open('bill_data.json', 'w') as outfile:
#     json.dump(out_list, outfile, cls=json_encoder.AusBillsJsonEncoder)


# bills_progs = scrape_all_bill_progs()
# print(bills_progs[1].name)
# print(f"got {len(bills_progs)} bills in progress")
# results = scrape_all_bills(bills_progs=bills_progs)
# print(f"got results")
# # if not os.path.exists(bills_folder):
# #     os.mkdir(bills_folder)
# for i, (bp, bill_e) in enumerate(results):
#     bp: BillProgress
#     bill_e: Either[str, Bill]
#     if bill_e.is_left():
#         log.error(f"Unable to retrieve bill {bp.name}.\nError: {bill_e.l_value}")
#         continue
#     b: Bill = bill_e.value
#     print(b.name)

#     # with open(bills_folder / f'{slugify(b.name)}.json', 'w') as f:
#     #     json.dump(b, f, cls=AusBillsJsonEncoder, indent=2)
#     # print(f"Done {i} / {len(bills_progs)} -- {i / len(bills_progs) * 100:05.2f}%")