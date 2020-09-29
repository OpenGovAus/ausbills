from bs4 import BeautifulSoup
import requests
import datetime
import calendar
import re

DATE = 'date'
URL = 'url'
TITLE = 'title'
DESCRIPTION = 'description'
PRESENTED_BY = 'presented_by'

ninth_assembly_bills = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills/summary_of_bills"
ninth_assembly_bills_meta = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills/bills_volume"
eighth_assembly_bills = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/bills_list"
eighth_assembly_bills_meta = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/bills_volume"
ninth_siteData = requests.get(ninth_assembly_bills).text
eighth_siteData = requests.get(eighth_assembly_bills).text

class All_Bills(object):
    _bills_data = [] # This list will end up containing all the bill dict entries, and is the data returned.

    def __init__(self):
        self._build_dataset()

    def _build_dataset(self):
        try:
            _bills_data = [] # This list will end up containing all the bill dict entries, and is the data returned.
            billPres = []
            billDescs = []

            soup = BeautifulSoup(ninth_siteData, 'html.parser')
            div = soup.find("div", {"id": "main"})
            billTitles = div.find_all('h4')
            for h4 in div.find_all('h4'): 
                h4.replace_with('') # Remove all <h4>s from the soup, this makes it less annoying to get the bill presenter string from <strong> tags. The ACT Government, man, it's weird.

            billData = div.find_all(re.compile(r'(div|p)'))
            billPres = div.find_all('strong')
            for entry in billData:
                if "This bill" in entry.text or "this bill" in entry.text:
                    billDescs.append(entry)

            for title in range(len(billTitles)): # Here we loop through every bill and compile its information into an entry in _bills_data
                _bill_title = billTitles[title].text
                _bill_url = billTitles[title].find('a')['href']
                _bill_description = billDescs[title].text
                _bill_presented_by = self._format_presenter(billPres[title].text)[0][13:]
                _bill_date = self._format_presenter(billPres[title].text)[1]
                bill_dict = {URL: _bill_url, TITLE: _bill_title, DESCRIPTION: _bill_description.replace("\xa0\xa0", " "), PRESENTED_BY: _bill_presented_by, DATE: _bill_date}

                self._bills_data.append(bill_dict)

        except Exception as e:
            print(e)

    def _format_presenter(self, date):
        formatted = []
        splitUp = date.replace('\xa0', ' ').split('—', 1)
        formatted.append(splitUp[0])
        dateSplit = splitUp[1].split(' ', 2)
        monthNum = list(calendar.month_name).index(dateSplit[1])
        finalDate = dateSplit[2] + '-' + "{0:0=2d}".format(monthNum) + '-' + dateSplit[0]
        formatted.append(finalDate)
        return(formatted)

    @property
    def data(self):
        return(self._bills_data)

all_bills = All_Bills.data
print(all_bills)