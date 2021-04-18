#!/usr/bin/env python3

'''
NAME: lf_report.py

PURPOSE: 

This program is a helper  class for reporting results for a lanforge python script.
The class will generate an output directory based on date and time in the /home/lanforge/reports-data/ .   
If the reports-data is not present then the date and time directory will be created in the current directory.
The banner and Candela Technology logo will be copied in the results directory. 
The results directory may be over written and many of the other paramaters during construction. 
Creating the date time directory on construction was a design choice.

EXAMPLE: 

This is a helper class, a unit test is included at the bottom of the file.  
To test lf_report.py and lf_graph.py together use the lf_report_test.py file

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2021 Candela Technologies Inc

'''

import os
import shutil
import datetime
import pandas as pd
import pdfkit

# internal candela references included during intial phases, to be deleted at future date
# https://candelatech.atlassian.net/wiki/spaces/LANFORGE/pages/372703360/Scripting+Data+Collection+March+2021
# base report class
class lf_report():
    def __init__(self,
                #_path the report directory under which the report directories will be created.
                _path = "/home/lanforge/report-data",
                _alt_path = "",
                _output_format = 'html',  # pass in on the write functionality, current not used
                _dataframe="",
                _title="LANForge Test Run Heading",
                _table_title="LANForge Table Heading",
                _graph_title="LANForge Graph Title",
                _obj = "",
                _obj_title = "",
                _date="", 
                _output_html="outfile.html",
                _output_pdf="outfile.pdf",
                _path_date_time=""):  # this is where the final report is placed.
                #other report paths, 

            # _path is where the directory with the data time will be created
            if _path == "local" or _path == "here":
                self.path = os.path.abspath(__file__)
                print("path set to file path: {}".format(self.path))
            elif _alt_path != "":
                self.path = _alt_path
                print("path set to alt path: {}".format(self.path))
            else:
                self.path = _path
                print("path set: {}".format(self.path))
                
            self.dataframe=_dataframe
            self.title=_title
            self.table_title=_table_title
            self.graph_title=_graph_title
            self.date=_date
            self.output_html=_output_html
            self.path_date_time = _path_date_time
            self.write_output_html = ""
            self.output_pdf=_output_pdf
            self.write_output_pdf = ""
            self.banner_html = ""
            self.graph_titles=""
            self.graph_image=""
            self.html = ""
            self.custom_html = ""
            self.objective = _obj
            self.obj_title = _obj_title
            #self.systeminfopath = ""
            self.date_time_directory = ""
            self.banner_directory = "artifacts"
            self.banner_file_name = "banner.png"    # does this need to be configurable
            self.logo_directory = "artifacts"       
            self.logo_file_name = "CandelaLogo2-90dpi-200x90-trans.png"      # does this need to be configurable.
            self.current_path = os.path.dirname(os.path.abspath(__file__))

            # pass in _date to allow to change after construction
            self.set_date_time_directory(_date)
            self.build_date_time_directory()

            # move the banners and candela images to report path
            self.copy_banner()
            self.copy_logo()
    
    def copy_banner(self):
        banner_src_file = str(self.current_path)+'/'+str(self.banner_directory)+'/'+str(self.banner_file_name)
        banner_dst_file = str(self.path_date_time)+'/'+ str(self.banner_file_name)
        #print("banner src_file: {}".format(banner_src_file))
        #print("dst_file: {}".format(banner_dst_file))
        shutil.copy(banner_src_file,banner_dst_file)

    def copy_logo(self):
        logo_src_file = str(self.current_path)+'/'+str(self.logo_directory)+'/'+str(self.logo_file_name)
        logo_dst_file = str(self.path_date_time)+'/'+ str(self.logo_file_name)
        #print("logo_src_file: {}".format(logo_src_file))
        #print("logo_dst_file: {}".format(logo_dst_file))
        shutil.copy(logo_src_file,logo_dst_file)

    def move_graph_image(self,):
        graph_src_file = str(self.graph_image)
        graph_dst_file = str(self.path_date_time)+'/'+ str(self.graph_image)
        print("graph_src_file: {}".format(graph_src_file))
        print("graph_dst_file: {}".format(graph_dst_file))
        shutil.move(graph_src_file,graph_dst_file)


    def set_path(self,_path):
        self.path = _path
    
    def set_date_time_directory(self,_date):
        self.date = _date
        if self.date != "":
            self.date_time_directory = self.date
        else:
            self.date_time_directory = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-h-%M-m-%S-s")).replace(':','-')

    #def set_date_time_directory(self,date_time_directory):
    #    self.date_time_directory = date_time_directory


    def build_date_time_directory(self):
        if self.date_time_directory == "":
            self.set_date_time_directory()
        #try:
        self.path_date_time = os.path.join(self.path, self.date_time_directory)
        print("path_date_time {}".format(self.path_date_time))
        try:        
            if not os.path.exists(self.path_date_time):
                os.mkdir(self.path_date_time)
        except:
            self.path_date_time = os.path.join(self.current_path, self.date_time_directory)
            if not os.path.exists(self.path_date_time):
                os.mkdir(self.path_date_time)
        print("report path : {}".format(self.path_date_time))    

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

    def get_path(self):
        return self.path
    # get_path_date_time, get_report_path and need to be the same ()
    def get_path_date_time(self):
        return self.path_date_time

    def get_report_path(self):
        return self.path_date_time

    def write_html(self): 
        self.write_output_html = str(self.path_date_time)+'/'+ str(self.output_html)
        print("write_output_html: {}".format(self.write_output_html))
        try:
            test_file = open(self.write_output_html, "w")
            test_file.write(self.html)
            test_file.close()
        except:
            print("write_html failed")
        return self.write_output_html

    def write_pdf(self):
            # write logic to generate pdf here
            # wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
            # sudo apt install ./wkhtmltox_0.12.6-1.focal_amd64.deb
            
            options = {"enable-local-file-access" : None}  # prevent error Blocked access to file
            self.write_output_pdf = str(self.path_date_time)+'/'+ str(self.output_pdf)
            pdfkit.from_file(self.write_output_html, self.write_output_pdf, options=options)
            pass

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

    def build_date_time(self):
        self.date_time = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-h-%m-m-%S-s")).replace(':','-')
        return self.date_time

    def build_path_date_time(self):
        try: 
            self.path_date_time = os.path.join(self.path,self.date_time)
            os.mkdir(self.path_date_time)
        except:
            curr_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      
            self.path_date_time = os.path.join(curr_dir_path,self.date_time)
            os.mkdir(self.path_date_time)       

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

    report = lf_report()
    report.set_title("Banner Title One")
    report.build_banner()

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

    print("report path {}".format(report.get_path()))
