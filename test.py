import dash_bootstrap_components as dbc
from dash import html
import xlrd
import numpy as np
from dash import Dash, Input, Output, callback, dash_table,html
import pandas as pd
import dash_bootstrap_components as dbc
import random
from dash import dcc

from collections import OrderedDict


friends = ['bhagat','pankaj','sanyam']
workbook = xlrd.open_workbook('OpTransactionHistory16-06-2022 (2).xls')
df = pd.DataFrame(columns=['S No.',\
                           'Value Date',\
                           'Transaction Date',\
                           'Cheque Number',\
                           'Transaction Remarks',\
                            'Withdrawal Amount (INR )',\
                             'Deposit Amount (INR )',\
                             'Balance (INR )'])
sheet = workbook.sheet_by_index(0)
cnt = 1
for rx in range(13,sheet.nrows):
    #print(sheet.row(rx))
    df.loc[len(df)] = [x.value for x in sheet.row(rx)][1:]
df.drop(df.tail(28).index,
        inplace = True)
df.replace('', np.nan, inplace = True)
df = df.dropna()
remarks = df['Transaction Remarks'].to_list()
transcation_type= [i.split('/')[0] for i in remarks]
df['Transcation type'] = transcation_type

def parse_all(string,transcation_type):
    if transcation_type == "UPI":
        return parse_remark_upi(string)
    else:
        return string
    
def parse_remark_upi(string):
    string_list = string.split('/')[1:-1]
    for i in string_list[:]:
        if i.isnumeric():
            string_list.remove(i)
        elif 'bank' in i.lower():
            string_list.remove(i)
    return ('-').join(string_list)
df['remark'] = df.apply(lambda x: parse_all(x['Transaction Remarks'],x['Transcation type']),axis=1)
final_df = df.drop(['Cheque Number','Transaction Remarks'],axis=1)
final_df['friends'] = ["" for _ in range(len(final_df))]

table_header = [
    html.Thead(html.Tr([html.Th(i) for i in final_df.columns]))
]
all_rows =[]
tooltips = []
for index,row in final_df.iterrows():
    index -=1
    dropdown_comp = dcc.Dropdown(id=str(index), options=[
        {'value': x, 'label': x} for x in friends
    ], multi=True, value="",placeholder='friend',style={'color': 'Black'})
    rowwed = [html.Td(i) for i in row.values.flatten().tolist()[:-1]]
    rowwed.append(dropdown_comp)
    final_row = html.Tr(rowwed,id="row"+str(index))
    all_rows.append(final_row)


table_body = [html.Tbody(all_rows)]
table = dbc.Table(table_header + table_body, bordered=True,
    dark=True,
    hover=True,
    responsive=True,
    striped=True)
items = [table]

for i in range(len(final_df)):
    items.extend([dbc.Tooltip(df['Transaction Remarks'].iloc[i],
        target="row"+str(i))])

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
                children = [
                    #header
                    html.Div(
                        html.H1("KHARCHA")
                    ),
                    #table
                    html.Div(
                        items
                    )
                ]
            )
if __name__ == '__main__':
    app.run_server(debug=True)