#!/usr/bin/env python3
'''
File: will search sub diretories for kpi.csv and place the data into an sqllite database 

Usage:
'''

import sys
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit
import pandas as pd
import sqlite3
import argparse
from  pathlib import Path

class csv_to_sqlite():
    def __init__(self,
                _path = '.',
                _file = 'kpi.csv',
                _database = 'test_db'):
        self.path = _path
        self.file = _file
        self.database = _database

    def store(self):
        print(self.path)
        path = Path(self.path)
        print(path)
        #path = Path('./test_data3')
        #path = Path('test_data3')
        #print(path)
        #quit(1)        

        kpi_list = list(path.glob('**/{}'.format(self.file)))
        #kpi_list = list(path.glob('**/kpi.csv'))
        print(kpi_list)
        print("lenth kpi_list {}".format(len(kpi_list)))

        df = pd.DataFrame()

        for kpi in kpi_list:
            # load data
            append_df = pd.read_csv(kpi, sep='\t')
            df = df.append(append_df, ignore_index=True)
            #print("df {data}".format(data=df))

        # information on sqlite database
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html

        print(self.database)
        conn = sqlite3.connect(self.database) 
        #conn = sqlite3.connect("qa_db") 
        #df.to_sql("dp_table",conn,if_exists='append')
        df.to_sql("dp_table",conn,if_exists='replace')
        conn.close()

def main():

    parser = argparse.ArgumentParser(
        prog='csv_sqlite.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        read kpi.csv into sqlit database:
            1. Useful Information goes here
            ''',
        
        description='''\
File: will search path recursivly for kpi.csv and place into sqlite database
Usage: csv_sqlite.py --path <path> --database <name>

        ''')
    parser.add_argument('--path', help='--path ./path_to_kpi',required=True)
    parser.add_argument('--file', help='--file kpi.csv',default='kpi.csv')
    parser.add_argument('--database', help='--database qa_test_db',default='qa_test_db')
    
    args = parser.parse_args()

    __path = args.path
    __file = args.file
    __database = args.database

    csv_sqlite = csv_to_sqlite(
                _path = __path,
                _file = __file,
                _database = __database)

    csv_sqlite.store()

if __name__ == '__main__':
    main()    