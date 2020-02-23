# Aus Bills

This is a package is for obtaining parliament bills for Australian governments.

## Install via pip

```
pip3 install git+https://github.com/KipCrossing/Aus-Bills
```

Current governments that are supported:

- Australian Federal Government

## Contributing

Fork the repo and install requirements

```
pip3 install -r requirements.txt
```

Each state should their own bills and corresponding website. Add a python file for a new state in the /ausbills dir. the python file should have the naming convention: `wa_bills.py` for _Western Australia_ for example. Make sure we all agree on method/object/output conventions (use federal_bills as a guide). Once you are happy, update the README on method usage and make a Pull Request.

## Australian Federal Government

This module had methods for scraping the [Australian Federal Parliament](https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726) website, using _beautiful soup_.

The bills are scraped to get data from both the house and the senate:

```python
from ausbills.federal_parliment import All_Bills, Bill
all_bills = All_Bills()
print(all_bills.data)
bill_five = all_bills.data[5]
```

`all_bills.data` is a list of all current bills and some basic data in the form of a dict. The rest of the data may be obtained via the **Bill** object. To initialise a **Bill** object:

```python
bill = Bill(bill_five)
print(bill.summary)
print(bill.sponsor)
print(bill.bill_text_links)
print(bill.explanatory_memoranda_links)
```

## TheVoteForYou API

_Under dev_

I decided (for now) to add functions to obtain relevant data via the [TheyVoteForYou API](https://theyvoteforyou.org.au/help/data).

### Todo

- bills in All_Bills ?
- get more bill data
