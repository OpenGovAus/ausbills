from ausbills import federal_bills
import pandas as pd

df_lower = pd.DataFrame(federal_bills.get_house_bills())

print(df_lower)
