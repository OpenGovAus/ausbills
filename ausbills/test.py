from federal_parliment import All_Bills, Bill

fb = All_Bills()

print(fb)

# print(fb.data[3])
# print()
# url = fb.data[3]
# b = Bill(fb.data[3])
#
# print(b.url)
# print(b.intro_house)
# print(b.summary)
# print(b.sponsor)
# print(b.bill_text_links)
# print(b.explanatory_memoranda_links)
#
# for bd in fb.data:
#
#     b = Bill(bd)
#     print(b.summary)
#     print(b.sponsor)
#     print('---------')

print(repr(Bill(fb.data[3])))
