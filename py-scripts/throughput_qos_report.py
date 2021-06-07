'''
------------------------------------------------------------------------------------
Throughput QOS report evaluates the throughput for a number of clients which are running
traffic with a particular type of service Video | Voice | BE | BK
------------------------------------------------------------------------------------
'''
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import pdfkit
from lf_report import lf_report
from lf_graph import lf_bar_graph


def table(report, title, data):
    # creating table
    report.set_table_title(title)
    report.build_table_title()
    report.set_table_dataframe(data)
    report.build_table()


def grph(report, data_set=None, xaxis_name="stations", yaxis_name="Throughput 2 (Mbps)",
         xaxis_categories=None, label=None, graph_image_name=""):
    # creating bar graph
    report.set_graph_title(graph_image_name)
    report.build_graph_title()
    graph = lf_bar_graph(_data_set=data_set,
                         _xaxis_name=xaxis_name,
                         _yaxis_name=yaxis_name,
                         _xaxis_categories=xaxis_categories,
                         _graph_image_name=graph_image_name,
                         _label=label,
                         _color=None,
                         _color_edge='red')
    graph_png = graph.build_bar_graph()
    print("graph name {}".format(graph_png))
    report.set_graph_image(graph_png)
    report.move_graph_image()
    report.build_graph()


def generate_report(util, sta_num, bps_rx_a, bps_rx_b, tbl_title, grp_title, upload=1000000, download=1000000):
    # report generation main function
    rx_a = []
    rx_b = []
    pas_fail_up = []
    pas_fail_down = []
    thrp_b = upload * len(sta_num)  # get overall upload values
    thrp_a = download * len(sta_num)  ## get overall download values
    print(f"given upload--{thrp_b} and download--{thrp_a} values")
    index = -1
    for a in bps_rx_a:
        index += 1
        if len(a):
            rx_a.append(f'min: {min(a)} | max: {max(a)} | avg: {sum(a) / len(a)}')
            if thrp_a:
                print(
                    f"getting overall download values '{index}'----- {sum(a)} \n {(thrp_a / 100) * (100 - int(util[index]))}")
                if (thrp_a / 100) * (100 - int(util[index])) <= sum(a):
                    pas_fail_down.append("PASS")
                else:
                    pas_fail_down.append("FAIL")
        else:
            pas_fail_down.append("NA")
            rx_a.append(0)

        if len(bps_rx_b[index]):
            rx_b.append(f'min: {min(bps_rx_b[index])} | max: {max(bps_rx_b[index])} | '
                        f'avg: {(sum(bps_rx_b[index]) / len(bps_rx_b[index])):.2f}')

            if thrp_b:
                print(
                    f"getting overall upload values '{index}'----- {sum(bps_rx_b[index])} \n {(thrp_b / 100) * (100 - int(util[index]))}")
                if (thrp_b / 100) * (100 - int(util[index])) <= sum(bps_rx_b[index]):
                    pas_fail_up.append("PASS")
                else:
                    pas_fail_up.append("FAIL")
        else:
            pas_fail_up.append("NA")
            rx_b.append(0)

        util[index] = f'{util[index]}%'  # append % to the util values

    overall_tab = pd.DataFrame({
        'Channel Utilization (%)': util, "No.of.clients": [len(sta_num)] * len(util),
        'Speed (mbps)': [f'upload: {upload} | download: {download}'] * len(util),
        'Upload (mbps)': rx_b, 'Download (mbps)': rx_a
    })
    print(f"overall table \n{overall_tab}")

    pasfail_tab = pd.DataFrame({
        'Channel Utilization (%)': util,
        'Upload': pas_fail_up,
        'Download': pas_fail_down
    })
    print(f"pass-fail table \n {pasfail_tab}")

    report = lf_report()
    report_path = report.get_path()
    report_path_date_time = report.get_path_date_time()
    print("path: {}".format(report_path))
    print("path_date_time: {}".format(report_path_date_time))
    report.set_title(tbl_title)
    report.build_banner()

    # objective title and description
    report.set_obj_html(_obj_title="Objective",
                        _obj="Through this test we can evaluate the throughput for given number of clients which"
                             "are running the traffic with a particular TOS i.e BK,BE,VI,VO")
    report.build_objective()

    table(report, "Overall throughput", overall_tab)
    table(report, "Throughput Pass/Fail", pasfail_tab)

    if download:
        grph(report,
             data_set=[[min(i) for i in bps_rx_a], [max(i) for i in bps_rx_a], [sum(i) / len(i) for i in bps_rx_a]],
             xaxis_name="Load", yaxis_name="Throughput (Mbps)",
             xaxis_categories=util, label=["min", "max", 'avg'], graph_image_name="Throughput_download")
    if upload:
        grph(report,
             data_set=[[min(i) for i in bps_rx_b], [max(i) for i in bps_rx_b], [sum(i) / len(i) for i in bps_rx_b]],
             xaxis_name="Load", yaxis_name="Throughput (Mbps)",
             xaxis_categories=util, label=["min", "max", 'avg'], graph_image_name="Throughput_upload")

    for i in range(len(util)):
        if download:
            grph(report, data_set=[bps_rx_a[i]], xaxis_name="stations",
                 yaxis_name="Throughput (Mbps)", xaxis_categories=range(0, len(sta_num)),
                 label=[util[i]], graph_image_name=f"client-Throughput-download_{i}")
        if upload:
            grph(report, data_set=[bps_rx_b[i]], xaxis_name="stations",
                 yaxis_name="Throughput (Mbps)", xaxis_categories=range(0, len(sta_num)),
                 label=[util[i]], graph_image_name=f"client-Throughput-upload_{i}")

    html_file = report.write_html()
    print("returned file {}".format(html_file))
    report.write_pdf()

    # report.generate_report()
