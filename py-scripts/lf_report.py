#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import matplotlib as mpl 
import numpy as np 
import pandas as pd
import pdfkit
import math

# internal candela references included during intial phases, to be deleted at future date
# https://candelatech.atlassian.net/wiki/spaces/LANFORGE/pages/372703360/Scripting+Data+Collection+March+2021
# base report class
class lf_report():
    def __init__(self,
                _dataframe="",
                _title="LANForge Test Run Heading",
                _table_title="LANForge Table Heading",
                _graph_title="LANForge Graph Title",
                _obj = "",
                _obj_title = "",
                _date="1/1/2-21 00:00(UTC)",
                _output_html="outfile.html",
                _output_pdf="outfile.pdf"):

            self.dataframe=_dataframe
            self.title=_title
            self.table_title=_table_title
            self.graph_title=_graph_title
            self.date=_date
            self.output_html=_output_html
            self.output_pdf=_output_pdf
            self.banner_html = ""
            self.graph_titles=""
            self.graph_image=""
            self.html = ""
            self.custom_html = ""
            self.objective = _obj
            self.obj_title = _obj_title
    

    def set_title(self,_title):
        self.title = _title

    def set_table_title(self,_table_title):
        self.table_title = _table_title

    def set_graph_title(self,_graph_title):
        self.graph_title = _graph_title

    def set_date(self,_date):
        self.date = _date

    def set_dataframe(self,_dataframe):
        self.dataframe = _dataframe

    def set_custom_html(self,_custom_html):
        self.custom_html = _custom_html

    def set_obj_html(self,_obj_title, _obj ):
        self.objective = _obj
        self.obj_title = _obj_title

    def set_graph_image(self,_graph_image):
        self.graph_image = _graph_image

    def write_html(self): 
            # dataframe_html = self.dataframe.to_html(index=False)  # have the index be able to be passed in.
            # self.build_banner()
            # self.build_table_title()
            # self.html = self.banner_html + self.table_html +  dataframe_html
            test_file = open(self.output_html, "w")
            test_file.write(self.html)
            test_file.close()
            return self.html

    def write_pdf(self):
            # write to pdf
            # write logic to generate pdf here
            # wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
            # sudo apt install ./wkhtmltox_0.12.6-1.focal_amd64.deb
            options = {"enable-local-file-access" : None}  # prevent eerror Blocked access to file
            pdfkit.from_file(self.output_html, self.output_pdf, options=options)


    def generate_report(self):
        self.write_html()            
        self.write_pdf()

    # only use is pass all data in constructor, no graph output
    def build_all(self):
        self.build_banner()
        self.build_table_title()
        self.build_table()

    def build_banner(self):
        self.banner_html = """
               <!DOCTYPE html>
                <html lang='en'>
                <head>
                <meta charset='UTF-8'>
                <meta name='viewport' content='width=device-width, initial-scale=1' />
                <br>
                </head>

                <title>BANNER </title></head>
                <body>
                <div class='Section report_banner-1000x205' style='background-image:url("banner.png");background-repeat:no-repeat;padding:0;margin:0;min-width:1000px; min-height:205px;width:1000px; height:205px;max-width:1000px; max-height:205px;'>
                <br>
                <img align='right' style='padding:25;margin:5;width:200px;' src="CandelaLogo2-90dpi-200x90-trans.png" border='0' />

                <div class='HeaderStyle'>
                <br>
                <h1 class='TitleFontPrint' style='color:darkgreen;'>""" + str(self.title) + """</h1>
                <h3 class='TitleFontPrint' style='color:darkgreen;'>""" + str(self.date) + """</h3>
                <br>
                <br>
                <br>
                </div>
                """
        self.html += self.banner_html

    def build_table_title(self):
        self.table_title_html = """
                <html lang='en'>
                <head>
                <meta charset='UTF-8'>
                <meta name='viewport' content='width=device-width, initial-scale=1' />
                <div class='HeaderStyle'>
                <h2 class='TitleFontPrint' style='color:darkgreen;'>""" + str(self.table_title) + """</h2>
                """
        self.html += self.table_title_html

    # right now from data frame
    def build_table(self):
        self.dataframe_html = self.dataframe.to_html(index=False)  # have the index be able to be passed in.
        self.html += self.dataframe_html

    def build_custom(self):
        self.html += self.custom_html

    def build_objective(self):
        self.obj_html = """
                    <!-- Test Objective -->
                    <h3 align='left'>""" + str(self.obj_title) + """</h3> 
                    <p align='left' width='900'>""" + str(self.objective) + """</p>
                    """
        self.html += self.obj_html

    def build_graph_title(self):
        self.table_graph_html = """
                <html lang='en'>
                <head>
                <meta charset='UTF-8'>
                <meta name='viewport' content='width=device-width, initial-scale=1' />
                <div class='HeaderStyle'>
                <h2 class='TitleFontPrint' style='color:darkgreen;'>""" + str(self.graph_title) + """</h2>
                """
        self.html += self.table_graph_html

    def build_graph(self):
        self.graph_html_obj = """
              <img align='center' style='padding:15;margin:5;width:1000px;' src=""" + "%s" % (self.graph_image) + """ border='1' />
            <br><br>
            """
        self.html +=self.graph_html_obj





# Unit Test
if __name__ == "__main__":

    # Testing: generate data frame 
    dataframe = pd.DataFrame({
    'product':['CT521a-264-1ac-1n','CT521a-1ac-1ax','CT522-264-1ac2-1n','CT523c-2ac2-db-10g-cu','CT523c-3ac2-db-10g-cu','CT523c-8ax-ac10g-cu','CT523c-192-2ac2-1ac-10g'],
    'radios':[1,1,2,2,6,9,3],
    'MIMO':['N','N','N','Y','Y','Y','Y'],
    'stations':[200,64,200,128,384,72,192],
    'mbps':[300,300,300,10000,10000,10000,10000]
    })

    print(dataframe)

    # Testing: generate data frame 
    dataframe2 = pd.DataFrame({
     'station':[1,2,3,4,5,6,7],
     'time_seconds':[23,78,22,19,45,22,25]
    })


    #report = lf_report(_dataframe=dataframe)
    report = lf_report()
    report.set_title("Banner Title One")
    report.build_banner()
    #report.set_title("Banner Title Two")
    #report.build_banner()

    report.set_table_title("Title One")
    report.build_table_title()

    report.set_dataframe(dataframe)
    report.build_table()

    report.set_table_title("Title Two")
    report.build_table_title()

    report.set_dataframe(dataframe2)
    report.build_table()

    #report.build_all()

    html_file = report.write_html() 
    print("returned file ")
    print(html_file)
    report.write_pdf()
