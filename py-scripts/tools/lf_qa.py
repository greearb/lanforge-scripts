#!/usr/bin/env python3
# flake8: noqa
'''
File: read kpi.csv place in sql database, create png of historical kpi and present graph on dashboard
Usage: lf_qa.py --store --png --show --path <path to directories to traverse> --database <name of database>

Usage for comparison, not both directories need to be under html-reports 
    lf_qa.py --path <path to directories to traverse> --path_comp <path to compare report> --store --png --database <test.db>

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


class csv_sql:
    def __init__(self,
                 _path='.',
                 _path_comp='',
                 _lf_qa_report_path='',
                 _file='kpi.csv',
                 _database='qa_db',
                 _table='qa_table',
                 _png=False,
                 _test_window_days='7'):
        self.path = _path
        self.path_comp = _path_comp
        self.lf_qa_report_path = _lf_qa_report_path
        logger.debug("lf_qa path: {path}".format(path=self.path))
        logger.debug("lf_qa path_comp: {path}".format(path=self.path_comp))
        logger.debug("lf_qa lf_qa_report_path: {path}".format(path=self.lf_qa_report_path))
        self.test_window_days=_test_window_days
        self.file = _file
        self.database = _database
        self.table = _table
        self.png = _png
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

    def get_dut_info(self):
        # try:
        logger.info(
            "get_dut_info DUT: {DUT} SW:{SW} HW:{HW} SN:{SN}" .format(
                DUT=self.dut_model_num,
                SW=self.dut_sw_version,
                HW=self.dut_hw_version,
                SN=self.dut_serial_num))

        dut_dict = {
            'DUT': [self.dut_model_num],
            'SW version': [self.dut_sw_version],
            'HW version': [self.dut_hw_version],
            'SN': [self.dut_serial_num]
        }
        logger.info('DUT dict: {dict}'.format(dict=dut_dict))
        dut_info_df = pd.DataFrame(dut_dict)
        logger.info("DUT df from dict: {df}".format(df=dut_info_df))

        return dut_info_df

    def get_parent_path(self, _path):
        parent_path = os.path.dirname(_path)
        return parent_path

    # TODO put a wrapper around all the LANforge pertinate information 
    # TODO put in traceback on the exceptions.
    def get_kernel_version_from_meta(sefl, _kpi_path):
        kernel_version = "NA"
        logger.info("read meta path for kernel version:  {_kpi_path}".format(_kpi_path=_kpi_path))
        try:
            meta_data_path = _kpi_path + '/' + '/meta.txt'
            meta_data_fd = open(meta_data_path, 'r')
            for line in meta_data_fd:
                if "lanforge_kernel_version:" in line:
                    kernel_version = line.replace("$ lanforge_kernel_version:", "")
                    kernel_version = test_run.strip()
                    logger.info("meta_data_path: {meta_data_path} Kernel Version: {kernel}".format(
                        meta_data_path=meta_data_path, kernel=kernel_version))
                    break
            meta_data_fd.close()
        except BaseException:
            logger.info("exception reading meta get_kernel_version_from_meta {_kpi_path}".format(
                _kpi_path=_kpi_path))
        return kernel_version                 

    def get_radio_firmware_from_meta(sefl, _kpi_path):
        radio_firmware = "NA"
        logger.info("read meta path for radio firmware version:  {_kpi_path}".format(_kpi_path=_kpi_path))
        try:
            meta_data_path = _kpi_path + '/' + '/meta.txt'
            meta_data_fd = open(meta_data_path, 'r')
            for line in meta_data_fd:
                if "radio_firmware" in line:
                    radio_firmware = line.replace("$ radio_firmware:", "")
                    radio_firmware = test_run.strip()
                    logger.info("meta_data_path: {meta_data_path} Radio Firmware : {radio_fw}".format(
                        meta_data_path=meta_data_path, kernel=kernel_version))
                    break
            meta_data_fd.close()
        except BaseException:
            logger.info("exception reading meta get_kernel_version_from_meta {_kpi_path}".format(
                _kpi_path=_kpi_path))
        return radio_firmware                 


    def get_gui_info_from_meta(sefl, _kpi_path):
        gui_version = "NA"
        gui_build_date = "NA"
        gui_build_date
        logger.debug("read meta path for gui version:  {_kpi_path}".format(_kpi_path=_kpi_path))
        try:
            meta_data_path = _kpi_path + '/' + '/meta.txt'
            meta_data_fd = open(meta_data_path, 'r')
            for line in meta_data_fd:
                if "lanforge_gui_version_full:" in line:
                    # gui_version = line.replace("lanforge_gui_version_full:", "")
                    # gui_version = test_run.strip()

                    pattern = "\"BuildVersion\" : \"(\\S+)\""
                    match = re.search(pattern, line)
                    if (match is not None):
                        gui_version = match.group(1)

                    pattern = "\"BuildDate\" : \"(\\S+\\s+\\S+\\s+\\S+\\s+\\S+\\s+\\S+\\s+\\S+\\s+\\S+)\""
                    match = re.search(pattern, line)
                    if (match is not None):
                        gui_build_date = match.group(1)


                    logger.info("meta_data_path: {meta_data_path} GUI Version: {gui_version} GUI Build Date {gui_build_date}".format(
                        meta_data_path=meta_data_path, gui_version=gui_version,gui_build_date=gui_build_date))

                    break
            meta_data_fd.close()
        
        except BaseException:
            logger.info("exception reading meta get_gui_version_from_meta {_kpi_path}".format(
                _kpi_path=_kpi_path))
        return gui_version, gui_build_date                 

    def get_server_info_from_meta(sefl, _kpi_path):
        server_version = "NA"
        server_build_date = "NA"
        logger.debug("read meta path for server version:  {_kpi_path}".format(_kpi_path=_kpi_path))
        try:
            meta_data_path = _kpi_path + '/' + '/meta.txt'
            meta_data_fd = open(meta_data_path, 'r')
            for line in meta_data_fd:
                if "lanforge_server_version_full:" in line:

                    pattern = "Version: (\\S+)"
                    match = re.search(pattern, line)
                    if (match is not None):
                        server_version = match.group(1)

                    pattern = "Compiled on:  (\\S+\\s+\\S+\\s+\\S+\\s+\\S+\\s+\\S+\\s+\\S+\\s+\\S+)"

                    match = re.search(pattern, line)
                    if (match  is not None):
                        server_build_date = match.group(1)


                    logger.info("meta_data_path: {meta_data_path} server Version: {server_version}".format(
                        meta_data_path=meta_data_path, server_version=server_version))
                    logger.info("meta_data_path: {meta_data_path} server_build_date: {server_build}".format(
                        meta_data_path=meta_data_path, server_build=server_build_date))
                    
                    break

            meta_data_fd.close()
        except BaseException:
            logger.info("exception reading meta get_gui_server_from_meta {_kpi_path}".format(
                _kpi_path=_kpi_path))
        return server_version, server_build_date                

    def get_test_dir_info_from_meta(sefl, _kpi_path):
        test_dir = "NA"
        logger.debug("read meta path for test dir:  {_kpi_path}".format(_kpi_path=_kpi_path))
        try:
            meta_data_path = _kpi_path + '/' + '/meta.txt'
            meta_data_fd = open(meta_data_path, 'r')
            for line in meta_data_fd:
                if "file_meta:" in line:
                    split_line = line.split('/')
                    test_dir = split_line[-2]
                    logger.info("meta_data_path: {meta_data_path} test_dir: {test_dir}".format(
                        meta_data_path=meta_data_path, test_dir=test_dir))
                    break                        

            meta_data_fd.close()
        except BaseException:
            logger.info("exception reading meta get_gui_server_from_meta {_kpi_path}".format(
                _kpi_path=_kpi_path))
        return test_dir                


    #def get_server_from_meta(sefl, _kpi_path):
    #def get_gui_from_meta(sefl, _kpi_path):


    def get_test_id_test_tag(self, _kpi_path):
        test_id = "NA"
        test_tag = "NA"
        use_meta_test_tag = False
        try:
            kpi_df = pd.read_csv(_kpi_path, sep='\t')
            test_id_list = list(kpi_df['test-id'])
            test_id = list(set(test_id_list))
            test_id = test_id[-1]  # done to get element of list
        except BaseException:
            logger.info(
                "WARNING: Is test_id set in Manual Test?  exception reading test_id in csv _kpi_path {kpi_path}".format(
                    kpi_path=_kpi_path))
        try:
            test_tag_list = list(kpi_df['test-tag'])
            test_tag = list(set(test_tag_list))
            test_tag = test_tag[-1]  # done to get element of list
        except BaseException:
            logger.info(
                "WARNING: is test-tag set in Manual Test?, exception reading test-tag in csv _kpi_path {kpi_path}, try meta.txt".format(
                    kpi_path=_kpi_path))

        # if test_tag still NA then try meta file after 5.4.3 the test_tag should be in meta.txt
        try:
            if test_tag == "NA":
                _kpi_path = _kpi_path.replace('kpi.csv', '')
                use_meta_test_tag, test_tag = self.get_test_tag_from_meta(
                    _kpi_path)
        except BaseException:
            logger.info("exception reading meta.txt _kpi_path: {kpi_path}".format(
                kpi_path=_kpi_path))
        if use_meta_test_tag:
            logger.info("test_tag from meta.txt _kpi_path: {kpi_path}".format(
                kpi_path=_kpi_path))
        return test_id, test_tag

    def get_test_run_from_meta(self, _kpi_path):
        test_run = "NA"
        logger.info("read meta path {_kpi_path}".format(_kpi_path=_kpi_path))
        try:
            meta_data_path = _kpi_path + '/' + '/meta.txt'
            meta_data_fd = open(meta_data_path, 'r')
            for line in meta_data_fd:
                if "test_run" in line:
                    test_run = line.replace("$ test_run: ", "")
                    test_run = test_run.strip()
                    logger.info("meta_data_path: {meta_data_path} test_run: {test_run}".format(
                        meta_data_path=meta_data_path, test_run=test_run))
                    break
            meta_data_fd.close()
        except BaseException:
            logger.info("exception reading test_run from {_kpi_path}".format(
                _kpi_path=_kpi_path))

        if test_run == "NA":
            try:
                test_run = _kpi_path.rsplit('/', 2)[0]
                logger.info("try harder test_run: {test_run}".format(test_run=test_run))
            except BaseException:
                logger.info("exception getting test_run from kpi_path")
            logger.info("Try harder test_run: {test_run} _kpi_path: {_kpi_path}".format(test_run=test_run, _kpi_path=_kpi_path))
        return test_run

    # TODO retrieve the kernel, GUI, and Server information

    def get_test_tag_from_meta(self, _kpi_path):
        test_tag = "NA"
        use_meta_test_tag = False
        gui_version_5_4_3 = False
        logger.info("read meta path {_kpi_path}".format(_kpi_path=_kpi_path))
        try:
            meta_data_path = _kpi_path + '/' + 'meta.txt'
            meta_data_fd = open(meta_data_path, 'r')
            for line in meta_data_fd:
                if "gui_version:" in line:
                    gui_version = line.replace("$ lanforge_gui_version:", "")
                    gui_version = gui_version.strip()
                    if gui_version == '5.4.3':
                        gui_version_5_4_3 = True
                        use_meta_test_tag = True
                    logger.info("meta_data_path: {meta_data_path} lanforge_gui_version: {gui_version} 5.4.3: {gui_version_5_4_3}".format(
                        meta_data_path=meta_data_path, gui_version=gui_version, gui_version_5_4_3=gui_version_5_4_3))
            meta_data_fd.close()
            if gui_version_5_4_3:
                meta_data_fd = open(meta_data_path, 'r')
                test_tag = 'NA'
                for line in meta_data_fd:
                    if "test_tag" in line:
                        test_tag = line.replace("test_tag", "")
                        test_tag = test_tag.strip()
                        logger.info(
                            "meta_data_path {meta_data_path} test_tag {test_tag}".format(
                                meta_data_path=meta_data_path,
                                test_tag=test_tag))
                meta_data_fd.close()
        except BaseException:
            logger.info("exception reading test_tag from {_kpi_path}".format(
                _kpi_path=_kpi_path))

        return use_meta_test_tag, test_tag

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
            if "lf_qa" in str(pdf_info):
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

    # TODO can use alternate path passed in as a comparison directory
    # Would need to figure out how to do the relative paths
    # Or figure out a way to 
    # os.path.relpath(path1, path2)
    # os.path.exists 
    # https://docs.python.org/3.10/library/os.path.html
    def get_kpi_chart_html_relative_compare(self):       
        kpi_chart_html = """
            <table border="0">
                <tbody>
        """
        # this gets the path to the data used 
        # reportes need to be relative to path
        path = Path(self.path)
        path_comp = Path(self.path_comp)
        # Hard code for now
        kpi_chart_list = list(path.glob('**/kpi-chart*.png'))
        kpi_chart_comp_list = list(path_comp.glob('**/kpi-chart*.png'))
        table_index = 0
        for kpi_chart in kpi_chart_list:
            parent_path = os.path.dirname(kpi_chart)
            kpi_path = os.path.join(parent_path, "kpi.csv")
            test_tag, test_id = self.get_test_id_test_tag(kpi_path)
            # Path returns a list of objects
            kpi_chart = os.path.abspath(kpi_chart)

            if "print" in kpi_chart:
                pass
            else:
                # do relative paths to the lf_qa_report_path
                kpi_chart_relative = os.path.relpath(kpi_chart, self.lf_qa_report_path)
                logger.debug("kpi_chart_relative: {r_chart}".format(r_chart=kpi_chart_relative))

                kpi_chart_results_dir = os.path.dirname(kpi_chart_relative)
                logger.debug("results_dir: {dir_path}".format(dir_path=kpi_chart_results_dir))

                if (table_index % 2) == 0:
                    kpi_chart_html += """<tr>"""
                kpi_chart_html += """
                    <td>
                        {test_tag}  {test_id} 
                        <a href="{dir_path}" target="_blank">results_dir</a>
                    </td>
                    <td>
                        <a href="{kpi_chart_ref}"  target="_blank">
                            <img src="{kpi_chart_src}" style="width:400px;max-width:400px" title="{kpi_chart_title}">
                        </a>
                    </td>
                """.format(test_tag=test_tag, test_id=test_id, dir_path=kpi_chart_results_dir, kpi_chart_ref=kpi_chart_relative, kpi_chart_src=kpi_chart_relative, kpi_chart_title=kpi_chart_relative)

                # see if there is a matching chart in the comparison directory
                # will need to refactor into separate method
                kpi_chart_comp_found = False
                for kpi_chart_comp in kpi_chart_comp_list:
                    parent_path_comp = os.path.dirname(kpi_chart_comp)
                    kpi_path_comp = os.path.join(parent_path_comp, "kpi.csv")
                    test_tag_comp, test_id_comp = self.get_test_id_test_tag(kpi_path_comp)
                    if test_tag == test_tag_comp and test_id == test_id_comp:
                        kpi_chart_comp_found = True
                        logger.debug("test_tag : {tag} test_tag_comp : {ctag} test_id : {test_id} test_id_comp : {test_id_comp}".format(
                            tag=test_tag,ctag=test_tag_comp,test_id=test_id,test_id_comp=test_id_comp
                        ) )
                        # get relative path 
                        kpi_chart_comp_relative = os.path.relpath(kpi_chart_comp, self.lf_qa_report_path)
                        logger.debug("kpi_chart_comp_relative: {r_chart}".format(r_chart=kpi_chart_comp_relative))

                        compare_results_dir = os.path.dirname(kpi_chart_comp_relative)
                        logger.debug("compare_results_dir: {dir_path}".format(dir_path=compare_results_dir))
                        
                        kpi_chart_html += """
                            <td>
                                {test_tag}  {test_id} 
                                <a href="{dir_path}" target="_blank">compare_results_dir</a>
                            </td>
                            <td>
                                <a href="{kpi_chart_ref}"  target="_blank">
                                    <img src="{kpi_chart_src}" style="width:400px;max-width:400px" title="{kpi_chart_title}">
                                </a>
                            </td>
                        """.format(test_tag=test_tag_comp, test_id=test_id_comp, dir_path=compare_results_dir,kpi_chart_ref=kpi_chart_comp_relative, kpi_chart_src=kpi_chart_comp_relative, kpi_chart_title=kpi_chart_comp_relative)
                        break
                    if kpi_chart_comp_found:
                        # even if comparison not found increase the index
                        table_index += 1
                        if (table_index % 2) == 0:
                            kpi_chart_html += """</tr>"""
                
                if not kpi_chart_comp_found:
                    # even if comparison not found increase the index
                    table_index += 1
                    if (table_index % 2) == 0:
                        kpi_chart_html += """</tr>"""

        if (table_index % 2) != 0:
            kpi_chart_html += """</tr>"""
        kpi_chart_html += """</tbody></table>"""
        return kpi_chart_html


    def get_kpi_chart_html_relative(self):
        kpi_chart_html = """
            <table border="0">
                <tbody>
        """
        path = Path(self.path)
        # Hard code for now
        kpi_chart_list = list(path.glob('**/kpi-chart*.png'))
        table_index = 0
        for kpi_chart in kpi_chart_list:
            parent_path = os.path.dirname(kpi_chart)
            kpi_path = os.path.join(parent_path, "kpi.csv")
            test_tag, test_id = self.get_test_id_test_tag(kpi_path)
            # Path returns a list of objects
            kpi_chart = os.path.abspath(kpi_chart)
            if "print" in kpi_chart:
                pass
            else:
                # do relative paths to the lf_qa_report_path
                kpi_chart_relative = os.path.relpath(kpi_chart, self.lf_qa_report_path)
                logger.debug("kpi_chart_relative: {r_chart}".format(r_chart=kpi_chart_relative))

                kpi_chart_results_dir = os.path.dirname(kpi_chart_relative)
                logger.debug("results_dir: {dir_path}".format(dir_path=kpi_chart_results_dir))

                if (table_index % 2) == 0:
                    kpi_chart_html += """<tr>"""
                kpi_chart_html += """
                    <td>
                        {test_tag}  {test_id}
                        <a href="{dir_path}" target="_blank">results_dir</a>
                    </td>
                    <td>
                        <a href="{kpi_chart_0}"  target="_blank">
                            <img src="{kpi_chart_1}" style="width:400px;max-width:400px" title="{kpi_chart_2}">
                        </a>
                    </td>
                """.format(test_tag=test_tag, test_id=test_id, dir_path=kpi_chart_results_dir, kpi_chart_0=kpi_chart_relative, kpi_chart_1=kpi_chart_relative, kpi_chart_2=kpi_chart_relative)
                table_index += 1
                if (table_index % 2) == 0:
                    kpi_chart_html += """</tr>"""
        if (table_index % 2) != 0:
            kpi_chart_html += """</tr>"""
        kpi_chart_html += """</tbody></table>"""
        return kpi_chart_html


    # information on sqlite database
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
    # sqlite browser:
    # Fedora  sudo dnf install sqlitebrowser
    # Ubuntu sudo apt-get install sqlite3
    #
    def store(self):
        logger.info("reading kpi and storing in db {}".format(self.database))
        path = Path(self.path)
        logger.info("store path {path}".format(path=path))
        logger.info("self.path  {path}".format(path=self.path))
        self.kpi_list = list(path.glob('**/kpi.csv'))  # Hard code for now

        if not self.kpi_list:
            logger.info("WARNING: used --store , no new kpi.csv found, check input path or remove --store from command line")

        rows = []
        for kpi in self.kpi_list:  # TODO note empty kpi.csv failed test
            df_kpi_tmp = pd.read_csv(kpi, sep='\t')
            # only store the path to the kpi.csv file
            _kpi_path = str(kpi).replace('kpi.csv', '')
            df_kpi_tmp['kpi_path'] = _kpi_path
            test_run = self.get_test_run_from_meta(_kpi_path)
            df_kpi_tmp['test_run'] = test_run

            use_meta_test_tag, test_tag = self.get_test_tag_from_meta(_kpi_path)
            if use_meta_test_tag:
                df_kpi_tmp['test-tag'] = test_tag

            test_dir = self.get_test_dir_info_from_meta(_kpi_path)
            # test_dir = test_dir.replace('-',' ')
            df_kpi_tmp['test_dir'] = test_dir

            logger.info("test_dir: {test_dir}".format(test_dir=test_dir))

            df_kpi_tmp['kernel'] = self.get_kernel_version_from_meta(_kpi_path)
            df_kpi_tmp['radio_fw'] = self.get_radio_firmware_from_meta(_kpi_path)
            df_kpi_tmp['gui_ver'], df_kpi_tmp['gui_build_date'] = self.get_gui_info_from_meta(_kpi_path)
            df_kpi_tmp['server_ver'], df_kpi_tmp['server_build_date'] = self.get_server_info_from_meta(_kpi_path)

            # this next line creats duplicate entries
            self.df = pd.concat([self.df,df_kpi_tmp], ignore_index=True)


        self.conn = sqlite3.connect(self.database)
        try:
            self.df.to_sql(self.table, self.conn, if_exists='append')
        except BaseException:
            logger.info("attempt to append to database with different column layout,\
                 caused an exception, input new name --database <new name>")
            print(
                "Error attempt to append to database with different column layout,\
                     caused an exception, input new name --database <new name>",
                file=sys.stderr)
            exit(1)
        self.conn.close()

    # information on sqlite database
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
    # sqlite browser:
    # Fedora  sudo dnf install sqlitebrowser
    # Ubuntu sudo apt-get install sqlite3
    #
    def store_comp(self):
        logger.info("reading kpi and storing in db {}".format(self.database))
        path = Path(self.path_comp)
        logger.info("store path {path}".format(path=path))
        logger.info("self.path_comp  {path}".format(path=self.path_comp))
        self.kpi_list = list(path.glob('**/kpi.csv'))  # Hard code for now

        if not self.kpi_list:
            logger.info("WARNING: used --store , no new kpi.csv found, check input path or remove --store from command line")

        for kpi in self.kpi_list:  # TODO note empty kpi.csv failed test
            df_kpi_tmp = pd.read_csv(kpi, sep='\t')
            # only store the path to the kpi.csv file
            _kpi_path = str(kpi).replace('kpi.csv', '')
            df_kpi_tmp['kpi_path'] = _kpi_path
            test_run = self.get_test_run_from_meta(_kpi_path)
            df_kpi_tmp['test_run'] = test_run

            use_meta_test_tag, test_tag = self.get_test_tag_from_meta(_kpi_path)
            if use_meta_test_tag:
                df_kpi_tmp['test-tag'] = test_tag

            test_dir = self.get_test_dir_info_from_meta(_kpi_path)
            # test_dir = test_dir.replace('-',' ')
            df_kpi_tmp['test_dir'] = test_dir

            logger.info("test_dir: {test_dir}".format(test_dir=test_dir))

            df_kpi_tmp['kernel'] = self.get_kernel_version_from_meta(_kpi_path)
            df_kpi_tmp['radio_fw'] = self.get_radio_firmware_from_meta(_kpi_path)
            df_kpi_tmp['gui_ver'], df_kpi_tmp['gui_build_date'] = self.get_gui_info_from_meta(_kpi_path)
            df_kpi_tmp['server_ver'], df_kpi_tmp['server_build_date'] = self.get_server_info_from_meta(_kpi_path)
            
            # this next line creates duplicate entries
            # df_kpi_tmp = df_kpi_tmp.append(df_kpi_tmp, ignore_index=True)
            self.df = self.df.append(df_kpi_tmp, ignore_index=True)

        self.conn = sqlite3.connect(self.database)
        try:
            self.df.to_sql(self.table, self.conn, if_exists='append')
        except BaseException:
            logger.info("attempt to append to database with different column layout,\
                 caused an exception, input new name --database <new name>")
            print(
                "Error attempt to append to database with different column layout,\
                     caused an exception, input new name --database <new name>",
                file=sys.stderr)
            exit(1)
        self.conn.close()



    def generate_png(self, group, test_id_list, test_tag,
                     test_rig, kpi_path_list, kpi_fig, df_tmp):
        # save the figure - figures will be over written png
        # for testing
        png_server_img = ''
        # generate the png files
        logger.info("generate png and kpi images from kpi kpi_path:{}".format(
            df_tmp['kpi_path']))
            # LAN-1535 scripting: test_l3.py output masks other output when browsing (index.html) create relative paths in reports
        # generate png img path
        png_path = os.path.join(
            kpi_path_list[-1], "{}_{}_{}_kpi.png".format(group, test_tag, test_rig))
        png_path = png_path.replace(' ', '')
        # generate html graphics path
        html_path = os.path.join(
            kpi_path_list[-1], "{}_{}_{}_kpi.html".format(group, test_tag, test_rig))
        html_path = html_path.replace(' ', '')
        
        # generate png image
        png_present = True
        try:
            kpi_fig.write_image(png_path, scale=1, width=1200, height=300)
        except ValueError as err:
            logger.info("ValueError kpi_fig.write_image {msg}".format(msg=err))
            png_present = False
            # exit(1)
        except BaseException as err:
            logger.info("BaseException kpi_fig.write_image{msg}".format(msg=err))
            png_present = False
            # exit(1)
        # generate html image (interactive)
        # TODO Do not crash if a PNG is not present
        if png_present:
            kpi_fig.write_html(html_path)
            # Relative path
            img_kpi_html_path_relative = os.path.relpath(html_path, self.lf_qa_report_path)
            png_img_path_relative = os.path.relpath(png_path, self.lf_qa_report_path)

            self.html_results += """
            <a href={img_kpi_html_path} target="_blank">
                <img src={png_server_img}>
            </a>
            """.format(img_kpi_html_path=img_kpi_html_path_relative, png_server_img=png_img_path_relative)

            # link to interactive results
            report_index_html_path = kpi_path_list[-1] + "readme.html"
            relative_report_index_html = os.path.relpath(report_index_html_path, self.lf_qa_report_path)

            self.html_results += """<a href={report_index_html_path} target="_blank">{test_id}_{group}_{test_tag}_{test_rig}_Report </a>
            """.format(report_index_html_path=relative_report_index_html, test_id=test_id_list[-1], group=group, test_tag=test_tag, test_rig=test_rig)
            self.html_results += """<br>"""
            self.html_results += """<br>"""
            self.html_results += """<br>"""
            self.html_results += """<br>"""
            self.html_results += """<br>"""

    
    # TODO determin the subtest pass and fail graph
    # df is sorted by date oldest to newest
    # get the test_run for last run
    # query the db for  all pass and fail or last run
    # put in table
    def sub_test_information(self):
        logger.info("generate table and graph from subtest data per run: {}".format(
            time.time()))
        # https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html-
        self.conn = sqlite3.connect(self.database)
        # current connection is sqlite3 /TODO move to SQLAlchemy
        df3 = pd.read_sql_query(
            "SELECT * from {}".format(self.table), self.conn)
        # sort by date from oldest to newest.
        try:
            df3 = df3.sort_values(by='Date')
        except BaseException:
            logger.info(("Database empty reading subtest: "
                   "KeyError(key) when sorting by Date for db: {db},"
                   " check Database name, path to kpi, typo in path, exiting".format(db=self.database)))
            exit(1)
        self.conn.close()

        # test_run are used for detemining the subtest-pass, subtest-fail
        # the tests are sorted by date above.
        test_run_list = list(df3['test_run'])
        logger.info("test_run_list first [0] {}".format(test_run_list[0]))
        logger.info("test_run_list last [-1] {}".format(test_run_list[-1]))

        self.test_run = test_run_list[-1]
        # collect this runs subtest totals
        df_tmp = df3.loc[df3['test_run'] == self.test_run]
        subtest_passed_list = list(df_tmp['Subtest-Pass'])
        subtest_failed_list = list(df_tmp['Subtest-Fail'])

        try:
            self.subtest_passed = int(sum(subtest_passed_list))
            self.subtest_failed = int(sum(subtest_failed_list))
            self.subtest_total = self.subtest_passed + self.subtest_failed
        except BaseException:
            warning_msg = ("WARNING subtest values need to be filtered or"
                           " Test is not behaving in filling out subtest values")
            logger.warning(warning_msg)
            logger.warning("{warn}".format(warn=warning_msg))
            logger.debug("stderr : {file}".format(file=sys.stderr))
            logger.warning("{warn}".format(warn=warning_msg))
            logger.debug("stdout : {file}".format(file=sys.stdout))

            self.subtest_passed = 0
            self.subtest_failed = 0
            self.subtest_total = 0

        logger.info("{run} subtest Total:{total} Pass:{passed} Fail:{failed}".format(
            run=self.test_run, total=self.subtest_total, passed=self.subtest_passed, failed=self.subtest_failed
        ))

        # extract the DUT information from last run
        self.dut_model_num_list = list(set(list(df_tmp['dut-model-num'])))
        self.dut_model_num_list = [x for x in self.dut_model_num_list if x is not None]
        if self.dut_model_num_list:
            self.dut_model_num = self.dut_model_num_list[-1]

        self.dut_sw_version_list = list(set(list(df_tmp['dut-sw-version'])))
        self.dut_sw_version_list = [x for x in self.dut_sw_version_list if x is not None]
        if self.dut_sw_version_list:
            self.dut_sw_version = self.dut_sw_version_list[-1]

        self.dut_hw_version_list = list(set(list(df_tmp['dut-hw-version'])))
        self.dut_hw_version_list = [x for x in self.dut_hw_version_list if x is not None]
        if self.dut_hw_version_list:
            self.dut_hw_version = self.dut_hw_version_list[-1]

        self.dut_serial_num_list = list(set(list(df_tmp['dut-serial-num'])))
        self.dut_serial_num_list = [x for x in self.dut_serial_num_list if x is not None]
        if self.dut_serial_num_list:
            self.dut_serial_num = self.dut_serial_num_list[-1]

        logger.info(
            "In png DUT: {DUT} SW:{SW} HW:{HW} SN:{SN}" .format(
                DUT=self.dut_model_num,
                SW=self.dut_sw_version,
                HW=self.dut_hw_version,
                SN=self.dut_serial_num))

    def generate_graph_png(self):
        logger.info(
            "generate png and html to display, generate time: {}".format(
                time.time()))

        # https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html-
        self.conn = sqlite3.connect(self.database)
        # current connection is sqlite3 /TODO move to SQLAlchemy
        df3 = pd.read_sql_query(
            "SELECT * from {}".format(self.table), self.conn)
        # sort by date from oldest to newest.
        try:
            df3 = df3.sort_values(by='Date')
        except BaseException:
            logger.info("Database empty: KeyError(key) when sorting by Date, check Database name, path to kpi, typo in path, exiting")
            exit(1)
        self.conn.close()

        # graph group and test-tag are used for detemining the graphs, can use any columns
        # the following list manipulation removes the duplicates
        graph_group_list = list(df3['Graph-Group'])
        graph_group_list = [x for x in graph_group_list if x is not None]
        graph_group_list = list(set(graph_group_list))
        logger.info("graph_group_list: {}".format(graph_group_list))

        # prior to 5.4.3 there was not test-tag, the test tag is in the meta data
        # logger.info("dataframe df3 {df3}".format(df3=df3))

        test_tag_list = list(df3['test-tag'])
        test_tag_list = [x for x in test_tag_list if x is not None]
        test_tag_list = list(sorted(set(test_tag_list)))
        # logger.info("test_tag_list: {}".format(test_tag_list) )

        test_rig_list = list(df3['test-rig'])
        test_rig_list = [x for x in test_rig_list if x is not None]
        test_rig_list = list(sorted(set(test_rig_list)))
        self.test_rig_list = test_rig_list
        logger.info("test_rig_list: {}".format(test_rig_list))

        # Time now generating the report
        time_now = round(time.time() * 1000)
        test_window_epoch = int(self.test_window_days) * 86400000

        # create the rest of the graphs
        for test_rig in test_rig_list:
            for test_tag in test_tag_list:
                for group in graph_group_list:
                    df_tmp = df3.loc[(df3['test-rig'] == test_rig) & (
                        df3['Graph-Group'] == str(group)) & (df3['test-tag'] == str(test_tag))]
                    if not df_tmp.empty:
                        # Note if graph group is score there is sub tests for pass and fail
                        # would like a percentage

                        df_tmp = df_tmp.sort_values(by='Date')
                        test_id_list = list(df_tmp['test-id'])
                        kpi_path_list = list(df_tmp['kpi_path'])

                        # get Device Under Test Information ,
                        # the set command uses a hash , sorted puts it back in order
                        # the set reduces the redundency the filster removes None
                        # list puts it back into a list
                        # This code is since the dut is not passed in to lf_qa.py when
                        # regernation of graphs from db

                        # find the last Date in the dataframe see if it is a test no longer run
                        recent_test_run = df_tmp["Date"].iloc[-1]
                        oldest_test_run = df_tmp["Date"].iloc[0]
                        # if the recent test is over a week old do not include in run
                        # 1 day = 86400000 milli seconds
                        # 1 week = 604800000 milli seconds
                        time_difference = int(time_now) -int(recent_test_run)
                        logger.info("time_now: {time_now} recent_test_run: {recent_test_run} difference: {time_difference} test_window_epoch: {test_window_epoch} oldest_test_run: {oldest_test_run}".format(
                            time_now=time_now,recent_test_run=recent_test_run,test_window_epoch=test_window_epoch, time_difference=time_difference, oldest_test_run=oldest_test_run))
                        ##if (time_difference) < 604800000:  # TODO have window be configurable
                        if (time_difference) < test_window_epoch:  # TODO have window be configurable
                            units_list = list(df_tmp['Units'])
                            logger.info(
                                "GRAPHING::: test-rig {} test-tag {}  Graph-Group {}".format(test_rig, test_tag, group))
                            # group of Score will have subtest
                            if group == 'Score':
                                # Print out the Standard Score report
                                kpi_fig = (
                                    px.scatter(
                                        df_tmp,
                                        x="Date",
                                        y="numeric-score",
                                        custom_data=[
                                            'numeric-score',
                                            'Subtest-Pass',
                                            'Subtest-Fail',
                                            'kernel'
                                            ],
                                        color="short-description",
                                        hover_name="short-description",
                                        size_max=60)).update_traces(
                                    mode='lines+markers')

                                kpi_fig.update_traces(
                                    hovertemplate="<br>".join([
                                        "kernel-version: %{customdata[4]}",
                                        "numeric-score: %{customdata[0]}",
                                        "Subtest-Pass: %{customdata[1]}",
                                        "Subtest-Fail: %{customdata[2]}"
                                    ])
                                )

                                kpi_fig.update_layout(
                                    title="{test_id} : {group} : {test_tag} : {test_rig}".format(
                                        test_id=test_id_list[-1], group=group, test_tag=test_tag, test_rig=test_rig),
                                    xaxis_title="Time",
                                    yaxis_title="{}".format(units_list[-1]),
                                    xaxis={'type': 'date'}
                                )
                                kpi_fig.update_layout(autotypenumbers='convert types')

                                self.generate_png(df_tmp=df_tmp,
                                                group=group,
                                                test_id_list=test_id_list,
                                                test_tag=test_tag,
                                                test_rig=test_rig,
                                                kpi_path_list=kpi_path_list,
                                                kpi_fig=kpi_fig)

                            else:
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
                                            'server_build_date',
                                            'dut-hw-version',
                                            'dut-sw-version',
                                            'dut-model-num',
                                            'dut-serial-num'
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
                                        "dut-hw-version: %{customdata[9]}",
                                        "dut-sw-version: %{customdata[10]}",
                                        "dut-model-num: %{customdata[11]}",
                                        "dut-serial-num: %{customdata[12]}",
                                    ])
                                )

                                kpi_fig.update_layout(autotypenumbers='convert types')

                                self.generate_png(df_tmp=df_tmp,
                                                group=group,
                                                test_id_list=test_id_list,
                                                test_tag=test_tag,
                                                test_rig=test_rig,
                                                kpi_path_list=kpi_path_list,
                                                kpi_fig=kpi_fig)


# Feature, Sum up the subtests passed/failed from the kpi files for each
# run, poke those into the database, and generate a kpi graph for them.
def main():

    parser = argparse.ArgumentParser(
        prog='lf_qa.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        read kpi.csv into sqlite database , save png of history and preset on dashboard

            ''',
        description='''\
File: read kpi.csv place in sql database, create png of historical kpi and present graph on dashboard
Usage: lf_qa.py --store --png --path <path to directories to traverse> --database <name of database>

        ''')
    parser.add_argument(
        '--path',
        help='''
            --path top directory of the test suite directory, 
            for example /html-reports/TEST_RUNS/TEST_SUITE  
            /home/lanforge/html-reports/ct_us/lf_check_suite
            ''',
        default='')
    parser.add_argument(
        '--path_comp',
        help='''
            --path_comp , this is the directory to compare results from a previous run.
            top directory path to kpi if regererating database or png files,
            for example /html-reports/TEST_RUNS/TEST_SUITE_COMPARE 
            /home/lanforge/html-reports/ct_us/lf_check_compare_suite
            default: ''
            ''',
        default='')

    parser.add_argument('--file', help='--file kpi.csv  default: kpi.csv',
                        default='kpi.csv')  # TODO is this needed
    parser.add_argument(
        '--database',
        help='--database qa_test_db  default: qa_test_db',
        default='qa_test_db')
    parser.add_argument(
        '--table',
        help='--table qa_table  default: qa_table',
        default='qa_table')
    parser.add_argument(
        '--store',
        help='--store , store kpi to db, action store_true',
        action='store_true')
    parser.add_argument(
        '--store_comp',
        help='--store_comp , store compared data kpi to db, action store_true',
        action='store_true')
    parser.add_argument(
        '--png',
        help='--png,  generate png for kpi in path, generate display, action store_true',
        action='store_true')
    parser.add_argument(
        '--dir',
        help="--dir <results directory> default lf_qa",
        default="lf_qa")

    parser.add_argument('--test_window_days', help="--test_window,  days to look back for test results , used to elimnate older tests being reported default 7 days", default="7")

    parser.add_argument('--test_suite', help="--test_suite , the test suite is to help identify which suite was run ", default="lf_qa")

    parser.add_argument('--server', help="--server , server switch is deprecated ", default="")


    # logging configuration:
    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")

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

    __path = args.path
    if args.path_comp != '' and os.path.exists(args.path_comp):
        __path_comp = args.path_comp
    elif args.path_comp == '':
        __path_comp = ''
    else:
        __path_comp = ''
        logger.warning("Comparison path does not exist, entered: {path_comp}".format(path_comp=args.path_comp))
    __file = args.file
    __database = args.database
    __table = args.table
    __png = args.png
    __dir = args.dir
    __test_window_days = args.test_window_days


    logger.info("config:\
            path:{path} file:{file}\
            database:{database} table:{table} \
            store:{store} png:{png}" .format(
        path=__path, file=__file,
        database=__database, table=__table,
        store=args.store, png=args.png))

    if __path == '' and args.store:
        logger.info("--path <path of kpi.csv> must be entered if --store ,  exiting")
        exit(1)
    elif not args.store:
        if args.png:
            logger.info("if --png set to create png files from database")
        elif not args.png:
            logger.info("Need to enter an action of --store --png ")
            exit(1)

    # create report class for reporting
    report = lf_report(_path=__path,
                       _results_dir_name=__dir,
                       _output_html="lf_qa.html",
                       _output_pdf="lf_qa.pdf")

    # for relative path reporting 
    __lf_qa_report_path = report.get_path_date_time()

    csv_dash = csv_sql(
        _path=__path,
        _path_comp = __path_comp,
        _lf_qa_report_path = __lf_qa_report_path,
        _file=__file,
        _database=__database,
        _table=__table,
        _png=__png,
        _test_window_days=__test_window_days)
    # csv_dash.sub_test_information()

    if args.store:
        csv_dash.store()
        
    if args.store_comp:
        csv_dash.store_comp()

    if args.png:
        csv_dash.sub_test_information()
        csv_dash.generate_graph_png()

        # generate output reports
        report.set_title("LF QA: Verification Test Run")
        report.build_banner_left()
        report.start_content_div2()
        report.set_obj_html("Objective", "QA Verification")
        report.build_objective()
        report.set_table_title("Device Under Test")
        report.build_table_title()
        dut_info_df = csv_dash.get_dut_info()
        logger.info("DUT Results: {}".format(dut_info_df))
        report.set_table_dataframe(dut_info_df)
        report.build_table()

        test_rig_list = csv_dash.get_test_rig_list()
        # keep the list, currently one test bed results
        if test_rig_list:
            report.set_table_title("Test Rig: {} Links".format(test_rig_list[-1]))
            report.build_table_title()
        else:
            note = '''
                lf_qa.py Test Rig field is empty , 
                for wifi_capacity consider setting Test Rig ID and Test Tag under Select Output tab
                for dataplane and ap_auto set Test Rig ID and Test Tag under the Report Configuration tab
                No reaults will be generated for Test Rig field empty
                '''

            logger.info("lf_qa.py Test Rig field in empty")
            logger.info(note)
            report.set_table_title("Test Rig field in kpi is empty")
            report.build_table_title

        # use relative paths
        pdf_file = report.get_pdf_file()
        # pdf_parent_path = os.path.dirname(pdf_link_path)
        # pdf_parent_name = os.path.basename(pdf_parent_path)
        
        
        pdf_url = './' + pdf_file
        report.build_pdf_link("PDF_Report", pdf_url)

        report_path = report.get_path()
        report_basename = os.path.basename(report_path)
        report_url = './../../' + report_basename
        report.build_link("Current Test Suite Results Directory", report_url)

        report_parent_path = report.get_parent_path()
        report_parent_basename = os.path.basename(report_parent_path)
        report_parent_url = './../../../' + report_parent_basename
        report.build_link("All Test-Rig Test Suites Results Directory", report_parent_url)


        # links table for tests 
        report.set_table_title("Test Suite")
        report.build_table_title()
        suite_html = csv_dash.get_suite_html()
        logger.info("suite_html {}".format(suite_html))
        report.set_custom_html(suite_html)
        report.build_custom()

        # sub test summary
        lf_subtest_summary = pd.DataFrame()
        lf_subtest_summary['Subtest Total'] = [csv_dash.subtest_total]
        lf_subtest_summary['Subtest Passed'] = [csv_dash.subtest_passed]
        lf_subtest_summary['Subtest Falied'] = [csv_dash.subtest_failed]

        report.set_table_title("Suite Subtest Summary")
        report.build_table_title()
        report.set_table_dataframe(lf_subtest_summary)
        report.build_table()

        # png summary of test
        report.set_table_title("Suite Summary")
        report.build_table_title()

        if args.path_comp != '':
            kpi_chart_html = csv_dash.get_kpi_chart_html_relative_compare()
        else:
            kpi_chart_html = csv_dash.get_kpi_chart_html_relative()

        report.set_custom_html(kpi_chart_html)
        report.build_custom()

        report.set_table_title("QA Test Results")
        report.build_table_title()
        report.build_text()
        html_results = csv_dash.get_html_results()
        report.set_custom_html(html_results)
        report.build_custom()
        report.build_footer()
        html_report = report.write_html_with_timestamp()
        # logger.info("html report: {}".format(html_report))
        # DO NOT remove print statement
        print("html report: {}".format(html_report))
        try:
            report.write_pdf_with_timestamp()
        except BaseException:
            logger.info("exception write_pdf_with_timestamp()")


if __name__ == '__main__':
    main()
