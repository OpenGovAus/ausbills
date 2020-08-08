from federal_parliment import Bill, all_bills
import datetime

CHAMBER = "chamber"
SHORT_TITLE = "short_title"
INTRO_HOUSE = "intro_house"
PASSED_HOUSE = "passed_house"
INTRO_SENATE = "intro_senate"
PASSED_SENATE = "passed_senate"
ASSENT_DATE = "assent_date"
URL = "url"
ACT_NO = "act_no"
ID = "id"


print(all_bills[3])


NoneType = type(None)

assert isinstance(all_bills, list)

for bd in all_bills[:5]:
    assert isinstance(bd[URL], str)
    print(bd[ID] + " - " + bd[SHORT_TITLE])
    assert '=' in bd[URL]
    assert bd[URL].split(':')[0] in ['http', 'https']
    assert bd[CHAMBER] in ["House", "Senate"]
    assert isinstance(bd[SHORT_TITLE], str)
    assert isinstance(bd[INTRO_HOUSE], (datetime.date, NoneType))
    assert isinstance(bd[PASSED_HOUSE], (datetime.date, NoneType))
    assert isinstance(bd[INTRO_SENATE], (datetime.date, NoneType))
    assert isinstance(bd[PASSED_SENATE], (datetime.date, NoneType))
    assert isinstance(bd[ASSENT_DATE], (datetime.date, NoneType))
    # assert isinstance(bd[ACT_NO], (int, NoneType))

    # Do the bill tests better

    b = Bill(bd)
    assert isinstance(b.summary, str)
    assert isinstance(b.url, str)
    assert isinstance(b.intro_house, (datetime.date, NoneType))
    assert isinstance(b.sponsor, str)
    assert isinstance(b.bill_text_links, dict)
    assert isinstance(b.explanatory_memoranda_links, dict)
    assert isinstance(b.data, dict)
    assert isinstance(b.data[INTRO_HOUSE], str)
    assert isinstance(b.portfolio, str)

# fix datetime input
