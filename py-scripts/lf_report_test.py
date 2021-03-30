#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import matplotlib as mpl 
import numpy as np 
import pandas as pd
import pdfkit
from lf_report import lf_report
from lf_graph import lf_bar_graph

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

    # test lf_graph in report
    dataset = [[45,67,34,22],[22,45,12,34],[30,55,69,37]]
    x_axis_values = [1,2,3,4]

    report.set_graph_title("Graph Title")
    report.build_graph_title()
    graph = lf_bar_graph(_data_set=dataset, 
                        _xaxis_name="stations", 
                        _yaxis_name="Throughput 2 (Mbps)", 
                        _xaxis_categories=x_axis_values,
                        _graph_image_name="Bi-single_radio_2.4GHz",
                        _label=["bi-downlink", "bi-uplink",'uplink'], 
                        _color=None,
                        _color_edge='red')


    graph_png = graph.build_bar_graph()

    print("graph name {}".format(graph_png))

    report.set_graph_image(graph_png)

    report.build_graph()

    #report.build_all()

    html_file = report.write_html() 
    print("returned file {}".format(html_file))
    print(html_file)
    report.write_pdf()

    report.generate_report()
