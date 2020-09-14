# Aus Bills

This is a package is for obtaining parliament bills for Australian governments.

## Install via pip

```
pip install ausbills
```

Current governments that are supported:

- Australian Federal Government
- Australian Capital Territory Legislative Assembly

---

## Australian Federal Government

This module had methods for scraping the [Australian Federal Parliament](https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726) website, using _beautiful soup_.

The bills are scraped to get data from both the house and the senate:

```python
from ausbills.federal_parliment import all_bills, Bill
print(all_bills)
bill_five = all_bills[5]
```

`all_bills.data` is a list of all current bills and some basic data in the form of a dict. The rest of the data may be obtained via the **Bill()** object.

```python
bill = Bill(bill_five)
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

## Contributing

We use **BeautifulSoup** to scrape the bills from the Bills websites. so make sure you become familiar with the docs [here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

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

---
## Australian Capital Territory Legislative Assembly Bills

### ACT Legislative Assembly Todo
#### Get Bills:
##### Bills from 9th Assembly:
- Get list of bill names found @ https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills/summary_of_bills
- Get bill metadata from https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills/bills_volume

##### Bills from previous Assemblies:
###### 8th Assembly (Will encompass 9th assembly at the end of 2020):
- Get list of bill names from https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/bills_list
- Get bill metadata from https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/bills_volume

###### 1st - 7th Assemblies:
Unfortunately, the ACT Government stores these bill lists as PDF files that don't follow a directory pattern. Instead they're stored in generated SquizMatrix directories. It's easy to scrape the file location though, the only annoying part is scraping the PDFs themselves.

- Get bill metadata from https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/business6/ + appended volume ID

The volume ID differs from Assembly to Assembly and doesn't follow a pattern, but are unlikely to change since different parliamentary sites pull data from these lists, so it's 99% safe to hard-code the URLs, and would be very easy to change should the host files change.

