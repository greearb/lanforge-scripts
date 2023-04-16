#!/usr/bin/env python3
'''
    lf_inspect.py  --database <test.db>

    lf_inspect.py will do analysis on a database and comprare entries in a datbase.

TODO :  Add to help how to run or which parameters needed to run: on lanforge, a server that is not lanforge, At a desktop
'''
import sys
import os
import importlib
import plotly.express as px
import pandas as pd
import sqlite3
import argparse
from pathlib import Path
import time
import logging
import re
import csv


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../")))

lf_report = importlib.import_module("py-scripts.lf_report")
lf_report = lf_report.lf_report
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

# Any style components can be used
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

class inspect_sql:
    def __init__(self,
                 _path='.',
                 _dir='',
                 _database_list=[],
                 _csv_results = '',
                 _table=None):
        self.path = _path
        self.dir = _dir
        self.table = _table
        logger.debug("path: {path}".format(path=self.path))
        logger.debug("dir: {dir}".format(dir=self.dir))
        self.database_list = _database_list
        self.database = []
        self.conn = None
        self.kpi_list = []
        self.html_list = []
        self.conn = None
        self.df = pd.DataFrame()
        self.plot_figure = []
        self.html_results = ""
        self.test_rig_list = []
        self.short_description_list = []
        self.dut_model_num_list = "NA"
        self.dut_model_num = "NA"
        self.dut_sw_version_list = "NA"
        self.dut_sw_version = "NA"
        self.dut_hw_version_list = "NA"
        self.dut_hw_version = "NA"
        self.dut_serial_num_list = "NA"
        self.dut_serial_num = "NA"
        self.subtest_passed = 0
        self.subtest_failed = 0
        self.subtest_total = 0
        self.test_run = ""

        self.csv_results = _csv_results
        self.csv_results_file = ""
        self.csv_results_writer = ""
        self.csv_results_column_headers = ""



        # results
        self.junit_results = ""
        self.html_results = ""
        self.background_green = "background-color:green"
        self.background_red = "background-color:red"
        self.background_orange = "background-color:orange"
        self.background_purple = "background-color:purple"
        self.background_blue = "background-color:blue"


    def start_csv_results(self):
        self.logger.info("self.csv_results")
        self.csv_results_file = open(self.csv_results, "w")
        self.csv_results_writer = csv.writer(
            self.csv_results_file, delimiter=",")
        self.csv_results_column_headers = [
            'Test', 'Command', 'Result', 'STDOUT', 'STDERR']
        self.csv_results_writer.writerow(self.csv_results_column_headers)
        self.csv_results_file.flush()

    def get_junit_results(self):
        return self.junit_results

    # TODO allow for running of multiple test suites
    def start_junit_testsuites(self):
        self.junit_results += """<?xml version="1.0" encoding="UTF-8" ?>
            <testsuites>
        """

    def finish_junit_testsuites(self):
        self.junit_results += """
        </testsuites>
        """

    def start_junit_testsuite(self):
        self.junit_results += """
        <testsuite name="{suite}">
        """.format(suite=self.test_suite)

    def finish_junit_testsuite(self):
        self.junit_results += """
        </testsuite>
        """

    def get_junit_results(self):
        return self.junit_results

    def get_html_results(self):
        return self.html_results

    def start_html_results(self):
        self.html_results += """
                <table border="1" class="dataframe">
                    <thead>
                        <tr style="text-align: left;">
                          <th>Test</th>
                          <th>Command</th>
                          <th>Duration</th>
                          <th>Start</th>
                          <th>End</th>
                          <th>Result</th>
                          <th>STDOUT</th>
                          <th>STDERR</th>
                        </tr>
                      </thead>
                      <tbody>
                      """

    def finish_html_results(self):
        self.html_results += """
                    </tbody>
                </table>
                <br>
                <br>
                <br>
                """

    # Helper methods
    def compare_data(self):
        logger.info("compare the data in the database from list: {db_list}".format(db_list=self.database_list))

        # TODO for now deal with single database

        self.database = self.database_list[0]
        self.conn =sqlite3.connect(self.database)
        df3 = pd.read_sql_query("SELECT * from {}".format(self.table), self.conn)
        # sort by date from oldest to newest.
        try:
            df3 = df3.sort_values(by='Date')
        except BaseException:
            logger.info("Database empty: KeyError(key) when sorting by Date, check Database name, path to kpi, typo in path, exiting")
            exit(1)
        self.conn.close()

        # graph group and test-tag are used for detemining comparison, can use any columns
        # the following list manipulation removes the duplicates 
        graph_group_list = list(df3['Graph-Group'])
        graph_group_list = [x for x in graph_group_list if x is not None]
        graph_group_list = list(sorted(set(graph_group_list)))
        logger.info("graph_group_list: {}".format(graph_group_list))


        test_tag_list = list(df3['test-tag'])
        test_tag_list = [x for x in test_tag_list if x is not None]
        test_tag_list = list(sorted(set(test_tag_list)))
        logger.info("test_tag_list: {}".format(test_tag_list) )

        test_rig_list = list(df3['test-rig'])
        test_rig_list = [x for x in test_rig_list if x is not None]
        test_rig_list = list(sorted(set(test_rig_list)))
        self.test_rig_list = test_rig_list
        logger.info("test_rig_list: {}".format(test_rig_list))

        short_description_list = list(df3['short-description'])
        short_description_list = [x for x in short_description_list if x is not None]
        short_description_list = list(sorted(set(short_description_list)))
        self.short_description_list = short_description_list
        logger.info("short_description_list: {}".format(short_description_list))


        # find the comparisons
        for test_rig in test_rig_list:
            for test_tag in test_tag_list:
                for group in graph_group_list:
                    for description in short_description_list:
                        # df_temp will contain all the data for a single run 
                        # TODO this pulls out the data,  there needs to be a similiar 
                        # functionality that allows the user to request specific information on the queries
                        # need to be very specific
                        df_tmp = df3.loc[(df3['test-rig'] == test_rig) & (
                            df3['Graph-Group'] == str(group)) & (df3['test-tag'] == str(test_tag)) & (df3['short-description'] == str(description))]
                        if not df_tmp.empty:
                            # Note if graph group is score there is sub tests for pass and fail
                            # would like a percentage


                            # TODO cannot sort by date as it is each individual entry 
                            df_tmp = df_tmp.sort_values(by='Date')

                            # need to drop duplicates as lf_qa may have been run multiple times on the same data
                            df_tmp = df_tmp.drop_duplicates()

                            # write out the df to a tmp_db for analysis
                            # FOR TESTING ONLY 
                            '''
                            self.conn = sqlite3.connect('tmp_db.db')
                            try:
                                df_tmp.to_sql(self.table, self.conn, if_exists='append')
                            except BaseException:
                                logger.info("attempt to append to database with different column layout,\
                                    caused an exception, input new name --database <new name>")
                                print(
                                    "Error attempt to append to database with different column layout,\
                                        caused an exception, input new name --database <new name>",
                                    file=sys.stderr)
                                exit(1)
                            self.conn.close()
                            '''



                            date_list = list(df_tmp['Date'])
                            test_id_list = list(df_tmp['test-id'])
                            kpi_path_list = list(df_tmp['kpi_path'])
                            numeric_score_list = list(df_tmp['numeric-score'])
                            units_list = list(df_tmp['Units'])
                            short_description_list = list(df_tmp['short-description'])
                            # print out last two values in the list
                            # TODO need to check for other values
                            percent_delta = 0
                            if((int(numeric_score_list[-1]) != 0 and numeric_score_list[-1] is not None ) and numeric_score_list[-2] is not None):
                                percent_delta = round(((numeric_score_list[-2]/numeric_score_list[-1]) * 100), 2)

                            logger.debug("Desc1: {desc1} Desc2: {desc2} Date1: {date1} Date2: {date2} units: {units} numeric_score1: {ns1} numeric_score2: {ns2} percent: {percent}".format(
                                desc1=short_description_list[-1],desc2=short_description_list[-2],date1=date_list[-1],date2=date_list[-2],
                                units=units_list[-1],ns1=numeric_score_list[-1],ns2=numeric_score_list[-2], percent=percent_delta))

                            '''
                                            'Date',
                                            'test_dir',
                                            'numeric-score',
                                            'kernel',
                                            'radio_fw',
                                            'gui_ver',
                                            'gui_build_date',
                                            'server_ver',
                                            'server_build_date'
                            '''


                            # get Device Under Test Information ,
                            # the set command uses a hash , sorted puts it back in order
                            # the set reduces the redundency the filster removes None
                            # list puts it back into a list
                            # This code is since the dut is not passed in to lf_qa.py when
                            # regernation of graphs from db

                            # we now have a single entry to add to the csv file

                            # units_list = list(df_tmp['Units'])
                            # logger.info("Inspecting::: test-rig {tr} test-tag {tt}  Graph-Group {gg}".format(tr=test_rig, tt=test_tag, gg=group))



                        '''
                            kpi_fig = (
                                px.scatter(
                                    df_tmp,
                                    x="Date",
                                    y="numeric-score",
                                    custom_data=[
                                        'Date',
                                        'test_dir',
                                        'numeric-score',
                                        'kernel',
                                        'radio_fw',
                                        'gui_ver',
                                        'gui_build_date',
                                        'server_ver',
                                        'server_build_date'
                                        ],
                                    color="short-description",
                                    hover_name="short-description",
                                    size_max=60)).update_traces(
                                mode='lines+markers')

                            kpi_fig.update_layout(
                                title="{test_id} : {group} : {test_tag} : {test_rig}".format(
                                    test_id=test_id_list[-1], group=group, test_tag=test_tag, test_rig=test_rig),
                                xaxis_title="Time",
                                yaxis_title="{units}".format(units=units_list[-1]),
                                xaxis={'type': 'date'}
                            )

                            kpi_fig.update_traces(
                                hovertemplate="<br>".join([
                                    "Date: %{customdata[0]}",
                                    "test_dir: %{customdata[1]}",
                                    "numeric-score: %{customdata[2]}",
                                    "kernel-version: %{customdata[3]}",
                                    "radio-fw: %{customdata[4]}",
                                    "gui-version: %{customdata[5]}",
                                    "gui-build-date: %{customdata[6]}",
                                    "server-version: %{customdata[7]}",
                                    "server-build-date: %{customdata[8]}",
                                ])
                            )

                        '''



        pass

    def get_test_rig_list(self):
        return self.test_rig_list

    def get_html_results(self):
        return self.html_results

    def get_suite_html(self):
        suite_html_results = """
            <table class="dataframe" border="1">
                    <thead>
                        <tr style="text-align: center;">
                          <th>Test</th>
                          <th>Test_Tag</th>
                          <th>Links</th>
                          <th>Directory Name</th>
                        </tr>
                    </thead>
                <tbody>
        """

        path = Path(self.path)
        pdf_info_list = list(path.glob('**/*.pdf'))  # Hard code for now
        logger.info("pdf_info_list {}".format(pdf_info_list))
        for pdf_info in pdf_info_list:
            if "lf_inspect" in str(pdf_info):
                pass
            else:
                pdf_base_name = os.path.basename(pdf_info)
                if "check" in str(pdf_base_name):
                    pass
                else:
                    # TODO remove the fixed path code
                    # try relative path
                    parent_path = os.path.dirname(pdf_info)
                    parent_name = os.path.basename(parent_path)

                    # for the chamberview tests the results is in index.html
                    # so need to move index.html to readme.html
                    # use os.rename(source,destination) , 
                    # check for index
                    index_html_file = parent_path + "/index.html"
                    if os.path.exists(index_html_file):
                        readme_html_file = parent_path + "/readme.html"
                        os.rename(index_html_file,readme_html_file)

                    dir_path = '../' + parent_name 
                    pdf_path = '../' + parent_name + "/" +  pdf_base_name
                    html_path = "../" + parent_name + "/readme.html"

                    kpi_path = os.path.join(parent_path, "kpi.csv")
                    test_id, test_tag = self.get_test_id_test_tag(kpi_path)
                    suite_html_results += """
                    <tr style="text-align: center; margin-bottom: 0; margin-top: 0;">
                        <td>{test_id}</td><td>{test_tag}</td><td><a href="{html_path}" target="_blank">html</a> / 
                        <a href="{pdf_path}" target="_blank">pdf</a> / 
                        <a href="{dir_path}" target="_blank">results_dir</a></td>
                        <td>{parent_name}</td></tr> 
                    """.format(test_id=test_id, test_tag=test_tag, html_path=html_path, pdf_path=pdf_path, dir_path=dir_path, parent_name=parent_name)
        suite_html_results += """
                    </tbody>
                </table>
                <br>
                """

        return suite_html_results

    #
    def db_compare(self):
        pass

# Feature, Sum up the subtests passed/failed from the kpi files for each
# run, poke those into the database, and generate a kpi graph for them.
def main():

    parser = argparse.ArgumentParser(
        prog='lf_inspect.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        read kpi.csv into sqlite database , save png of history and preset on dashboard

            ''',
        description='''\
Read in two databases and compare the inputs
Usage: lf_inspect.py --db  db_one,db_two

        ''')
    parser.add_argument('--path', help=''' --path to where to place the results ''', default='')

    parser.add_argument('--database', help='--database db_one,db_two', default='qa_test_db')
    parser.add_argument('--table', help='--table qa_table  default: qa_table', default='qa_table')
    parser.add_argument('--dir', help="--dir <results directory> default lf_qa", default="lf_inspect")
    # logging configuration:
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")

    args = parser.parse_args()

    # set up logger

    # set the logger level to debug
    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    __database_list = args.database.split(',')
    __dir = args.dir
    __path = args.path
    __table = args.table


    if __path == '' :
        logger.info("--path may be used ")

    # create report class for reporting
    report = lf_report(_path=__path,
                       _results_dir_name=__dir,
                       _output_html="lf_inspect.html",
                       _output_pdf="lf_inspect.pdf")

    # for relative path reporting 
    __lf_inspect_report_path = report.get_path_date_time()

    inspect_db = inspect_sql(
        _path=__path,
        _dir = __dir,
        _database_list=__database_list,
        _table=__table)

    # TODO there would neeed to be comparison parameters passed in 
    # what was going to be used for the comparison.
    # currently use the last two runs
    inspect_db.compare_data()

    # csv_dash.sub_test_information()

    #if args.store:
    #    csv_dash.store()
        

    # generate output reports
    report.set_title("Compare Results: Verification Test Run")
    report.build_banner_left()
    report.start_content_div2()
    report.set_obj_html("Objective", "QA Verification")
    report.build_objective()
    report.set_table_title("Device Under Test")
    report.build_table_title()

    report_path = report.get_path()
    report_basename = os.path.basename(report_path)
    report_url = './../../' + report_basename
    report.build_link("Current Test Suite Results Directory", report_url)

    report_parent_path = report.get_parent_path()
    report_parent_basename = os.path.basename(report_parent_path)
    report_parent_url = './../../../' + report_parent_basename
    report.build_link("All Test-Rig Test Suites Results Directory", report_parent_url)


    report.build_footer()
    html_report = report.write_html_with_timestamp()
    # logger.info("html report: {}".format(html_report))
    print("html report: {}".format(html_report))
    try:
        report.write_pdf_with_timestamp()
    except BaseException:
        logger.info("exception write_pdf_with_timestamp()")


if __name__ == '__main__':
    main()
