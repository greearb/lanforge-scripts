#!/usr/bin/env python3
"""
Name : lf_db_comparison.py

Purpose : lf_db_comparison.py used for comparing the two databases and data manipulations using sql query's

Example :
    lf_db_comparison.py --db1 <path of the database_1> --db2 <path of the database_2> --table_name <table_name>

    python3 lf_db_comparison.py --db1 "/home/tarun/Desktop/qa_LRQ_FULL_1.db" --db2 "/home/tarun/Desktop/qa_LRQ_FULL_2.db" --table_name "qa_table"
"""

import os
import sys
import sqlite3
import argparse
import openpyxl
import pandas as pd
from datetime import datetime
import datetime
from openpyxl.styles import Alignment, PatternFill

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

class db_comparison():
    def __init__(self, data_base1=None, data_base2=None, table_name=None):
        self.short_description = None
        self.sub_lists = None
        self.conn2 = None
        self.conn1 = None
        self.db1 = data_base1
        self.db2 = data_base2
        self.directory = None
        self.table_name = table_name
        self.conn1 = sqlite3.connect(self.db1)
        self.conn2 = sqlite3.connect(self.db2)

    def building_output_directory(self,directory_name="LRQ_Comparison_Report"):
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S_")  # %Y-%m-%d-%H-h-%m-m-%S-s
        if directory_name:
            self.directory = os.path.join(now + str(directory_name))
            print("Name of the Report Folder:", self.directory)
        try:
            if not os.path.exists(self.directory):
                os.mkdir(self.directory)
        except Exception as e:
            print(e)

    def checking_data_bases(self, db1, db2):
        # checking if database files r exist
        if not os.path.isfile(db1):
            print(f"Error: File {db1} does not exist")
            exit()
        if not os.path.isfile(db2):
            print(f"Error: File {db2} does not exist")
            exit()

        # cursor for first database
        cursor1 = self.conn1.cursor()
        # cursor for second database
        cursor2 = self.conn2.cursor()

        # column names from first database
        cursor1.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
        columns1 = [col[0] for col in cursor1.description]
        print("First database columns names:", columns1)

        # column names from second database
        cursor2.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
        columns2 = [col[0] for col in cursor2.description]
        print("Second database columns names:", columns2)

        if columns1 != columns2:
            print("Error: Column names do not match")
            exit()

        cursor1.execute(f"SELECT * FROM {self.table_name}")
        data1 = cursor1.fetchall()

        cursor2.execute(f"SELECT * FROM {self.table_name}")
        data2 = cursor2.fetchall()

        if data1 == data2:
            print("Data is identical (Same) in the given two databases.")
        else:
            print("Data is not identical in the given two databases.")

    def querying(self):
        # Querying the databases base on the test-tags
        query = []
        test_tags = ['WCT_MTK7915_%_5G_UDP_UL_AT', 'WCT_MTK7915_%_2G_UDP_UL_AT',
                     'WCT_MTK7915_%_5G_UDP_DL_AT', 'WCT_MTK7915_%_2G_UDP_DL_AT',
                     'WCT_MTK7915_%_5G_TCP_UL_AT', 'WCT_MTK7915_%_2G_TCP_UL_AT',
                     'WCT_MTK7915_%_5G_TCP_DL_AT', 'WCT_MTK7915_%_2G_TCP_DL_AT', 'AP_AUTO']
        # setting up the short_descriptions for WCT, AP_AUTO tags.
        for i in range(len(test_tags)):
            if test_tags[i].split('_')[-2] == "UL":
                self.short_description = 'UL Mbps - % STA'
            elif test_tags[i].split('_')[-2] == "DL":
                self.short_description = 'DL Mbps - % STA'
            elif test_tags[i] == "AP_AUTO":
                self.short_description = 'Basic Client Connectivity % %'
            query.append(
                'SELECT DISTINCT "test-tag",  "short-description", "numeric-score" FROM ' + self.table_name + ' WHERE "test-tag" LIKE \"' +
                test_tags[i] + '\" and "short-description" LIKE \"'+ self.short_description + '\";')
        query_df_dict = {
            "db1_df" : [],
            "db2_df" : [],
            "sorted_db1_df" : [],
            "sorted_db2_df" : [],
            "merged_df" : []
        }
        # reading the sql query's from the both databases
        for i in query:
            query_df_dict['db1_df'].append(pd.read_sql_query(i, self.conn1))
            query_df_dict['db2_df'].append(pd.read_sql_query(i, self.conn2))
        # sorting the two databases based on test-tags and placing in different list
        for df in range(len(query_df_dict['db1_df'])):
            query_df_dict["sorted_db1_df"].append(query_df_dict["db1_df"][df].sort_values(by='test-tag', ascending=True))
            query_df_dict["sorted_db2_df"].append(query_df_dict["db2_df"][df].sort_values(by='test-tag', ascending=True))
        # merging the dataframes and placing in a 'merged_df' list
        for sorted_df in range(len(query_df_dict['sorted_db1_df'])):
            query_df_dict["merged_df"].append(query_df_dict["sorted_db1_df"][sorted_df].merge(query_df_dict["sorted_db2_df"][sorted_df], on=['test-tag', 'short-description'], suffixes=('_1', '_2')))

        print("Query DataFrames List After Merge :", query_df_dict["merged_df"])

        # converting 'merged_df' list to dict data
        final_dict = []
        for i in query_df_dict["merged_df"]:
            final_dict.append(i.to_dict())
        print("\n Final dictionary list:", final_dict)

        # Separating the test-tags, numeric-score of the db1 and db2 and storing them in list
        merged_dict = {'test_tag': [],
                       'n_score1': [],
                       'n_score2': [],
                       'sorted_test_tags' : [],
                       'final_test_tags' : [],
                       'percentage_values' : None
                       }

        # calculating the percentage for numeric-score_1 & numeric-score_2
        percentage_list = []
        for i in range(len(final_dict)):
            for j in range(len(final_dict[i]['numeric-score_1'])):
                if final_dict[i]['numeric-score_2'][
                    j] == 0:  # checking the divisor value 0 or not, before calculating the percentage
                    percentage_diff, for_color_box = 0.0, 0.0
                    percentage_list.append(str(percentage_diff) + "%")
                else:  # if divisor not equal to zero, calculate the simple percentage
                    percentage_diff = round(
                        (abs((final_dict[i]['numeric-score_2'][j] / final_dict[i]['numeric-score_1'][j])) * 100), 1)
                    percentage_list.append(str(percentage_diff) + "%")
        print("\n List of the percentage values for all stations:\n", percentage_list)

        # TODO: need to remove the slicing the list
        # slicing the list into equally with each sub-list 16 items due to the percentage_list has 64 items of the 4 tables values.
        merged_dict['percentage_values'] = [percentage_list[i:i + 16] for i in range(0, len(percentage_list), 16)]
        print("\n Comparison Values of all tables :", merged_dict['percentage_values'])


        for i in range(len(final_dict)):
            merged_dict['test_tag'].append(list((final_dict[i]['test-tag'].values())))
            merged_dict['n_score1'].append(list((final_dict[i]['numeric-score_1'].values())))
            merged_dict['n_score2'].append(list((final_dict[i]['numeric-score_2'].values())))
            merged_dict["sorted_test_tags"].append([tag for tag in merged_dict['test_tag'][i][0:len(merged_dict['test_tag'][i]):4]]) # TODO: Try to find the other way to access the test-tags instead list slicing
        print("\n All test-tags of the merged tables : \n", merged_dict['test_tag'])
        print("\n Sorted Test-tags of the all tables without duplicates :\n", merged_dict["sorted_test_tags"])

        # Separating the test-tags extended with ' ' 3 times for each table
        for item in merged_dict["sorted_test_tags"]:
            sub_list = []
            for elm in item:
                sub_list.extend([elm, ' ', ' ', ' '])
            merged_dict['final_test_tags'].append(sub_list)
        print("\n List of the test-tags extended with ' ' 3 times for each table :\n ", merged_dict['final_test_tags'])
        print("\n Numeric Score values of db1 :\n", merged_dict['n_score1'])
        print("\n Numeric Score values of db2 :\n", merged_dict['n_score2'])


        # def extract_number(s):
        #     return int(s.split()[-2])
        # short_desc_values = list(final_dict[0]['short-description'].values())
        # print("\n Short-Description list: ", list(short_desc_values))
        # numbers = list(map(extract_number, short_desc_values))
        # combined = list(zip(numbers, percentage_list))
        # result = {k: v for k, v in combined}
        # print("Mapping the result comparisons to the short-description :", result)  # result= {1: '100.2%', 19: '100.0%'}

        tables = []
        for i in range(len(merged_dict['n_score1'])):
            if not test_tags[i] == "AP_AUTO":
                tables.append(pd.DataFrame({'Radio-Type': merged_dict['final_test_tags'][i],
                                            'No of Clients': ['1', '5', '10', '19', '1', '5', '10', '19', '1', '5',
                                                              '10', '19',
                                                              '1', '5', '10', '19'],
                                            'Values DB1': merged_dict['n_score1'][i],
                                            'Values DB2': merged_dict['n_score2'][i],
                                            'Comparison (%)': merged_dict['percentage_values'][i]}))
            else:
                tables.append(pd.DataFrame({'Type': ['', '', '', '', 'AP_AUTO', '', '', '', ''],
                                            'Band': ['', '2 Ghz', '', '', '5 Ghz', '', '', 'Dual Band', ''],
                                            'Time': ['Min', 'Avg', 'Max', 'Min', 'Avg', 'Max', 'Min', 'Avg', 'Max'],
                                            'Values DB1': merged_dict['n_score1'][i],
                                            'Values DB2': merged_dict['n_score2'][i],
                                            'Comparison (%)': merged_dict['percentage_values'][i]}))

        self.building_output_directory()
        writer_obj = pd.ExcelWriter(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx', engine='xlsxwriter')

        tables[0].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=4, startcol=0)

        tables[1].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=4, startcol=6)

        tables[2].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=22, startcol=0)

        tables[3].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=22, startcol=6)

        tables[4].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=40, startcol=0)

        tables[5].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=40, startcol=6)

        tables[6].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=58, startcol=0)

        tables[7].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=58, startcol=6)

        tables[8].to_excel(writer_obj, sheet_name='LRQ', index=False, startrow=79, startcol=0)

        writer_obj.sheets['LRQ'].write(2, 5, "THE LRQ DATA COMPARISON")

        ############################################################

        # for column in table1:
        #  table1   column_width = max(table1[column].astype(str).map(len).max(), len(column))
        #     col_idx = table1.columns.get_loc(column)
        #     writer_obj.sheets['LRQ'].set_column(col_idx, col_idx, column_width)

        #############################################################

        writer_obj.close()

        print("Report Path : ", f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx')
        wb = openpyxl.load_workbook(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx')
        ws = wb['LRQ']
        ws.column_dimensions['A'].width = 29
        ws.column_dimensions['B'].width = 14
        ws.column_dimensions['B'].alignment = Alignment(horizontal='center')
        ws.column_dimensions['C'].width = 11
        ws.column_dimensions['D'].width = 11
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 24
        ws.column_dimensions['F'].alignment = Alignment(horizontal='center')
        ws.column_dimensions['E'].alignment = Alignment(horizontal='right')
        fill_cell1 =  PatternFill(patternType='solid', fgColor='FEE135')
        ws['F3'].fill = fill_cell1
        ws.column_dimensions['G'].width = 29
        ws.column_dimensions['H'].width = 14
        ws.column_dimensions['H'].alignment = Alignment(horizontal='center')
        ws.column_dimensions['I'].width = 11
        ws.column_dimensions['J'].width = 11
        ws.column_dimensions['K'].width = 15
        ws.column_dimensions['K'].alignment = Alignment(horizontal='right')
        wb.save(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx')
        wb.close()

def main():
    parser = argparse.ArgumentParser(description='Compare data in two SQLite databases')
    parser.add_argument('--db1', help='Path to first database file (.db)')
    parser.add_argument('--db2', help='Path to second database file (.db)')
    parser.add_argument('--table_name', help='Name of table to compare', default="qa_table")

    args = parser.parse_args()

    obj = db_comparison(data_base1=args.db1,
                        data_base2=args.db2,
                        table_name=args.table_name)
    # checking the dbs are existed and the data is identical or not
    obj.checking_data_bases(db1=args.db1, db2=args.db2)
    # querying
    obj.querying()

if __name__ == "__main__":
    main()
