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
import importlib
import sqlite3
import logging
import argparse
import openpyxl
import pandas as pd
from datetime import datetime
import datetime
from openpyxl.styles import Alignment, PatternFill

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../")))

logger =logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class db_comparison():
    def __init__(self, data_base1=None, data_base2=None, table_name=None):
        self.csv_file_name = None
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
            logger.info("Name of the Report Folder: {}".format(self.directory))
        try:
            if not os.path.exists(self.directory):
                os.mkdir(self.directory)
        except Exception as e:
            logger.error("ERROR : The report path is existed but unable to find. Exception raised : {}\n".format(e))

    def checking_data_bases(self, db1, db2):
        # checking if database files r exist
        if not os.path.isfile(db1):
            logger.error(f"Error: File {db1} does not exist\n")
            exit()
        if not os.path.isfile(db2):
            logger.error(f"Error: File {db2} does not exist\n")
            exit()

        # cursor for first database
        cursor1 = self.conn1.cursor()
        # cursor for second database
        cursor2 = self.conn2.cursor()

        # column names from first database
        cursor1.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
        columns1 = [col[0] for col in cursor1.description]
        logger.info(f"First database columns names: {columns1}")

        # column names from second database
        cursor2.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
        columns2 = [col[0] for col in cursor2.description]
        logger.info(f"Second database columns names: {columns2}")

        if columns1 != columns2:
            logger.error("Error: DB1, DB2 column names are not matched.")
            exit()

        cursor1.execute(f"SELECT * FROM {self.table_name}")
        data1 = cursor1.fetchall()

        cursor2.execute(f"SELECT * FROM {self.table_name}")
        data2 = cursor2.fetchall()

        if data1 == data2:
            logger.info("Data is identical (Same) in the given two databases.")
        else:
            logger.info("Data is not identical in the given two databases.")

    def db_querying_with_where_clause(self, column_names, condition=''):
        # Querying the databases
        split_column_names = column_names.split(', ')
        adding_quotes = ['"' + item + '"' for item in split_column_names]
        column_names = ', '.join(adding_quotes)

        query = ['SELECT ' + column_names + ' FROM ' + self.table_name + ' WHERE ' + condition + ';']
        logger.info(" Your Data Base Query : {}".format(query))
        merged_df = None
        db1_query , db2_query = None, None
        if query is not None:
            for i in query:
                db1_query = pd.read_sql_query(i, self.conn1)
                db2_query = pd.read_sql_query(i, self.conn2)
            df1 = pd.DataFrame(db1_query)
            df2 = pd.DataFrame(db2_query)
            merged_df = df1.merge(df2, left_index=True, right_index=True, suffixes=('_1', '_2'))
        else:
            logger.info("Query is empty")
        logger.info("Merged Query Results :".format(merged_df))
        return merged_df

    def db_querying_with_limit(self, column_names, condition='', limit=None):
        # Querying the databases
        split_column_names = column_names.split(', ')
        adding_quotes = ['"' + item + '"' for item in split_column_names]
        column_names = ', '.join(adding_quotes)
        query = [
            'SELECT ' + column_names + ' FROM ' + self.table_name + ' WHERE ' + condition + ' LIMIT ' + limit + ';']
        # logger.info(" Your Data Base Query : {}".format(query))
        db1_query, db2_query = None, None
        converted_results = []
        if query is not None:
            for i in query:
                db1_query = pd.read_sql_query(i, self.conn1)
                db2_query = pd.read_sql_query(i, self.conn2)
            df1 = pd.DataFrame(db1_query)
            df2 = pd.DataFrame(db2_query)
            query_result = [df1.replace(r'\s+', '', regex=True), df2.replace(r'\s+', '', regex=True)]
            # checking the selected columns data are identical or not
            if str(df1) == str(df2):
                logger.info("The values of %s columns are same in db1 & db2" % column_names)
                # TODO : Need to sort and merge the dataframes are identical in db1 & db2
            else:
                logger.info("The values of %s columns are not same in db1 & db2" % column_names)
                # TODO : Need to sort and merge the dataframes if the data are not identical in db1 & db2

            for i, df in enumerate(query_result):
                result_dict = {}
                for column in df.columns:
                    result_dict[f"{column}_{i + 1}"] = df[column].values[0]
                converted_results.append(result_dict)
        else:
            logger.info("Query is empty")
        # logger.info("List of the dictionary values of the two databases : %s" % converted_results)
        return converted_results

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
            query.append('SELECT DISTINCT "test-tag",  "short-description", "numeric-score" FROM ' + self.table_name + ' WHERE "test-tag" LIKE \"' +
                test_tags[i] + '\" and "short-description" LIKE \"'+ self.short_description + '\";')
        # query dataframe dictionary
        query_df_dict = {
            "db1_df" : [],
            "db2_df" : [],
            "sorted_db1_df" : [],
            "sorted_db2_df" : [],
            "merged_df" : []
        }
        if query:
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
            # removing the empty dataframes from the list of the dataframes
            query_df_dict["merged_df"] = [df for df in query_df_dict["merged_df"] if not df.empty]
            logger.info("Query DataFrames List After Merge : {}".format(query_df_dict["merged_df"]))

        # Calculating the percentage for the db1-numeric-score & db2-numeric-score and attaching the Comparison (%) values to same dataframe
        percentage_list = []
        for item in query_df_dict['merged_df']:
            temp_list = []
            for i in range(len(item['numeric-score_1'])):
                temp_list.append(str(round(abs(((item['numeric-score_2'][i] / item['numeric-score_1'][i]) * 100)), 1)) + "%")
            percentage_list.append(temp_list)
            item['Comparison (%)'] = temp_list      # adding the comparison column
            if item['test-tag'][0] == "AP_AUTO":
                item.rename(columns={'test-tag': 'Radio-Type', 'short-description': 'Short Description - Band Ranges', 'numeric-score_1':'Values of DB1', 'numeric-score_2':'Values of DB2'}, inplace=True)
            else:
                item.rename(columns={'test-tag': 'Radio-Type', 'short-description': 'No of Clients', 'numeric-score_1':'Values of DB1', 'numeric-score_2':'Values of DB2'}, inplace=True)
        logger.info("Percentage values for all tables in a list :".format(percentage_list))
        logger.info("Final Data Frame List:".format(query_df_dict["merged_df"]))

        # building the new output directory
        self.building_output_directory()

        if query_df_dict["merged_df"]:
            # converting the dataframes list into a csv file
            for n in range(len(query_df_dict["merged_df"])):
                if query_df_dict["merged_df"][n]['Radio-Type'][0] == 'AP_AUTO':
                    with open(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/ap_auto.csv', 'w') as f:
                        for i, df in enumerate(query_df_dict["merged_df"]):
                            if df['Radio-Type'][0] == 'AP_AUTO':
                                df.to_csv(f, index=True, header=f'Table{i+1}')
                else:
                    with open(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/wct.csv', 'w') as f:
                        for i, df in enumerate(query_df_dict["merged_df"]):
                            if df['Radio-Type'][0] != 'AP_AUTO':
                                df.to_csv(f, index=True, header=f'Table{i+1}')

        # placing the tables in different Excel-Sheets based on the test-tags
        writer_obj = pd.ExcelWriter(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx', engine='xlsxwriter')
        row, column = 9, 0
        for i, df in enumerate(query_df_dict["merged_df"]):
            if i > 0:
                if i % 2 != 0:
                    column = len(query_df_dict["merged_df"][i - 1].columns) + 1
                else:
                    row += len(query_df_dict["merged_df"][i - 1]) + 2
                    column = 0
            if df['Radio-Type'][0] != 'AP_AUTO':
                df.to_excel(writer_obj, sheet_name='LRQ-WCT', index=False, startrow=row, startcol=column)
                # fetching the info about kernel and gui_ver for WifiCapacity
                result = self.db_querying_with_limit(column_names='kernel, gui_ver',
                                                     condition='"test-id" == "WiFi Capacity"', limit='1')

                writer_obj.sheets['LRQ-WCT'].write(2, 5, "THE LRQ WCT DATA COMPARISON")
                writer_obj.sheets['LRQ-WCT'].write(4, 0, "Vaule of DB1 :")
                writer_obj.sheets['LRQ-WCT'].write(4, 1, f"Kernel : {result[0]['kernel_1']}")
                writer_obj.sheets['LRQ-WCT'].write(4, 3, f"Gui-Ver : {result[0]['gui_ver_1']}")
                writer_obj.sheets['LRQ-WCT'].write(6, 0, "Vaule of DB1 :")
                writer_obj.sheets['LRQ-WCT'].write(6, 1, f"Kernel : {result[1]['kernel_2']}")
                writer_obj.sheets['LRQ-WCT'].write(6, 3, f"Gui-Ver : {result[1]['gui_ver_2']}")
            else:
                df.to_excel(writer_obj, sheet_name='LRQ-AP_AUT0', index=False, startrow=9, startcol=0)
                # fetching the info about kernel and gui_ver for AP Auto
                result = self.db_querying_with_limit(column_names='kernel, gui_ver',
                                                     condition='"test-id" == "AP Auto"', limit='1')

                writer_obj.sheets['LRQ-AP_AUT0'].write(2, 5, "THE LRQ AP-AUTO DATA COMPARISON")
                writer_obj.sheets['LRQ-AP_AUT0'].write(2, 5, "THE LRQ WCT DATA COMPARISON")
                writer_obj.sheets['LRQ-AP_AUT0'].write(4, 0, "Vaule of DB1 :")
                writer_obj.sheets['LRQ-AP_AUT0'].write(4, 1, f"Kernel : {result[0]['kernel_1']}")
                writer_obj.sheets['LRQ-AP_AUT0'].write(4, 3, f"Gui-Ver : {result[0]['gui_ver_1']}")
                writer_obj.sheets['LRQ-AP_AUT0'].write(6, 0, "Vaule of DB1 :")
                writer_obj.sheets['LRQ-AP_AUT0'].write(6, 1, f"Kernel : {result[1]['kernel_2']}")
                writer_obj.sheets['LRQ-AP_AUT0'].write(6, 3, f"Gui-Ver : {result[1]['gui_ver_2']}")

        writer_obj.save()

        # styling the sheets
        wb = openpyxl.load_workbook(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx')
        for n in range(len(query_df_dict["merged_df"])):
            if query_df_dict["merged_df"][n]['Radio-Type'][0] == 'AP_AUTO':
                # Styling for sheet-LRQ-AP_AUTO
                ws1 = wb['LRQ-AP_AUT0']
                ws1.column_dimensions['A'].alignment = Alignment(horizontal='center')
                ws1.column_dimensions['A'].width = 15
                ws1.column_dimensions['B'].width = 35
                ws1.column_dimensions['C'].width = 13
                ws1.column_dimensions['D'].width = 13
                ws1.column_dimensions['E'].width = 15
                ws1.column_dimensions['F'].width = 30
                ws1.column_dimensions['F'].alignment = Alignment(horizontal='center')
                ws1.column_dimensions['E'].alignment = Alignment(horizontal='right')
                fill_cell1 = PatternFill(patternType='solid', fgColor='FEE135')
                ws1['F3'].fill = fill_cell1
            else:
                # Styling for sheet-LRQ-WCT
                ws = wb['LRQ-WCT']
                ws.column_dimensions['A'].alignment = Alignment(horizontal='center')
                ws.column_dimensions['A'].width = 30
                ws.column_dimensions['B'].width = 17
                ws.column_dimensions['C'].width = 13
                ws.column_dimensions['D'].width = 13
                ws.column_dimensions['E'].width = 15
                ws.column_dimensions['F'].width = 27
                ws.column_dimensions['F'].alignment = Alignment(horizontal='center')
                ws.column_dimensions['E'].alignment = Alignment(horizontal='right')
                fill_cell1 =  PatternFill(patternType='solid', fgColor='FEE135')
                ws['F3'].fill = fill_cell1
                ws.column_dimensions['G'].width = 30
                ws.column_dimensions['H'].width = 17
                ws.column_dimensions['I'].width = 13
                ws.column_dimensions['J'].width = 13
                ws.column_dimensions['K'].width = 15
                ws.column_dimensions['K'].alignment = Alignment(horizontal='right')

        wb.save(f'/home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx')

        logger.info(f'Report Path : /home/tharun/lanforge-scripts/py-scripts/tools/{self.directory}/lrq_db_comparison.xlsx')
        wb.close()

def main():
    parser = argparse.ArgumentParser(description='Compare data in two SQLite databases')
    parser.add_argument('--db1', help='Path to first database file (.db)')
    parser.add_argument('--db2', help='Path to second database file (.db)')
    parser.add_argument('--table_name', help='Name of table to compare', default="qa_table")
    # logging configuration:
    parser.add_argument('--log_level', default=None,  help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")

    args = parser.parse_args()

    # set the logger level to debug
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    logger.debug("Comparing results db1: {db1} db2: {db2} ".format(db1=args.db1,db2=args.db2))

    obj = db_comparison(data_base1=args.db1,
                        data_base2=args.db2,
                        table_name=args.table_name)
    # checking the dbs are existed and the data is identical or not
    obj.checking_data_bases(db1=args.db1, db2=args.db2)
    # querying
    obj.querying()

if __name__ == "__main__":
    main()
