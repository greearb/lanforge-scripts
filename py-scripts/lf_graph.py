#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import matplotlib as mpl 
import numpy as np 
import pandas as pd
import pdfkit
import math

# internal candela references included during intial phases, to be deleted at future date

# graph reporting classes
class lf_bar_graph():
    def __init__(self,
                _data_set= [[30,55,69,37],[45,67,34,22],[22,45,12,34]],
                _xaxis_name="x-axis",
                _yaxis_name="y-axis",
                _xaxis_categories=[1,2,3,4],
                _graph_image_name="image_name",
                _label=["bi-downlink", "bi-uplink",'uplink'],
                _color=None,
                _bar_width=0.25,
                _color_edge='grey',
                _font_weight='bold',
                _color_name=['lightcoral','darkgrey','r','g','b','y'],
                _figsize=(10,5),
                _dpi=96):

        self.data_set=_data_set
        self.xaxis_name=_xaxis_name
        self.yaxis_name=_yaxis_name
        self.xaxis_categories=_xaxis_categories
        self.graph_image_name=_graph_image_name
        self.label=_label
        self.color=_color
        self.bar_width=_bar_width
        self.color_edge=_color_edge
        self.font_weight=_font_weight
        self.color_name=_color_name
        self.figsize=_figsize
        


    def build_bar_graph(self):
        if self.color is None:
            i = 0
            self.color = []
            for col in self.data_set:
                self.color.append(self.color_name[i])
                i = i+1

        fig = plt.subplots(figsize=self.figsize)
        i = 0
        for set in self.data_set:
            if i > 0:
                br = br1
                br2 = [x + self.bar_width for x in br]
                plt.bar(br2, self.data_set[i], color=self.color[i], width=self.bar_width,  
                        edgecolor=self.color_edge, label=self.label[i])
                br1 = br2
                i = i+1
            else:
                br1 = np.arange(len(self.data_set[i]))
                plt.bar(br1, self.data_set[i], color=self.color[i], width=self.bar_width,
                        edgecolor=self.color_edge, label=self.label[i])
                i=i+1
        plt.xlabel(self.xaxis_name, fontweight='bold', fontsize=15)
        plt.ylabel(self.yaxis_name, fontweight='bold', fontsize=15)
        plt.xticks([r + self.bar_width for r in range(len(self.data_set[0]))],
                   self.xaxis_categories)
        plt.legend()

        fig = plt.gcf()
        plt.savefig("%s.png"% (self.graph_image_name), dpi=96)
        print("{}.png".format(self.graph_image_name))

        return "%s.png" % (self.graph_image_name)



# Unit Test
if __name__ == "__main__":

    output_html_1 = "graph_1.html"
    output_pdf_1 = "graph_1.pdf"

    # test build_bar_graph with defaults
    graph = lf_bar_graph()
    graph_html_obj = """
        <img align='center' style='padding:15;margin:5;width:1000px;' src=""" + "%s" % (graph.build_bar_graph()) + """ border='1' />
        <br><br>
        """
    # 
    test_file = open(output_html_1, "w")
    test_file.write(graph_html_obj)
    test_file.close()

    # write to pdf
    # write logic to generate pdf here
    # wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
    # sudo apt install ./wkhtmltox_0.12.6-1.focal_amd64.deb
    options = {"enable-local-file-access" : None}  # prevent eerror Blocked access to file
    pdfkit.from_file(output_html_1, output_pdf_1, options=options)


    # test build_bar_graph setting values
    dataset = [[45,67,34,22],[22,45,12,34],[30,55,69,37]]
    x_axis_values = [1,2,3,4]

    output_html_2 = "graph_2.html"
    output_pdf_2 = "graph_2.pdf"

    # test build_bar_graph with defaults
    graph = lf_bar_graph(_data_set=dataset, 
                        _xaxis_name="stations", 
                        _yaxis_name="Throughput 2 (Mbps)", 
                        _xaxis_categories=x_axis_values,
                        _graph_image_name="Bi-single_radio_2.4GHz",
                        _label=["bi-downlink", "bi-uplink",'uplink'], 
                        _color=None,
                        _color_edge='red')
    graph_html_obj = """
        <img align='center' style='padding:15;margin:5;width:1000px;' src=""" + "%s" % (graph.build_bar_graph()) + """ border='1' />
        <br><br>
        """
    # 
    test_file = open(output_html_2, "w")
    test_file.write(graph_html_obj)
    test_file.close()

    # write to pdf
    # write logic to generate pdf here
    # wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
    # sudo apt install ./wkhtmltox_0.12.6-1.focal_amd64.deb
    options = {"enable-local-file-access" : None}  # prevent eerror Blocked access to file
    pdfkit.from_file(output_html_2, output_pdf_2, options=options)



