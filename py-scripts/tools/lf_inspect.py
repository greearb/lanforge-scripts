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
                 _database_list=[]):
        self.path = _path
        self.dir = _dir
        logger.debug("path: {path}".format(path=self.path))
        logger.debug("dir: {dir}".format(dir=self.dir))
        self.database_list = _database_list
        self.kpi_list = []
        self.html_list = []
        self.conn = None
        self.df = pd.DataFrame()
        self.plot_figure = []
        self.html_results = ""
        self.test_rig_list = []
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

    # Helper methods
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

    if __path == '' :
        logger.info("--path may be used ")

    # create report class for reporting
    report = lf_report(_path=__path,
                       _results_dir_name=__dir,
                       _output_html="lf_inspect.html",
                       _output_pdf="lf_inspect.pdf")

    # for relative path reporting 
    __lf_qa_report_path = report.get_path_date_time()

    inspect_db = inspect_sql(
        _path=__path,
        _dir = __dir,
        _database_list=__database_list)

    # csv_dash.sub_test_information()

    #if args.store:
    #    csv_dash.store()
        

    # generate output reports
    report.set_title("Compare Reqults: Verification Test Run")
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
