from bs4 import BeautifulSoup
import requests
import datetime

bills_legislation_url = "https://www.parliament.wa.gov.au/parliament/bills.nsf/screenWebCurrentBills"


class All_Bills(object):
    _bills_data = []

    def __init__(self):
        pass

    @property
    def data(self):
        return(self._bills_data)


all_bills = All_Bills().data


class Bill(object):

    def __init__(self, input):
        pass
