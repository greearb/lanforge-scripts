#!/usr/bin/env python3
"""
NAME: lf_graph.py

PURPOSE:
Common Library for generating graphs for LANforge output

SETUP:
/lanforge/html-reports directory needs to be present or output generated in local file

EXAMPLE:
see: /py-scritps/lf_report_test.py for example

COPYRIGHT:
    Copyright 2021 Candela Technologies Inc
    License: Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README
"""
import sys
import os
import importlib
import matplotlib.pyplot as plt
import numpy as np
import pdfkit
from matplotlib.colors import ListedColormap
import matplotlib.ticker as mticker
import argparse
import traceback
import logging


# TODO have scipy be part of the base install
try:
    from scipy import interpolate

except Exception as x:
    print("Info:  scipy package not installed, Needed for smoothing linear plots 'pip install scipy'  ")
    traceback.print_exception(Exception, x, x.__traceback__, chain=True)


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

lf_csv = importlib.import_module("py-scripts.lf_csv")
lf_csv = lf_csv.lf_csv

# internal candela references included during intial phases, to be deleted
# at future date

# graph reporting classes


class lf_bar_graph:
    def __init__(self, _data_set=None,
                 _xaxis_name="x-axis",
                 _yaxis_name="y-axis",
                 _xaxis_categories=None,
                 _xaxis_label=None,
                 _graph_title="",
                 _title_size=16,
                 _graph_image_name="image_name",
                 _label=None,
                 _color=None,
                 _bar_width=0.25,
                 _color_edge='grey',
                 _font_weight='bold',
                 _color_name=None,
                 _figsize=(10, 5),
                 _show_bar_value=False,
                 _xaxis_step=1,
                 _xticks_font=None,
                 _xaxis_value_location=0,
                 _text_font=None,
                 _text_rotation=None,
                 _grp_title="",
                 _legend_handles=None,
                 _legend_loc="best",
                 _legend_box=None,
                 _legend_ncol=1,
                 _legend_fontsize=None,
                 _dpi=96,
                 _enable_csv=False):

        if _data_set is None:
            _data_set = [[30.4, 55.3, 69.2, 37.1], [45.1, 67.2, 34.3, 22.4], [22.5, 45.6, 12.7, 34.8]]
        if _xaxis_categories is None:
            _xaxis_categories = [1, 2, 3, 4]
        if _xaxis_label is None:
            _xaxis_label = ["a", "b", "c", "d"]
        if _label is None:
            _label = ["bi-downlink", "bi-uplink", 'uplink']
        if _color_name is None:
            _color_name = ['lightcoral', 'darkgrey', 'r', 'g', 'b', 'y']
        self.data_set = _data_set
        self.xaxis_name = _xaxis_name
        self.yaxis_name = _yaxis_name
        self.xaxis_categories = _xaxis_categories
        self.xaxis_label = _xaxis_label
        self.title = _graph_title
        self.title_size = _title_size
        self.graph_image_name = _graph_image_name
        self.label = _label
        self.color = _color
        self.bar_width = _bar_width
        self.color_edge = _color_edge
        self.font_weight = _font_weight
        self.color_name = _color_name
        self.figsize = _figsize
        self.show_bar_value = _show_bar_value
        self.xaxis_step = _xaxis_step
        self.xticks_font = _xticks_font
        self._xaxis_value_location = _xaxis_value_location
        self.text_font = _text_font
        self.text_rotation = _text_rotation
        self.grp_title = _grp_title
        self.enable_csv = _enable_csv
        self.lf_csv = lf_csv()
        self.legend_handles = _legend_handles
        self.legend_loc = _legend_loc
        self.legend_box = _legend_box
        self.legend_ncol = _legend_ncol
        self.legend_fontsize = _legend_fontsize

    def build_bar_graph(self):
        if self.color is None:
            i = 0
            self.color = []
            for _ in self.data_set:
                self.color.append(self.color_name[i])
                i = i + 1

        plt.subplots(figsize=self.figsize)
        i = 0

        def show_value(rectangles):
            for rect in rectangles:
                h = rect.get_height()
                plt.text(rect.get_x() + rect.get_width() / 2., h, h,
                         ha='center', va='bottom', rotation=self.text_rotation, fontsize=self.text_font)

        for _ in self.data_set:
            if i > 0:
                br = br1
                br2 = [x + self.bar_width for x in br]
                rects = plt.bar(br2, self.data_set[i], color=self.color[i], width=self.bar_width,
                                edgecolor=self.color_edge, label=self.label[i])
                if self.show_bar_value:
                    show_value(rects)
                br1 = br2
                i = i + 1
            else:
                br1 = np.arange(len(self.data_set[i]))
                rects = plt.bar(br1, self.data_set[i], color=self.color[i], width=self.bar_width,
                                edgecolor=self.color_edge, label=self.label[i])
                if self.show_bar_value:
                    show_value(rects)
                i = i + 1
        plt.xlabel(self.xaxis_name, fontweight='bold', fontsize=15)
        plt.ylabel(self.yaxis_name, fontweight='bold', fontsize=15)
        if self.xaxis_categories[0] == 0:
            plt.xticks(np.arange(0,
                                 len(self.xaxis_categories),
                                 step=self.xaxis_step),
                       fontsize=self.xticks_font)
        else:
            plt.xticks([i + self._xaxis_value_location for i in np.arange(0, len(self.data_set[0]), step=self.xaxis_step)],
                       self.xaxis_categories, fontsize=self.xticks_font)
        plt.legend(
            handles=self.legend_handles,
            loc=self.legend_loc,
            bbox_to_anchor=self.legend_box,
            ncol=self.legend_ncol,
            fontsize=self.legend_fontsize)
        plt.suptitle(self.title, fontsize=self.title_size)
        plt.title(self.grp_title)
        plt.gcf()
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        plt.close()
        logger.debug("{}.png".format(self.graph_image_name))
        if self.enable_csv:
            if self.data_set is not None and self.xaxis_categories is not None:
                if len(self.xaxis_categories) == len(self.data_set[0]):
                    self.lf_csv.columns = []
                    self.lf_csv.rows = []
                    self.lf_csv.columns.append(self.xaxis_name)
                    self.lf_csv.columns.extend(self.label)
                    self.lf_csv.rows.append(self.xaxis_categories)
                    self.lf_csv.rows.extend(self.data_set)
                    self.lf_csv.filename = f"{self.graph_image_name}.csv"
                    self.lf_csv.generate_csv()
                else:
                    raise ValueError(
                        "Length and x-axis values and y-axis values should be same.")
            else:
                 logger.debug("No Dataset Found")
        logger.debug("{}.csv".format(self.graph_image_name))
        return "%s.png" % self.graph_image_name


class lf_scatter_graph:
    def __init__(self,
                 _x_data_set=None,
                 _y_data_set=None,
                 _values=None,
                 _xaxis_name="x-axis",
                 _yaxis_name="y-axis",
                 _label=None,
                 _graph_image_name="image_name1",
                 _color=None,
                 _figsize=(9, 4),
                 _enable_csv=True):
        if _x_data_set is None:
            _x_data_set = ["sta0 ", "sta1", "sta2", "sta3"]
        if _y_data_set is None:
            _y_data_set = [[30, 55, 69, 37]]
        if _label is None:
            _label = ["num1", "num2"]
        self.x_data_set = _x_data_set
        self.y_data_set = _y_data_set
        self.xaxis_name = _xaxis_name
        self.yaxis_name = _yaxis_name
        self.figsize = _figsize
        self.graph_image_name = _graph_image_name
        self.color = _color
        self.label = _label
        self.values = _values
        self.enable_csv = _enable_csv
        self.lf_csv = lf_csv()

    def build_scatter_graph(self):
        if self.color is None:
            self.color = [
                "orchid",
                "lime",
                "aquamarine",
                "royalblue",
                "darkgray",
                "maroon"]
        plt.subplots(figsize=self.figsize)
        if self.values is None:
            plt.scatter(
                self.x_data_set,
                self.y_data_set[0],
                color=self.color[0],
                label=self.label[0])
            if len(self.y_data_set) > 1:
                for i in range(1, len(self.y_data_set)):
                    plt.scatter(
                        self.x_data_set,
                        self.y_data_set[i],
                        color=self.color[i],
                        label=self.label[i])
            plt.xlabel(self.xaxis_name, fontweight='bold', fontsize=15)
            plt.ylabel(self.yaxis_name, fontweight='bold', fontsize=15)
            plt.gcf().autofmt_xdate()
            plt.legend()
        else:
            colours = ListedColormap(self.color)
            scatter = plt.scatter(
                self.x_data_set,
                self.y_data_set,
                c=self.values,
                cmap=colours)
            plt.xlabel(self.xaxis_name, fontweight='bold', fontsize=15)
            plt.ylabel(self.yaxis_name, fontweight='bold', fontsize=15)
            plt.gcf().autofmt_xdate()
            plt.legend(handles=scatter.legend_elements()[0], labels=self.label)
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        plt.close()
        logger.debug("{}.png".format(self.graph_image_name))
        if self.enable_csv:
            self.lf_csv.columns = self.label
            self.lf_csv.rows = self.y_data_set
            self.lf_csv.filename = f"{self.graph_image_name}.csv"
            self.lf_csv.generate_csv()

        return "%s.png" % self.graph_image_name

# have a second yaxis with line graph
class lf_bar_line_graph:
    def __init__(self, 
                 _data_set1=None,
                 # Note data_set2, data_set2_poly and data_set2_spline needs same size list
                 _data_set2=None,
                 _data_set2_poly=[False], # Values are True or False
                 _data_set2_poly_degree=[3],
                 _data_set2_interp1d=[False], # Values are True or False
                 _xaxis_name="x-axis",
                 _y1axis_name="y1-axis",
                 _y2axis_name="y2-axis",
                 _xaxis_categories=None,
                 _xaxis_label=None,
                 _graph_title="",
                 _title_size=16,
                 _graph_image_name="image_name",
                 _label1=None,
                 _label2=None,
                 _label2_poly=None,
                 _label2_interp1d=None,
                 _color1=None,
                 _color2=None,
                 _color2_poly=None,
                 _color2_interp1d=None,
                 _bar_width=0.25,
                 _color_edge='grey',
                 _font_weight='bold',
                 _color_name1=None,
                 _color_name2=None,
                 _marker=None,
                 _figsize=(10, 5),
                 _show_bar_value=False,
                 _xaxis_step=1,
                 _xticks_font=None,
                 _xaxis_value_location=0,
                 _text_font=None,
                 _text_rotation=None,
                 _grp_title="",
                 _legend_handles=None,
                 _legend_loc1="best",
                 _legend_loc2="best",
                 _legend_box1=None,
                 _legend_box2=None,
                 _legend_ncol=1,
                 _legend_fontsize=None,
                 _dpi=96,
                 _enable_csv=False):

        if _data_set1 is None:
            _data_set1 = [[30.4, 55.3, 69.2, 37.1], [45.1, 67.2, 34.3, 22.4], [22.5, 45.6, 12.7, 34.8]]
        if _xaxis_categories is None:
            _xaxis_categories = [1, 2, 3, 4]
        if _xaxis_label is None:
            _xaxis_label = ["a", "b", "c", "d"]
        if _label1 is None:
            _label1 = ["bi-downlink", "bi-uplink", 'uplink']
        if _label2 is None:
            _label2 = ["bi-downlink", "bi-uplink", 'uplink']

        if _color_name1 is None:
            _color_name1 = ['lightcoral', 'darkgrey', 'r', 'g', 'b', 'y']
        if _color_name2 is None:
            _color_name2 = ['lightcoral', 'darkgrey', 'r', 'g', 'b', 'y']
        self.data_set1 = _data_set1
        self.data_set2 = _data_set2
        self.data_set2_poly = _data_set2_poly
        self.data_set2_poly_degree = _data_set2_poly_degree
        self.data_set2_interp1d = _data_set2_interp1d
        self.xaxis_name = _xaxis_name
        self.y1axis_name = _y1axis_name
        self.y2axis_name = _y2axis_name
        self.xaxis_categories = _xaxis_categories
        self.xaxis_label = _xaxis_label
        self.title = _graph_title
        self.title_size = _title_size
        self.graph_image_name = _graph_image_name
        self.label1 = _label1
        self.label2 = _label2
        self.label2_poly = _label2_poly
        self.label2_interp1d = _label2_interp1d
        self.color1 = _color1
        self.color2 = _color2
        self.color2_poly = _color2_poly
        self.color2_interp1d = _color2_interp1d
        self.marker = _marker
        self.bar_width = _bar_width
        self.color_edge = _color_edge
        self.font_weight = _font_weight
        self.color_name1 = _color_name1
        self.color_name2 = _color_name2
        self.figsize = _figsize
        self.show_bar_value = _show_bar_value
        self.xaxis_step = _xaxis_step
        self.xticks_font = _xticks_font
        self._xaxis_value_location = _xaxis_value_location
        self.text_font = _text_font
        self.text_rotation = _text_rotation
        self.grp_title = _grp_title
        self.enable_csv = _enable_csv
        self.lf_csv = lf_csv()
        self.legend_handles = _legend_handles
        self.legend_loc1 = _legend_loc1
        self.legend_loc2 = _legend_loc2
        self.legend_box1 = _legend_box1
        self.legend_box2 = _legend_box2
        self.legend_ncol = _legend_ncol
        self.legend_fontsize = _legend_fontsize

    def build_bar_line_graph(self):
        if self.color1 is None:
            i = 0
            self.color1 = []
            for _ in self.data_set1:
                self.color1.append(self.color_name[i])
                i = i + 1

        fig, ax1 = plt.subplots(figsize=self.figsize)
        
        ax2 = ax1.twinx()

        i = 0

        def show_value(rectangles):
            for rect in rectangles:
                h = rect.get_height()
                ax1.text(rect.get_x() + rect.get_width() / 2., h, h,
                         ha='center', va='bottom', rotation=self.text_rotation, fontsize=self.text_font)

        for _ in self.data_set1:
            if i > 0:
                br = br1
                br2 = [x + self.bar_width for x in br]
                rects = ax1.bar(br2, self.data_set1[i], color=self.color1[i], width=self.bar_width,
                                edgecolor=self.color_edge, label=self.label1[i])
                if self.show_bar_value:
                    show_value(rects)
                br1 = br2
                i = i + 1
            else:
                br1 = np.arange(len(self.data_set1[i]))
                rects = ax1.bar(br1, self.data_set1[i], color=self.color1[i], width=self.bar_width,
                                edgecolor=self.color_edge, label=self.label1[i])
                if self.show_bar_value:
                    show_value(rects)
                i = i + 1
        ax1.set_xlabel(self.xaxis_name, fontweight='bold', fontsize=15)
        ax1.set_ylabel(self.y1axis_name, fontweight='bold', fontsize=15)
        if self.xaxis_categories[0] == 0:
            xsteps = plt.xticks(np.arange(0,
                                 len(self.xaxis_categories),
                                 step=self.xaxis_step),
                       fontsize=self.xticks_font)
        else:
            xsteps = plt.xticks([i + self._xaxis_value_location for i in np.arange(0, len(self.data_set1[0]), step=self.xaxis_step)],
                       self.xaxis_categories, fontsize=self.xticks_font)
        ax1.legend(
            handles=self.legend_handles,
            loc=self.legend_loc1,
            bbox_to_anchor=self.legend_box1,
            ncol=self.legend_ncol,
            fontsize=self.legend_fontsize)


        # overlay line graph
        def show_value2(data):
            for item, value in enumerate(data):
                ax2.text(item, value, "{value}".format(value=value), ha='center',rotation=self.text_rotation, fontsize=self.text_font)

        i = 0
        for _ in self.data_set2:
            br1 = np.arange(len(self.data_set2[i]))
            ax2.plot(
                br1,
                self.data_set2[i],
                color=self.color2[i],
                label=self.label2[i],
                marker=self.marker[i])
            show_value2(self.data_set2[i])
            # do polynomial smoothing
            if self.data_set2_poly[i]:
                poly = np.polyfit(br1,self.data_set2[i],self.data_set2_poly_degree[i])
                poly_y = np.poly1d(poly)(br1)
                ax2.plot(
                    br1,
                    poly_y,
                    color=self.color2_poly[i],
                    label=self.label2_poly[i]
                )
            if self.data_set2_interp1d[i]:
                cubic_interpolation_model = interpolate.interp1d(br1, self.data_set2[i],kind="cubic")

                x_sm = np.array(br1)
                x_smooth = np.linspace(x_sm.min(), x_sm.max(), 500)
                y_smooth = cubic_interpolation_model(x_smooth)
                ax2.plot(
                    x_smooth,
                    y_smooth,
                    color=self.color2_interp1d[i],
                    label=self.label2_interp1d[i]
                )

            i += 1
        ax2.set_xlabel(self.xaxis_name, fontweight='bold', fontsize=15)
        ax2.set_ylabel(self.y2axis_name, fontweight='bold', fontsize=15)
        ax2.tick_params(axis = 'y', labelcolor = 'orange')
            
        ax2.legend(
            handles=self.legend_handles,
            loc=self.legend_loc2,
            bbox_to_anchor=self.legend_box2,
            ncol=self.legend_ncol,
            fontsize=self.legend_fontsize)
        plt.suptitle(self.title, fontsize=self.title_size)
        plt.title(self.grp_title)
        plt.gcf()
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        plt.close()
        logger.debug("{}.png".format(self.graph_image_name))
        # TODO work though this for two axis
        if self.enable_csv:
            if self.data_set is not None and self.xaxis_categories is not None:
                if len(self.xaxis_categories) == len(self.data_set[0]):
                    self.lf_csv.columns = []
                    self.lf_csv.rows = []
                    self.lf_csv.columns.append(self.xaxis_name)
                    self.lf_csv.columns.extend(self.label)
                    self.lf_csv.rows.append(self.xaxis_categories)
                    self.lf_csv.rows.extend(self.data_set)
                    self.lf_csv.filename = f"{self.graph_image_name}.csv"
                    self.lf_csv.generate_csv()
                else:
                    raise ValueError(
                        "Length and x-axis values and y-axis values should be same.")
            else:
                 logger.debug("No Dataset Found")
        logger.debug("{}.csv".format(self.graph_image_name))
        return "%s.png" % self.graph_image_name



class lf_stacked_graph:
    """
    usage: This will generate a vertically stacked graph with list _data_set as well as with dictionary _data_set.

    example :

    For a graph with dictionary data_set

        obj = lf_stacked_graph(_data_set={'FCC0':0, 'FCC1':88.4,'FCC2':77.8,'FCC3':57.8,'FCC4':90.0,'FCC95':60.4,'FCC6':33.0},
                               _xaxis_name="", _yaxis_name="", _enable_csv=False, _remove_border=True)
        obj.build_stacked_graph()

    For a graph with list data_set

        obj = lf_stacked_graph(_data_set=[['FCC0', 'FCC1', 'FCC2', 'FCC3', 'FCC4', 'FCC95', 'FCC6'],
                                          [0, 88.4, 77.8, 57.8, 90.0, 60.4, 33.0],
                                          [100.0, 11.6, 22.2, 42.2, 10.0, 39.6, 67.0]])
        obj.build_stacked_graph()

    """
    def __init__(self,
                 _data_set=None,
                 _xaxis_name="Stations",
                 _yaxis_name="Numbers",
                 _label=None,
                 _graph_image_name="image_name2",
                 _color=None,
                 _figsize=(9, 4),
                 _enable_csv=True,
                 _width=0.79,
                 _bar_text_color='white',
                 _bar_font_weight='bold',
                 _bar_font_size=10,
                 _legend_title="Issues",
                 _legend_bbox=(1.13, 1.01),
                 _legend_loc="upper right",
                 _remove_border=False):
        if _data_set is None:
            _data_set = [[1, 2, 3, 4], [1, 1, 1, 1], [1, 1, 1, 1]]
        if _label is None:
            _label = ['Success', 'Fail']
        self.data_set = _data_set  # [x_axis,y1_axis,y2_axis]
        self.xaxis_name = _xaxis_name
        self.yaxis_name = _yaxis_name
        self.figsize = _figsize
        self.graph_image_name = _graph_image_name
        self.label = _label
        self.color = _color
        self.enable_csv = _enable_csv
        self.lf_csv = lf_csv()
        self.width = _width
        self.bar_text_color = _bar_text_color
        self.bar_font_weight = _bar_font_weight
        self.bar_font_size = _bar_font_size
        self.legend_title = _legend_title
        self.legend_bbox = _legend_bbox
        self.legend_loc = _legend_loc
        self.remove_border = _remove_border

    def build_stacked_graph(self):
        fig, axes_subplot = plt.subplots(figsize=self.figsize)
        if self.color is None:
            self.color = [
                "darkred",
                "tomato",
                "springgreen",
                "skyblue",
                "indigo",
                "plum"]
        if type(self.data_set) is list:
            plt.bar(self.data_set[0], self.data_set[1], color=self.color[0])
            plt.bar(
                self.data_set[0],
                self.data_set[2],
                bottom=self.data_set[1],
                color=self.color[1])
            if len(self.data_set) > 3:
                for i in range(3, len(self.data_set)):
                    plt.bar(self.data_set[0], self.data_set[i],
                            bottom=np.array(self.data_set[i - 2]) + np.array(self.data_set[i - 1]),color=self.color[i - 1])
            plt.legend(self.label)
        elif type(self.data_set) is dict:
            lable_values = []
            pass_values = []
            fail_values = []
            for i in self.data_set:
                lable_values.append(i)
            for j in self.data_set:
                pass_values.append(self.data_set[j])
                fail_values.append(round(float(100.0 - self.data_set[j]), 1))

            width = self.width
            figure_size, axes_subplot = plt.subplots(figsize=self.figsize)

            # building vertical bar plot
            bar_1 = plt.bar(lable_values, pass_values, width, color='green')
            bar_2 = plt.bar(lable_values, fail_values, width, bottom=pass_values, color='red')

            # inserting bar text
            for i, v in enumerate(pass_values):
                if v != 0:
                    plt.text(i + .005, v * 0.45, "%s%s" % (v, "%"), color=self.bar_text_color,
                             fontweight=self.bar_font_weight,
                             fontsize=self.bar_font_size, ha="center", va="center")
            for i, v in enumerate(fail_values):
                if v != 0:
                    plt.text(i + .005, v * 0.45 + pass_values[i], "%s%s" % (v, "%"), color=self.bar_text_color,
                             fontweight=self.bar_font_weight, fontsize=self.bar_font_size, ha="center", va="center")
            plt.legend([bar_1, bar_2], self.label, title=self.legend_title, bbox_to_anchor=self.legend_bbox,
                       loc=self.legend_loc)

        # to remove the borders
        if self.remove_border:
            for border in ['top', 'right', 'left', 'right', 'bottom']:
                axes_subplot.spines[border].set_visible(False)
                axes_subplot.yaxis.set_visible(False)

        plt.xlabel(self.xaxis_name)
        plt.ylabel(self.yaxis_name)
        plt.savefig("%s.png" % self.graph_image_name, bbox_inches="tight", dpi=96)
        plt.close()
        logger.debug("{}.png".format(self.graph_image_name))
        if self.enable_csv:
            self.lf_csv.columns = self.label
            self.lf_csv.rows = self.data_set
            self.lf_csv.filename = f"{self.graph_image_name}.csv"
            self.lf_csv.generate_csv()
        return "%s.png" % self.graph_image_name


class lf_horizontal_stacked_graph:
    def __init__(self,
                 _seg=2,
                 _yaxis_set=('A', 'B'),
                 _xaxis_set1=None,
                 _xaxis_set2=None,
                 _unit="%",
                 _xaxis_name="Stations",
                 _label=None,
                 _graph_image_name="image_name3",
                 _color=None,
                 _figsize=(9, 4),
                 _disable_xaxis=False,
                 _enable_csv=True):
        if _xaxis_set1 is None:
            _xaxis_set1 = [12, 0, 0, 16, 15]
        if _xaxis_set2 is None:
            _xaxis_set2 = [23, 34, 23, 0]
        if _label is None:
            _label = ['Success', 'Fail']
        if _color is None:
            _color = ["success", "Fail"]
        self.unit = _unit
        self.seg = _seg
        self.xaxis_set1 = _xaxis_set1
        self.xaxis_set2 = _xaxis_set2
        self.yaxis_set = _yaxis_set
        self.xaxis_name = _xaxis_name
        self.figsize = _figsize
        self.graph_image_name = _graph_image_name
        self.label = _label
        self.color = _color
        self.disable_xaxis = _disable_xaxis
        self.enable_csv = _enable_csv
        self.lf_csv = lf_csv()

    def build_horizontal_stacked_graph(self):
        def sumzip(items):
            return [sum(values) for values in zip(items)]

        fig, ax = plt.subplots(figsize=self.figsize)

        n = self.seg
        values1 = self.xaxis_set1
        values2 = self.xaxis_set2

        ind = np.arange(n) + .15
        width = 0.3

        plt.barh(
            ind,
            values1,
            width,
            color=self.color[0],
            label=self.label[0])
        plt.barh(
            ind,
            values2,
            width,
            left=sumzip(values1),
            color=self.color[1],
            label=self.label[1])

        extra_space = 0.15
        ax.set_yticks(ind + width - extra_space)
        ax.set_yticklabels(self.yaxis_set)
        ax.yaxis.set_tick_params(length=0, labelbottom=True)

        for i, v in enumerate(values1):
            if v != 0:
                plt.text(v * 0.45, i + .145, "%s%s" % (v, self.unit), color='white', fontweight='bold', fontsize=10,
                         ha='center', va='center')

        for i, v in enumerate(values2):
            if v != 0:
                plt.text(v * 0.45 + values1[i], i + .145, "%s%s" % (v, self.unit), color='white', fontweight='bold',
                         fontsize=10,
                         ha='center', va='center')

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.legend(loc='upper right')
        if self.disable_xaxis:
            plt.tick_params(
                axis='x',
                which='both',
                bottom=False,
                top=False,
                labelbottom=False)  # disable x-axis
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        plt.close()
        logger.debug("{}.png".format(self.graph_image_name))
        if self.enable_csv:
            self.lf_csv.columns = self.label
            self.lf_csv.rows = self.data_set
            self.lf_csv.filename = f"{self.graph_image_name}.csv"
            self.lf_csv.generate_csv()
        return "%s.png" % self.graph_image_name


class lf_line_graph:
    def __init__(self, _data_set=None,
                 _xaxis_name="x-axis",
                 _yaxis_name="y-axis",
                 _xaxis_categories=None,
                 _xaxis_label=None,
                 _graph_title="",
                 _title_size=16,
                 _graph_image_name="image_name",
                 _label=None,
                 _font_weight='bold',
                 _color=None,
                 _figsize=(10, 5),
                 _xaxis_step=5,
                 _xticks_font=None,
                 _text_font=None,
                 _legend_handles=None,
                 _legend_loc="best",
                 _legend_box=None,
                 _legend_ncol=1,
                 _legend_fontsize=None,
                 _marker=None,
                 _dpi=96,
                 _enable_csv=False,
                 _reverse_x=False,
                 _reverse_y=False):
        if _data_set is None:
            _data_set = [[30.4, 55.3, 69.2, 37.1], [45.1, 67.2, 34.3, 22.4], [22.5, 45.6, 12.7, 34.8]]
        if _xaxis_categories is None:
            _xaxis_categories = [1, 2, 3, 4, 5]
        if _xaxis_label is None:
            _xaxis_label = ["a", "b", "c", "d", "e"]
        if _label is None:
            _label = ["bi-downlink", "bi-uplink", 'uplink']
        if _color is None:
            _color = ['forestgreen', 'c', 'r', 'g', 'b', 'p']
        self.data_set = _data_set
        self.xaxis_name = _xaxis_name
        self.yaxis_name = _yaxis_name
        self.xaxis_categories = _xaxis_categories
        self.xaxis_label = _xaxis_label
        self.grp_title = _graph_title
        self.title_size = _title_size
        self.graph_image_name = _graph_image_name
        self.label = _label
        self.color = _color
        self.font_weight = _font_weight
        self.figsize = _figsize
        self.xaxis_step = _xaxis_step
        self.xticks_font = _xticks_font
        self.text_font = _text_font
        self.marker = _marker
        self.enable_csv = _enable_csv
        self.lf_csv = lf_csv()
        self.legend_handles = _legend_handles
        self.legend_loc = _legend_loc
        self.legend_box = _legend_box
        self.legend_ncol = _legend_ncol
        self.legend_fontsize = _legend_fontsize
        self.reverse_x = _reverse_x
        self.reverse_y = _reverse_y

    def build_line_graph(self):
        plt.subplots(figsize=self.figsize)
        i = 0
        for data in self.data_set:
            plt.plot(
                self.xaxis_categories,
                data,
                color=self.color[i],
                label=self.label[i],
                marker=self.marker)
            i += 1

        plt.xlabel(self.xaxis_name, fontweight='bold', fontsize=15)
        plt.ylabel(self.yaxis_name, fontweight='bold', fontsize=15)
        plt.legend(
            handles=self.legend_handles,
            loc=self.legend_loc,
            bbox_to_anchor=self.legend_box,
            ncol=self.legend_ncol,
            fontsize=self.legend_fontsize)
        plt.suptitle(self.grp_title, fontsize=self.title_size)
        if self.reverse_y:
            plt.gca().invert_yaxis()
        if self.reverse_x:
            plt.gca().invert_xaxis()            
        plt.gcf()
        plt.savefig("%s.png" % self.graph_image_name, dpi=96)
        plt.close()
        logger.debug("{}.png".format(self.graph_image_name))
        if self.enable_csv:
            if self.data_set is not None:
                self.lf_csv.columns = self.label
                self.lf_csv.rows = self.data_set
                self.lf_csv.filename = f"{self.graph_image_name}.csv"
                self.lf_csv.generate_csv()
            else:
                logger.debug("No Dataset Found")
        logger.debug("{}.csv".format(self.graph_image_name))
        return "%s.png" % self.graph_image_name


def main():
    # arguments
    parser = argparse.ArgumentParser(
        prog='lf_graph.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            lf_graph.py : unit test in lf_graph.py for exersizing the lf_graph.py library
            ''',
        description='''\
-----------------
NAME: lf_graph.py

PURPOSE:
Common Library for generating graphs for LANforge output

SETUP:
/lanforge/html-reports directory needs to be present or output generated in local file

EXAMPLE:
see: /py-scritps/lf_report_test.py for example

COPYWRITE
    Copyright 2021 Candela Technologies Inc
    License: Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README
---------------------
            ''')
    parser.add_argument(
        '--mgr',
        '--lfmgr',
        dest='lfmgr',
        help='sample argument: where LANforge GUI is running',
        default='localhost')
    # logging configuration
    parser.add_argument(
        '--debug',
        help='--debug this will enable debugging in py-json method',
        action='store_true')
    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger")

    # the args parser is not really used , this is so the report is not generated when testing
    # the imports with --help
    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    logger.debug("LANforge manager {lfmgr}".format(lfmgr=args.lfmgr))

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
    # prevent eerror Blocked access to file
    options = {"enable-local-file-access": None}
    pdfkit.from_file(output_html_1, output_pdf_1, options=options)

    # test build_bar_graph setting values
    dataset = [[45, 67, 34, 22], [22, 45, 12, 34], [30, 55, 69, 37]]
    x_axis_values = [1, 2, 3, 4]

    output_html_2 = "graph_2.html"
    output_pdf_2 = "graph_2.pdf"

    # test build_bar_graph with defaults
    graph = lf_bar_graph(_data_set=dataset,
                         _xaxis_name="stations",
                         _yaxis_name="Throughput 2 (Mbps)",
                         _xaxis_categories=x_axis_values,
                         _graph_image_name="Bi-single_radio_2.4GHz",
                         _label=["bi-downlink", "bi-uplink", 'uplink'],
                         _color=None,
                         _color_edge='red',
                         _enable_csv=True)
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
    # prevent eerror Blocked access to file
    options = {"enable-local-file-access": None}
    pdfkit.from_file(output_html_2, output_pdf_2, options=options)


# Unit Test
if __name__ == "__main__":
    main()
