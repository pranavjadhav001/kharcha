import dash_bootstrap_components as dbc
from dash import html
import xlrd
from dash import Dash, Input, Output, ctx, html, dcc
import numpy as np
from dash import Dash, Input, Output, callback, dash_table,html, MATCH, ALL
import pandas as pd
import dash_bootstrap_components as dbc
import random
from dash import callback_context

from dash import dcc
from collections import OrderedDict
from  dash_bootstrap_components import Row as R, Col as C
import io
import os
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import icici_xls
import hdfc_xls
import icici_credit_xls
import pandas as pd
from datetime import date
import xlrd
import pandas as pd
from utils import *
from db_utils import *
import argparse
from parse_remarks import *

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}
transaction_length = 10
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)
bank_dict = {'ICICI Bank':'icici_bank', 'ICICI Credit card':'icici_credit', 'HDFC Bank':'hdfc_bank'}
friends = ['bhagat','pankaj','sanyam']
columns = ['Date','Amount','TransactionType','Balance','Remarks_parsed','source','tag','friends']
db_columns = ['Date','Amount','TransactionType','Balance','Remarks_parsed','Remarks_raw','source']

def convert_to_dict(transaction_list):
    final_list = []
    for row in transaction_list:
        temp_dict = dict()
        for items,col in zip(row,db_columns):
            temp_dict[col]=items
        final_list.append(temp_dict)
    return final_list

def update_table_body(transaction_list):
    table_header = [
    html.Thead(html.Tr([html.Th(i) for i in columns]))
    ]
    all_rows =[]
    tooltips = []
    table_body = []
    for index,row in enumerate(transaction_list):
        dropdown_comp = dcc.Dropdown(id={"item": str(index)}, options=[
            {'value': x, 'label': x} for x in friends
        ], multi=True, value="",placeholder='friend',style={'color': 'Black'})
        dropdown_comp2 = html.Div(R([C(dcc.Dropdown(id={"my-dynamic-dropdown":str(index)},\
            options=['NY','SF'],style={'color': 'Black'})),
        C(dbc.Button('Submit', id={"button": str(index)}, n_clicks=0))]))
        rowwed = []
        for key,value in row.items():
            if key != 'Remarks_raw':
                rowwed.append(html.Td(value))
        rowwed.append(html.Td(dropdown_comp2))
        rowwed.append(html.Td(dropdown_comp))
        final_row = html.Tr(rowwed,id="row"+str(index))
        all_rows.append(final_row)
    table_body = [html.Tbody(all_rows)]
    table = dbc.Table(table_header + table_body, bordered=True,
        color='dark',
        dark=True,
        hover=True,
        responsive=True,
        striped=True)
    items = [table]
    for cnt,remark in enumerate(transaction_list):
        items.extend([dbc.Tooltip(remark['Remarks_raw'],target="row"+str(cnt))])
    return items

app.layout = html.Div([dcc.Store(id='store'),
    dcc.Store(id='table_store'),
    html.Div(html.H1("KHARCHA")),html.Div([
    html.Div(dcc.Upload(html.Button('icici bank statement upload'),id='ICICI Bank',multiple=True,\
        style_active={'backgroundColor': '#eee',}),\
        style={
            'width': '22%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '1%',
            'display': 'inline-block'
        }),
    html.Div(dcc.Upload(html.Button('icici credit statement upload'),id='ICICI Credit card',multiple=True),\
        style={
            'width': '22%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '1%',
            'display': 'inline-block'
        }),
    html.Div(dcc.Upload(html.Button('hdfc bank statement upload'),id='HDFC Bank',multiple=True),style={
            'width': '22%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '1%',
            'display': 'inline-block'
        }),
    html.Div(dcc.Upload(html.Button('hdfc credit statement upload'),id='HDFC credit',disabled=True),style={
            'width': '22%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '1%',
            'display': 'inline-block'
        })]),
    html.Div(R([C(dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date(2025, 9, 19),
        initial_visible_month=date(2022, 11, 1),
        end_date=date(2022,11,30)),width=4),
    C(dcc.Dropdown(['ICICI Bank', 'ICICI Credit card', 'HDFC Bank'],
    None, id='source'),width=2,align='center')])),
    html.Div(R([C(html.Div(id='output-container-date-picker-range')),
        C(html.Div(id='dd-output-container'))])),
    html.Div(id='table')])

def update_date(start_date, end_date, source):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '

    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string

    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here',None
    
    if start_date is not None and end_date is not None:
        new_start_date = shuffle_date(start_date)
        new_end_date = shuffle_date(end_date)
        connection = create_connection('global_statement.db')
        create_table_icici_statement('ALL_TRANSACTION', connection)
        if source is not None:
            cursor = connection.execute('SELECT * from ALL_TRANSACTION where Date between ? and ? and source = ?', \
                (new_start_date, new_end_date,source))
        else:
            cursor = connection.execute('SELECT * from ALL_TRANSACTION where Date between ? and ?', \
                (new_start_date, new_end_date))
        data = cursor.fetchall()
        return string_prefix,data
    else:
        return string_prefix,None

def shuffle_date(str_date):
    year,month,date = str_date.split('-')
    return '-'.join([year,month,date])

@app.callback(Output('output-container-date-picker-range', 'children'),
              Output('dd-output-container', 'children'),
              Output('table', 'children'),
              Input('HDFC Bank', 'filename'),
              Input('ICICI Credit card', 'filename'),
              Input('ICICI Bank', 'filename'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input('source', 'value'),
              prevent_initial_call=True,
              )
def update_output(list_of_names1,list_of_names2,list_of_names3,start_date,end_date,value):
    global transaction_length
    triggered_id = ctx.triggered_id
    if triggered_id == 'ICICI Bank':
        file_path = os.path.join('../excels',list_of_names3[0])
        transaction_list = icici_xls.get_universal_transaction_dict(file_path)
        connection = create_connection('global_statement.db')
        create_table_icici_statement('ALL_TRANSACTION', connection)
        insert_many('ALL_TRANSACTION', transaction_list, connection)
        table = update_table_body(transaction_list)
        string_prefix = 'Select a date to see it displayed here'
        source_value = 'Select a source'  
    elif triggered_id == 'HDFC Bank':
        file_path = os.path.join('../excels',list_of_names1[0])
        transaction_list = hdfc_xls.get_universal_transaction_dict(file_path)
        connection = create_connection('global_statement.db')
        create_table_icici_statement('ALL_TRANSACTION', connection)
        insert_many('ALL_TRANSACTION', transaction_list, connection)
        table = update_table_body(transaction_list)
        string_prefix = 'Select a date to see it displayed here'
        source_value = 'Select a source'  
    elif triggered_id == 'ICICI Credit card':
        file_path = os.path.join('../excels',list_of_names2[0])
        transaction_list = icici_credit_xls.get_universal_transaction_dict(file_path)
        connection = create_connection('global_statement.db')
        create_table_icici_statement('ALL_TRANSACTION', connection)
        insert_many('ALL_TRANSACTION', transaction_list, connection)
        table = update_table_body(transaction_list)
        string_prefix = 'Select a date to see it displayed here'
        source_value = 'Select a source'   
    else:
        source = bank_dict.get(value,None)
        string_prefix,db_data = update_date(start_date,end_date,source)
        transaction_list = convert_to_dict(db_data) 
        table = update_table_body(transaction_list)
        source_value = f'You have selected {value}'
    transaction_length = len(table)
    return string_prefix,source_value,table

print(transaction_length)

options = []
elements = []

@app.callback(
    Output("store", "data"),
    [Input({"my-dynamic-dropdown": ALL}, "search_value")],
    State("store", "data"),
    prevent_initial_call=True,
)
def get_search_value(*args):
    input_searches,data_store = args
    triggered_id = ctx.triggered_id
    search_value = input_searches[int(triggered_id['my-dynamic-dropdown'])]
    if search_value is None or not search_value:
        pass
    else:
        data_store = search_value
        elements.append(data_store)
        return data_store

@app.callback(
    Output({"my-dynamic-dropdown": ALL}, "options"),
    [Input({"button": ALL}, "n_clicks")],
    [
        State("store", "data"),
        State({"my-dynamic-dropdown": ALL}, "options"),
        State({"my-dynamic-dropdown": ALL}, "search_value")
    ],prevent_initial_call=True
)
def update_options(*args):
    options = args[-2]
    if len(elements) == 0:
        return options
    else:
        new_options = []
        for i in options:
            i.append(elements[-1]) 
        return options


if __name__ == '__main__':
    app.run_server(debug=True)
