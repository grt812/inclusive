import pandas as pd
df_xlsx = pd.read_excel("Trending Songs.xlsx")
print(df_xlsx.head(50))

wb = Workbook("Trending Songs.xlsx")
wb.save("trending.html")
