from bs4 import BeautifulSoup
import requests
import datetime


CHAMBER = "Chamber"
SHORT_TITLE = "Short Title"
INTRO_HOUSE = "Intro House"
PASSED_HOUSE = "Passed House"
INTRO_SENATE = "Intro Senate"
PASSED_SENATE = "Passed Senate"
ASSENT_DATE = "Assent Date"
URL = "URL"
ACT_NO = "Act No."
DOC = "doc"
PDF = "pdf"
HTML = "html"
SUMMARY = "Summary"
SPONSOR = "Sponsor"
TEXT_LINK = "text link"
EM_LINK = "em link"
ID = "id"
READING = 'reading'

bills_legislation_url = "https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Lists/Details_page?blsId=legislation%2fbillslst%2fbillslst_c203aa1c-1876-41a8-bc76-1de328bdb726"


class All_Bills(object):
    _bills_data = []
    chambers = ["House", "Senate"]
    this_year = datetime.datetime.now().year

    def __init__(self):
        self._build_dataset()

    def _build_dataset(self):
        try:
            for i in range(2):
                self._scrape_data(i)
        except Exception as e:
            print("Link broken:")
            print(e)

    def _scrape_data(self, table_no):
        website_url = requests.get(bills_legislation_url).text
        soup = BeautifulSoup(website_url, 'lxml')
        tables = soup.find_all('table')
        trs = tables[table_no].findAll('tr')
        tr = trs.pop(0)
        self.headings = self._get_row_data(tr.findAll('td'))

        for tr in trs:
            try:
                bill_url_string = str(tr.a['href'])
                row_data = self._get_row_data(tr.findAll('td'))
                row_dict = {CHAMBER: self.chambers[table_no]}
                for i in range(len(self.headings)):
                    row_dict[self.headings[i]] = row_data[i]
                row_dict[URL] = bill_url_string
                row_dict[ID] = bill_url_string.split('?')[-1].split('=')[-1]
                row_dict[SHORT_TITLE] = row_dict[SHORT_TITLE].replace('\n', '').replace('    ', '').replace(
                    '\r', '').replace('\u2014\u0080\u0094', ' ').replace('\u00a0', ',').replace('$', 'AUD ')
                row_dict = self._convert_to_datetime(row_dict)
                self._bills_data.append(row_dict)
            except Exception as e:
                print("Bad data", e, ' - ', row_dict[SHORT_TITLE])

    def _get_row_data(self, tds):
        row_data = []
        for col in range(7):
            try:
                if tds[col].span:
                    row_data.append(tds[col].span.string)
                else:
                    row_data.append("")
            except Exception as e:
                print(e)
                row_data.append("")
        return(row_data)

    def _convert_to_datetime(self, bill_dict):
        bill_year = self.this_year

        def to_datetime(indate):
            outdate = None
            if indate is not None:
                if indate != "" and '/' in indate:
                    tempdate = indate.split('/')
                    outdate = datetime.date(
                        bill_year, int(tempdate[1]), int(tempdate[0]))
            return(outdate)

        for i in range(6):
            year = self.this_year - i
            if str(year) in bill_dict[SHORT_TITLE]:
                bill_year = year
        house_stages = [INTRO_HOUSE, PASSED_HOUSE,
                        INTRO_SENATE, PASSED_SENATE, ASSENT_DATE]
        senate_stages = [INTRO_SENATE, PASSED_SENATE,
                         INTRO_HOUSE, PASSED_HOUSE, ASSENT_DATE]

        for stage in house_stages:
            bill_dict[stage] = to_datetime(bill_dict[stage])

        if bill_dict[CHAMBER] == self.chambers[0]:
            for i in range(len(house_stages)-1):
                if bill_dict[house_stages[i]] is not None and bill_dict[house_stages[i+1]] is not None:
                    if bill_dict[house_stages[i]] > bill_dict[house_stages[i+1]]:
                        d = bill_dict[house_stages[i+1]]
                        bill_dict[house_stages[i+1]] = datetime.date(d.year+1, d.month, d.day)
        elif bill_dict[CHAMBER] == self.chambers[1]:
            for i in range(len(senate_stages)-1):
                if bill_dict[senate_stages[i]] is not None and bill_dict[senate_stages[i+1]] is not None:
                    if bill_dict[senate_stages[i]] > bill_dict[senate_stages[i+1]]:
                        d = bill_dict[senate_stages[i+1]]
                        bill_dict[senate_stages[i+1]] = datetime.date(d.year+1, d.month, d.day)

        return(bill_dict)

    @property
    def data(self):
        return(self._bills_data)


all_bills = All_Bills().data


class Bill(object):
    _all_bills = all_bills

    def __init__(self, input):
        if isinstance(input, dict):
            try:
                self.create_vars(input)
            except Exception as e:
                raise Exception('Dict must have the correct keys. Missing key '
                                + str(e))
        elif isinstance(input, str):
            t_data = False
            for bill in self._all_bills:
                if input == bill[URL] or input == bill[ID]:
                    t_data = bill
            if t_data:
                self.create_vars(t_data)
            else:
                raise TypeError('Must be a valid url string')
        else:
            raise TypeError('Must be a dict of the correct format OR a valid url string. See docs.')

    def create_vars(self, initial_data):
        self._bill_data = initial_data
        self.url = initial_data[URL]
        self.chamber = initial_data[CHAMBER]
        self.short_title = initial_data[SHORT_TITLE]
        self.intro_house = initial_data[INTRO_HOUSE]
        self.passed_house = initial_data[PASSED_HOUSE]
        self.intro_senate = initial_data[INTRO_SENATE]
        self.passed_house = initial_data[PASSED_SENATE]
        self.assent_date = initial_data[ASSENT_DATE]
        self.act_no = initial_data[ACT_NO]
        self.bill_url = requests.get(self.url).text
        self.bill_soup = BeautifulSoup(self.bill_url, 'lxml')

    def __str__(self):
        return(self.short_title)

    def __repr__(self):
        return('<{}.{} : {} object at {}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.url.split('=')[-1],
            hex(id(self))))

    @property
    def summary(self):
        return(self.get_bill_summary())

    @property
    def sponsor(self):
        return(self.get_sponsor())

    @property
    def bill_text_links(self):
        return(self.get_bill_text_links())

    @property
    def explanatory_memoranda_links(self):
        return(self.get_bill_em_links())

    def get_bill_summary(self):
        try:
            div = self.bill_soup.find("div", id='main_0_summaryPanel')
        except Exception as e:
            div = None
        if div:
            for span_tag in div.find_all('span'):
                span_tag.unwrap()
            summary = div.p.text.replace('\n', '').replace('    ', '').replace(
                '\r', '').replace('\u2014\u0080\u0094', ' ').replace('\u00a0', ',').replace('$', 'AUD ')
        else:
            summary = ""
        return(summary)

    def get_bill_text_links(self):
        empyt_link_dict = {DOC: '',
                           PDF: '',
                           HTML: ''}
        all_texts = []
        tr_code = 'main_0_textOfBillReadingControl_readingItemRepeater_trFirstReading1_'
        for code_n in range(3):
            try:
                tr = self.bill_soup.find(
                    "tr", id=tr_code+str(code_n))
                links = []
                for a in tr.find_all('td')[1].find_all('a'):
                    links.append(a['href'])
                links_dict = {DOC: links[0],
                              PDF: links[1],
                              HTML: links[2]}
                print(links_dict)
                all_texts.append(links_dict)
            except Exception as e:
                links_dict = empyt_link_dict.copy()
        reading_dict = {
            'first': empyt_link_dict.copy(),
            'third': empyt_link_dict.copy(),
            'aspassed': empyt_link_dict.copy(),
        }

        for text in all_texts:
            for typ in reading_dict.keys():
                if typ in text[PDF]:
                    reading_dict[typ] = text
        print('-----------------------------')
        print(reading_dict)
        return(reading_dict)

    def get_bill_em_links(self):
        try:
            tr = self.bill_soup.find(
                "tr", id='main_0_explanatoryMemorandaControl_readingItemRepeater_trFirstReading1_0')
            links = []
            for a in tr.find_all('td')[1].find_all('a'):
                links.append(a['href'])
            links_dict = {DOC: links[0],
                          PDF: links[1],
                          HTML: links[2]}
            return(links_dict)
        except Exception as e:
            return({})

    def get_sponsor(self):
        try:
            tr = self.bill_soup.find("div", id='main_0_billSummary_sponsorPanel')
            return(tr.find_all('dd')[0].text.replace(' ', '').replace('\n', '').replace('\r', ''))
        except Exception as e:
            return('')

    @property
    def data(self):
        self._bill_data[READING] = 'first'
        text_type = [DOC, PDF, HTML]
        self._bill_data[SUMMARY] = self.summary
        self._bill_data[SPONSOR] = self.sponsor
        for TEXT in text_type:
            for reading in ['first', 'third', 'aspassed']:
                if self.bill_text_links[reading][TEXT] != '':
                    self._bill_data[TEXT_LINK + ' ' + TEXT] = self.bill_text_links[reading][TEXT]
                    self._bill_data[READING] = reading
                    print()
                    print(reading)
                    print()
            self._bill_data[EM_LINK + ' ' + TEXT] = self.explanatory_memoranda_links[TEXT]

        return(self._bill_data)
