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
eighth_assembly_bills = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/summary_of_bills"
eighth_assembly_bills_meta = "https://www.parliament.act.gov.au/parliamentary-business/in-the-chamber/previous-assemblies/eighth-assembly/bills_volume"
ninth_siteData = requests.get(ninth_assembly_bills).text
eighth_siteData = requests.get(eighth_assembly_bills).text

class All_Bills(object):
    _bills_data = [] # This list will end up containing all the bill dict entries, and is the data returned.

    def __init__(self):
        self._build_dataset()

    def _build_dataset(self):
        try:
            self._scrape_9th_assembly()
        except Exception as e:
            print('An exception ocurred when trying to scrape the 9th Assembly:\n')
            print(e)
    
        try:
            self._scrape_8th_assembly()
        except Exception as e:
            print('An exception ocurred when trying to scrape the 8th Assembly:\n')
            print(e)

    def _scrape_9th_assembly(self):
        billPres = []
        billDescs = []

        soup = BeautifulSoup(ninth_siteData, 'html.parser')
        div = soup.find("div", {"id": "main"})
        billTitles = div.find_all('h4')
        for h4 in div.find_all('h4'): 
            h4.replace_with('') # Remove all <h4>s from the soup, this makes it less annoying to get the bill presenter string from <strong> tags. The ACT Government, man, it's weird.

        billData = div.find_all(re.compile(r'(div|p)'))
        allStrong = div.find_all('strong')
        dumbDebug = []
        for strong in range(len(allStrong)):
            if('This bill' in allStrong[strong].text or 'e bill will also' in allStrong[strong].text):
                pass
            else:
                billPres.append(allStrong[strong])
        for entry in billData:
            if "This bill" in entry.text or "this bill" in entry.text:
                billDescs.append(entry)

        for title in range(len(billTitles)): # Here we loop through every bill and compile its information into an entry in _bills_data
            _bill_title = billTitles[title].text
            a = billTitles[title].find('a')
            if(a == None):
                _bill_url = ''
            else:
                _bill_url = a['href']
            _bill_description = billDescs[title].text
            _bill_presented_by = self._format_presenter_9th(billPres[title].text)[0][13:]
            _bill_date = self._format_presenter_9th(billPres[title].text)[1]

            bill_dict = {URL: _bill_url, TITLE: _bill_title, DESCRIPTION: _bill_description.replace("\xa0\xa0", " ").replace('‑', '-'), PRESENTED_BY: _bill_presented_by, DATE: _bill_date}

            self._bills_data.append(bill_dict)

    def _format_presenter_9th(self, title):
        formatted = []
        splitUp = title.replace('\xa0', ' ').split('—', 1)
        formatted.append(splitUp[0])
        dateSplit = splitUp[1].split(' ', 2)
        monthNum = list(calendar.month_name).index(dateSplit[1])
        finalDate = dateSplit[2] + '-' + "{0:0=2d}".format(monthNum) + '-' + "{0:0=2d}".format(int(dateSplit[0]))
        formatted.append(finalDate)
        return(formatted)

    def _scrape_8th_assembly(self):
        billDescs = []
        billTitles = []
        billScrutinyReports = []

        soup = BeautifulSoup(eighth_siteData, 'html.parser')
        div = soup.find('div', {'id': 'main'})
        paras = div.find_all('p')[8:]
        for p in range(len(paras)):
            if "<strong>" in str(paras[p]):
                billTitles.append(paras[p])

            elif "y Report " in str(paras[p]) or "Statement" in str(paras[p]):
                reports = paras[p].find_all('a', {'href': True})
                urls = []
                for report in range(len(reports)):
                    urls.append(reports[report]['href'])
                billScrutinyReports.append(urls)
            
            else:
                billDescs.append(paras[p].text.replace('‑', '-'))

        for bill in range(len(billTitles)):
            _bill_title = self._format_presenter_8th(billTitles[bill].text)[0].replace('‑', '-')
            _bill_presented_by = self._format_presenter_8th(billTitles[bill].text)[1].replace('‑', '-')
            _bill_date = self._format_presenter_8th(billTitles[bill].text)[2].replace('‑', '-')
            _bill_url = billTitles[bill].find('a')['href']
            _bill_description = billDescs[bill].replace('‑', '-')
            bill_dict = {TITLE: _bill_title, URL: _bill_url, DESCRIPTION: _bill_description, DATE: _bill_date, PRESENTED_BY: _bill_presented_by}
            self._bills_data.append(bill_dict)

    def _format_presenter_8th(self, title):
        count = 0
        formatted = []

        for char in title:
            if char == '—':
                count = count + 1

        if count > 2:
            title = title.replace('—', ' - ', 1) # The bill https://www.legislation.act.gov.au/b/db_47854/default.asp contains an extra '—', this hacks around it. 

        splitUp = title.replace('\xa0', ' ').split('—', 2)
        formatted.extend([splitUp[0], splitUp[1]])
        if(splitUp[2][0] == ' '): # The Gaming Machine Amendment Bill 2013 (No. 2) contains a space before the "6" in its date (of course), so we need to do this, otherwise funky things happen.
            edit = splitUp[2][1:]
            splitUp.remove(splitUp[2])
            splitUp.append(edit)
        dateSplit = splitUp[2].split(' ', 2)
        monthNum = list(calendar.month_name).index(dateSplit[1])
        finalDate = dateSplit[2] + '-' + "{0:0=2d}".format(monthNum) + '-' + "{0:0=2d}".format(int(dateSplit[0]))
        formatted.append(finalDate)
        return(formatted)

    @property
    def data(self):
        return(self._bills_data)

act_all_bills = All_Bills().data

class Bill(object):
    _all_bills = act_all_bills
