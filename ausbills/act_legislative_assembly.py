from bs4 import BeautifulSoup
import requests
import datetime

ninth_assembly_bills = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills/summary_of_bills"
ninth_assembly_bills_meta = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/bills/bills_volume"
eighth_assembly_bills = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/bills_list"
eighth_assembly_bills_meta = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/bills_volume"

class All_Bills(object):
    _bills_data = []

    def __init__(self):
        self._build_dataset()

    def _build_dataset(self):
        ninth_siteData = requests.get(ninth_assembly_bills).text
        eighth_siteData = requests.get(eighth_assembly_bills).text
            
        try:
            soup = BeautifulSoup(ninth_siteData, 'html.parser')
            div = soup.find("div", {"id": "main"})
            billTitles = div.find_all('h4')
            billData = div.find_all('p')[4:]
            billPres = []
            billDescs = []

            for entry in billData:
                if "<strong>" in str(entry):
                    billPres.append(entry)

                elif not "<strong>" in str(entry):
                    billDescs.append(entry)            

        except Exception as e:
                    print('An exception has happened mate')
                    print(e)