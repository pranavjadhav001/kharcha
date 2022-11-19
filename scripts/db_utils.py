import sqlite3
from sqlite3 import OperationalError

def create_connection(db_name):
	conn = sqlite3.connect(db_name)
	return conn

def create_table_icici_statement(table_name,connection):
	try:
		connection.execute(f'''CREATE TABLE {table_name}
	         (Date          DATE           NOT NULL,
	         Amount           REAL    NOT NULL,
	         TransactionType   TEXT     NOT NULL,
	         Balance           REAL     BLOB,
	         Remarks_parsed    TEXT     NOT NULL,
	         Remarks_raw       TEXT     NOT NULL,
	         source            TEXT     NOT NULL);''')
	except OperationalError as e:
		print('Table alreay exists with same name',e)

def insert_row(table_name,row,connection):
    connection.execute(f'INSERT INTO {table_name} (Date,Amount,TransactionType,Balance,Remarks_parsed,Remarks_raw,source)\
          VALUES(?,?,?,?,?,?,?);',tuple(row.values()))


def insert_many(table_name,all_rows,connection):
	for row in all_rows:
		insert_row(table_name, row,connection)

	connection.commit()

def fetch_data(connection,table_name):
	cursor = connection.execute(f"SELECT * from {table_name}")
	return cursor