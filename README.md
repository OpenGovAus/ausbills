# Aus Bills Discord Bot

This is a package is for obtaining parliament bills for Australian governments.

### Install via pip

```
pip install git+https://github.com/KipCrossing/Aus-Bills
```

Current governments that are supported:

- Australian Federal Government

## Australian Federal Government

This module had methods for scraping the [Australian Federal Parliament](https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726) website, using _beautiful soup_, and send to separate Senate and House of Representatives Discord channels as embeds that can be called throughout Discord server.

The bills are scraped to get data from upper(senate) and lower house bills are:

```python
from ausbills import federal_bills
federal_bills.get_house_bills()
federal_bills.get_senate_bills()
```

And can easily be turned into pandas dataframes:

```python
df_lower = pd.DataFrame(federal_bills.get_house_bills())
df_upper = pd.DataFrame(federal_bills.get_senate_bills())
```
