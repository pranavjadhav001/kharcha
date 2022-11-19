import pandas as pd
import numpy as np

def page_break_merge_statement(df):
    locations = np.where(df['Value Date'] == "")[0]
    for location in locations:
        df.iloc[location-1]['Transaction Remarks'] += df.iloc[location]['Transaction Remarks']
    df = df.drop(df.index[locations])
    return df

def page_break_merge_credit(df):
    locations = np.where(df['Transaction Date'] == "")[0]
    for location in locations:
        df.iloc[location-1]['Details'] += df.iloc[location]['Details']
    df = df.drop(df.index[locations])
    return df

def determine_transaction_type(doc_dict):
    if doc_dict['Deposit Amount'] == 0.0:
        return "DR"
    else:
        return "CR"

def parse_remarks(remark):
    return remark