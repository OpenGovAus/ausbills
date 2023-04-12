import json
import os
import sys

from ausbills.parliament.wa import get_bills_metadata, get_bill

FILEPATH = os.path.dirname(os.path.realpath(__file__)) + "/example_exports/"


def main():
    bill_list = [get_bill(bill).asDict() for bill in get_bills_metadata()]

    with open(FILEPATH + "wa_bills.json", "w") as f:
        f.write(json.dumps(bill_list, indent=2))


if __name__ == "__main__":
    if not os.path.isdir(FILEPATH):
        try:
            os.mkdir(FILEPATH)
        except WindowsError:
            sys.exit(f'Could not create directory "{FILEPATH}"')
    main()
