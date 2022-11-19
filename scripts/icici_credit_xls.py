import xlrd
import pandas as pd
from utils import *
from db_utils import *

def change_date(date_str):
	date,month,year = date_str.split('/')
	return '-'.join([year,month,date])

def get_universal_transaction_dict(file_path):
	workbook = xlrd.open_workbook(file_path)
	df = pd.DataFrame(columns=['Transaction Date','Transaction Remarks','Amount','Reference Number'])
	sheet = workbook.sheet_by_index(0)
	cnt = 1
	for rx in range(14,sheet.nrows):
	    df.loc[len(df)] = [x.value for x in sheet.row(rx) if x.value]
	#remove bottom metainfo
	df = page_break_merge_credit(df)
	final_list = []
	print(df.head())
	for index,row in df.iterrows():
	    raw_doc = row.to_dict()
	    final_list.append({
	        'Date': change_date(raw_doc['Transaction Date']),
	        'Amount': float(raw_doc['Amount'].split(' ')[0].replace(',','')),
	        'TransactionType': raw_doc['Amount'].split(' ')[-1].upper(),
	        'Balance':None,
	        'Remarks_parsed':parse_remarks(raw_doc['Transaction Remarks']),
	        'Remarks_raw':raw_doc['Transaction Remarks'],
	        'source':'icici_credit'
	    })
	return final_list



if __name__ == "__main__":
	transaction_list = get_universal_transaction_dict('../excels/CCLastStatement16-06-2022.xls')
	print(transaction_list)
	connection = create_connection('icici_credit.db')
	create_table_icici_statement('ICICI_CREDIT2', connection)
	insert_many('ICICI_CREDIT2', transaction_list, connection)
	cursor = fetch_data(connection, 'ICICI_CREDIT2')
	for row in cursor.fetchall():
		print(row)