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

dropdown_comp = dcc.Dropdown(id='friends', options=[
        {'value': x, 'label': x} for x in friends
    ], multi=True, value=friends)
final_df['friends'] = [dropdown_comp for _ in range(len(final_df))]
app = Dash(__name__)
app.layout = html.Div([
    dash_table.DataTable(data=final_df.to_dict('records'),\
        columns=[{"name": i, "id": i} if i == 'friends' else {"name": i, "id": i} for i in final_df.columns], \
        id='tbl',\
        editable=True,
        ),
        html.Div(id='table-dropdown-container'),
        dbc.Alert(id='tbl_out')])

@callback(Output('tbl_out', 'children'), Input('tbl', 'active_cell'))
def update_graphs(active_cell):
	return df['Transaction Remarks'].iloc[active_cell['row']] if active_cell else "Click the table"

if __name__ == '__main__':
    app.run_server(debug=True)