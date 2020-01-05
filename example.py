from ausbills import federal_bills
import pandas as pd

df_lower = pd.DataFrame(federal_bills.get_house_bills())
# df_upper = pd.DataFrame(ausbills.get_senate_bills())

print(df_lower)
