# Aus Bills

This is a package is for obtaining parliament bills for Australian governments.

### Install via pip

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

Each state should their own bills and corresponding website. Add a python file for a new state in the /ausbills dir. the python file should have the naming convention: `wa_bills.py` for *Western Australia* for example. Make sure we all agree on method/object/output conventions (use federal_bills as a guide). Once you are happy, update the README on method usage and make a Pull Request.

## Australian Federal Government

This module had methods for scraping the [Australian Federal Parliament](https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726) website, using _beautiful soup_, and send to separate Senate and House of Representatives Discord channels as embeds that can be called throughout Discord server.

The bills are scraped to get data from upper(senate) and lower house:

```python
from ausbills import federal_bills
federal_bills.get_house_bills()
federal_bills.get_senate_bills()
#returns a list of dicts
```

And can easily be turned into pandas dataframes:

```python
import pandas as pd
df_lower = pd.DataFrame(federal_bills.get_house_bills())
df_upper = pd.DataFrame(federal_bills.get_senate_bills())
```

You and get bill details buy providing the url string. For example:

```python
print(federal_bills.get_bill_summary(url))
```

## TheVoteForYou API

*Under dev*

I decided (for now) to add functions to obtain relevant data via the [TheyVoteForYou API](https://theyvoteforyou.org.au/help/data). This is in [ausbills/federal_theyvote.py](ausbills/federal_theyvote.py).
