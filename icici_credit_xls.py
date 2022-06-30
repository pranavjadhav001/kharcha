import xlrd
import pandas as pd
workbook = xlrd.open_workbook('CCLastStatement16-06-2022.xls')
df = pd.DataFrame(columns=['Transcation Date','Details','Amount','Reference Number'])
sheet = workbook.sheet_by_index(0)
cnt = 1
for rx in range(14,sheet.nrows):
    df.loc[len(df)] = [x.value for x in sheet.row(rx) if x.value]
df.head()