from federal_parliment import All_Bills, Bill
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

test_all_bills = All_Bills()

NoneType = type(None)

assert isinstance(test_all_bills.data, list)

for bd in test_all_bills.data:
    assert isinstance(bd[URL], str)
    print(bd[URL].split(':')[0], bd[URL])
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
    print(bd[SHORT_TITLE])

    # Do the bill tests better

    b = Bill(bd)
    print(b.summary)
    print(b.url)
    print(b.intro_house)
    print(b.summary)
    print(b.sponsor)
    print(b.bill_text_links)
    print(b.explanatory_memoranda_links)
