#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import matplotlib as mpl 
import numpy as np 
import pandas as pd
import pdfkit
from report_library import report_library

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


    #report = report_library(_dataframe=dataframe)
    report = report_library()
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
