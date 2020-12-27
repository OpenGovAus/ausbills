# Aus Bills

🇦🇺 This is a package is for obtaining parliament bills for Australian governments.

## Install via pip

```
pip install ausbills
```

Current governments that are supported:

- Australian Federal Government
- Australian Capital Territory Government

---

## Australian Federal Government

This module had methods for scraping the [Australian Federal Parliament](https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726) website, using _beautiful soup_.

The bills are scraped to get data from both the house and the senate:

```python
from ausbills.federal_parliment import get_all_bills, Bill
all_bills = get_all_bills()
print(all_bills)
bill_five = all_bills[5]
```

`all_bills.data` is a list of all current bills and some basic data in the form of a dict. The rest of the data may be obtained via the **Bill()** object.

```python
bill = Bill(bill_id=bill_five["id"])
print(bill.summary)
print(bill.sponsor)
print(bill.bill_text_links)
print(bill.explanatory_memoranda_links)
```

_or_ you can use the url string to create an instance of **Bill()**:

```python
bill = Bill(bill_five["url"])
```

_or_ the id

```python
bill = Bill(bill_five["id"])
```

You may also change the date format:

```python
bill = Bill(bill_five["id"],"DD/MM/YYYY")
```

and you can get the data dump as a dict:

```python
bill.data
```

---

## NSW Government

Using the ```nsw_parliament``` module, you can scrape bills from the [NSW Parliament website](https://www.parliament.nsw.gov.au/bills/pages/all-bills-1997.aspx)

Use ```nsw_all_bills``` to return a list of bill dicts (each dict represents an individual bill).
```python
from ausbills.nsw_parliament import nsw_all_bills

print(nsw_all_bills)
print('The first bill returned: ' + nsw_all_bills[0])
```

You can return more data on an individual bill using the **nsw_Bill** object:

```python
from ausbills.nsw_parliament import nsw_all_bills, nsw_Bill

all_the_bills_mate = nsw_all_bills
print(nsw_Bill(all_the_bills_mate).status)
```

---

## ACT Government

This module allows you to scrape bill data from the [Australian Capital Territory Legislative Assembly](https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills/summary_of_bills) website using _beautiful soup_.

Similarly to the Federal Parliament and WA modules, you can scrape all the bills like this:

```python
from ausbills.act_parliament import act_all_bills as all_bills

print(all_bills)
print('The 5th Bill is ' + all_bills[4])
```

You can interact with individual bills with the **act_Bill()** object:
```python
all_the_bills = all_bills
some_bill = act_Bill(all_the_bills[5])
print(some_bill.title)
```

---

## Queensland Government

This module integrates with the [Queensland government's legislation site](https://www.legislation.qld.gov.au/) to pull bills.

Queensland is a bit different to the other jurisdictions' modules, because it returns its bills in a JSON format. However returning the bills still works the same way:

Return all bills in a list:

```python
from ausbills.qld_parliament import qld_all_bills, qld_Bill

bills_list = qld_all_bills
print(bills_list[45])
```

To get more data from an individual bill, use the **qld_Bill** class:

```python
from aubills.qld_parliament import qld_all_bills, qld_Bill

some_bill_mate = qld_all_bills[72]
bill_obj = qld_Bill(some_bill_mate)

# Print the Explanatory Note URL:
print('Click me:\n' + bill_obj.explanatory_note)
```

---

## Contributing

We mostly use **BeautifulSoup** to scrape the bills from the Bills websites. so make sure you become familiar with the docs [here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

We use **json** for the Queensland site, so get familiar with that [here](https://docs.python.org/3/library/json.html):

Fork the repo and install requirements

```
pip3 install -r requirements.txt
```

Each state should their own bills and corresponding website. Add a python file for a new state in the /ausbills dir. the python file should have the naming convention: [`wa_parliment.py`](ausbills/wa_parliment.py) for [_Western Australia_](https://www.parliament.wa.gov.au/parliament/bills.nsf/screenWebCurrentBills) for example. Make sure we all agree on method/object/output conventions (use federal_bills as a guide). Once you are happy, update the README on method usage and make a Pull Request.

---

#### Upgrade package

Change VERSION in [setup.py](setup.py), then:

```
git tag -a 0.1.0 -m "update version 0.1.0"
git push origin 0.1.0
```



### Todo

- Write better usage docs
