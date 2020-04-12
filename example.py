from ausbills.federal_parliment import all_bills, Bill

print(all_bills)

print(all_bills[10]["url"])

print(Bill(all_bills[10]["url"]).data)

print('')

print(Bill(all_bills[10]["url"]).bill_text_links)
