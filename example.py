from ausbills import federal_bills
import pandas as pd

df_lower = federal_bills.get_house_bills()

print(df_lower[4]['URL'])

print(federal_bills.get_bill_summary(df_lower[3]['URL']))
