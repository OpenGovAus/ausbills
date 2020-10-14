import json
import time

from ausbills.json_encoder import AusBillsJsonEncoder
from ausbills.wa_parliment import scrape_all_bill_progs


bill_progs = scrape_all_bill_progs()
print(f"Scraped {len(bill_progs)} bills in progress from WA parliament website.")
with open(f'bill_progs_{int(time.time())}.tmp.json', 'w') as f:
    json.dump(bill_progs, f, indent=2, cls=AusBillsJsonEncoder)
