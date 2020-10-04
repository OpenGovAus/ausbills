import json
import os
from pathlib import Path

from slugify import slugify

from ausbills.json_encoder import AusBillsJsonEncoder
from ausbills.wa_parliment import *

# bills_folder = Path(f'wa_bills_out_{int(time())}')
bills_folder = Path(f'wa_bills_out')


def main():
    bills_progs = scrape_all_bill_progs()
    print(f"got {len(bills_progs)} bills in progress")
    results = scrape_all_bills(bills_progs=bills_progs)
    print(f"got results")
    if not os.path.exists(bills_folder):
        os.mkdir(bills_folder)
    for i, (bp, bill_e) in enumerate(results):
        bp: BillProgress
        bill_e: Either[str, Bill]
        if bill_e.is_left():
            log.error(f"Unable to retrieve bill {bp.name}.\nError: {bill_e.l_value}")
            continue
        b: Bill = bill_e.value

        with open(bills_folder / f'{slugify(b.name)}.json', 'w') as f:
            json.dump(b, f, cls=AusBillsJsonEncoder, indent=2)
        print(f"Done {i} / {len(bills_progs)} -- {i / len(bills_progs) * 100:05.2f}%")


if __name__ == "__main__":
    main()
