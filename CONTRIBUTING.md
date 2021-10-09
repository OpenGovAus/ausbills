# Contributing

To add a parliament that isn't supported by `ausbills` by using its functionality, use this guide (Scotland's parliament is used here for fun):

1. Find where bills are hosted; Scotland has theirs [here](https://www.parliament.scot/bills-and-laws/bills?qry=&billType=&billStage=&dateSelect=acfe09e8571447b6ac663f6362a20f42%7CWednesday%2C+June+9%2C+1971%7CWednesday%2C+June+9%2C+2021&showCurrentBills=true#results)

2. In [types.py](ausbills/types.py), add your parliament to the `Parliament` class:

    ```py
    class Parliament(Enum):
        FEDERAL = "FEDERAL"
        NSW = "NSW"
        WA = "WA"
        NT = "NT"
        QLD = "QLD"
        VIC = "VIC"
        SA = "SA"
        TAS = "TAS"
        ACT = "ACT"
        SCOTLAND = "SCOTLAND"
    ```

2. Create a file in `/ausbills/parliament/` with an appropriate name, like `scotland.py`

3. In that file, import the bill models and progress types, we use these for consistency, readability, and maintainability. You'll also need `dataclasses`:

    ```py
    import dataclasses
    from dataclasses import dataclass

    from ausbills.util import BillExtractor, BillListExtractor
    from ausbills.util.consts import *
    from ausbills.models import BillMeta, Bill
    from ausbills.types import BillProgress, ChamberProgress, Parliament
    from ausbills.log import get_logger
    ```

4. Create a logger, this should be used instead of `print`, etc

    ```py
    scotland_logger = get_logger(__file__)
    ```

5. Create a `dataclass` called BillMeta[Legislature], and make it extend `BillMeta`:

    ```py
    @dataclass
    class BillMetaScotland(BillMeta):
        pass
    ```
    This class will contain metadata obtainable from the online bill list that isn't already defined in `BillMeta`. This is what `BillMeta` looks like:

    ```py
    @dataclass
    class BillMeta:
        title: str
        link: UrlStr
        parliament: str
    ```
    These are the bare-minimum requirements for data to be obtained from the bill list (`parliament` will just be `Parliament.SCOTLAND.value`)

7. Add more fields for data that can be obtained by including them in your new `BillMeta[Legislature]` `dataclass`:

    ```py
    @dataclass
    class BillMetaScotland(BillMeta):
        bill_type: str
        progress: Dict
        chamber_progress: int
    ```

8. Create a `BillListExtractor` to scrape this data:

    ```py
    class ScotlandBillList(BillListExtractor):
        def __init__(self):
            self._scrape_data():
        
        @property
        def _webpage_data(self):
            return self._download_html('https://www.parliament.scot/bills-and-laws/bills?qry=&billType=&billStage=&dateSelect=acfe09e8571447b6ac663f6362a20f42%7CWednesday%2C+June+9%2C+1971%7CWednesday%2C+June+9%2C+2021&showCurrentBills=true#results')
        
        def _scrape_data(self):
            pass  # Magically return a list of bills from self._webpage_data
    ```

    `BillListExtractor` (an extension of `BillExtractor`) contains functions for downloading webpages and `JSON` URLs into usable `BeautifulSoup` or `json` data.

9. You'll now need to map that list to a `BillMeta[Legislature]` `dataclass` by defining a required function called `get_bills_metadata`

    ```py
    def get_bills_metadata():
        _all_bills = ScotlandBillList()._scrape_data()
        _bill_meta_list = []
        for bill_dict in _all_bills:
            bill_meta = BillMetaScotland(
                parliament=Parliament.SCOTLAND.value,
                progress=bill_dict[PASSED],
                title=bill_dict[TITLE],
                link=bill_dict[URL],
                bill_type=bill_dict[BILL_TYPE],
                chamber_progress=bill_dict[CHAMBER_PROGRESS]
            )
            _bill_meta_list.append(bill_meta)
        return(_bill_meta_list)
    ```
    This function will return a list of bills and associated metadata that can then be used individually with `get_bill` to obtain more data.

10. Create another `dataclass` called `Bill[Legislature]`, and follow the same steps as before, except this time, we're getting data from the bills' individual web pages, not the list page (e.g [one of these](https://www.parliament.scot/bills-and-laws/bills/european-charter-of-local-self-government-incorporation-scotland-bill))

    ```py
    @dataclass
    class BillScotland(Bill, BillMetaScotland):
        summary: str
        sponsor: str
    ```

11. Create a `BillExtractor` class. This will be responsible for scraping extra data for the new `dataclass`:

    ```py
    class ScotlandBillExtractor(BillExtractor):
        def __init__(self, bill_meta: BillMetaScotland):
            self.bill_soup = self._download_html(bill_meta.link)
        
        def _get_summary(self):
            pass  # Scrape the bill's summary

        def _get_sponsor(self):
            pass  # Scrape the bill's sponsor
            
        def _get_text_links(self):
            pass  # Scrape the URLs to the bill's legislative text
     ```

12. Now create `get_bill`. This function combines the metadata already extracted with the new data that can only be grabbed from the bill's URL:

    ```py
    def get_bill(bill_meta: BillMetaScotland) -> BillScotland:
        scotland_helper = ScotlandBillExtractor(bill_meta)
        bill_act = BillScotland(
            **dataclasses.asdict(bill_meta),  # Copy metadata we already got as separate instance.
            sponsor=scotland_helper._get_sponsor(),
            summary=scotland_helper._get_sponsor(),
            bill_text_links=scotland_helper._get_text_links()
        )
        return bill_act
    ```

13. Check and format your code with `flake8` (it should be included with `ausbills`'s dependencies).

    ```sh
    flake8 ausbills/parliament/scotland.py
    ```

    This should print any code standard errors (like long lines or unused imports) that should be fixed before creating a Pull Request.

## Testing

Once you've written your bill scraper, it needs to pass our generic test, you can check if it does by running this command:

```sh
py -m pytest -s tests/test_generic.py --parl '[parliament name]'
```

Where `'[parliament name]'` would be `'scotland'` in this case, since our module is written in `scotland.py`.

If the test does not pass, fix any errors and try again, etc etc.

You can also write a more specific test for your module if you think it's necessary.
