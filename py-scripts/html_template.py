""" this is generic report format for DFSS Test
 rum - python3 html_template.py"""

from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import os.path
from os import path
import pdfkit


# dev complete
def report_banner(date):
    banner_data = """
                   <!DOCTYPE html>
                    <html lang='en'>
                    <head>
                    <meta charset='UTF-8'>
                    <meta name='viewport' content='width=device-width, initial-scale=1' />
                    <title>DFS Testing Report</title>                        

                    </head>


                    <body>
                    <div class='Section report_banner-1000x205' style='background-image:url("/home/lanforge/LANforgeGUI_5.4.3/images/report_banner-1000x205.jpg");background-repeat:no-repeat;padding:0;margin:0;min-width:1000px; min-height:205px;width:1000px; height:205px;max-width:1000px; max-height:205px;'>
                    <br>
                    <img align='right' style='padding:25;margin:5;width:200px;' src="/home/lanforge/LANforgeGUI_5.4.3/images/CandelaLogo2-90dpi-200x90-trans.png" border='0' />


                    <div class='HeaderStyle'>
                    <br>
                    <h1 class='TitleFontPrint' style='color:darkgreen;'>  Dynamic Frequency Selection  </h1>
                    <h3 class='TitleFontPrint' style='color:darkgreen;'>""" + date + """</h3>
                    </div>
                    </div>

                    <br><br>

                 """
    return str(banner_data)


# dev complete
def test_objective(
        objective="The DFS Test is designed to test the Performance of the Netgear Access Point.Dynamic frequency selection is a technology that is designed to ensure that wireless devices operating in the unlicensed WLAN 5 GHz bands are able to detect when they may be interfering with military and weather radar systems and automatically switch over to another frequency where they will not cause any disturbance. "):
    test_objective = """
                    <!-- Test Objective -->
                    <h3 align='left'>Objective</h3> 
                    <p align='left' width='900'>""" + str(objective) + """</p>
                    <br>
                    """
    return str(test_objective)


# dev complete
def test_setup_information(ap_name="", ssid="", num_client=1):
    setup_information = """
                        <!-- Test Setup Information -->
                        <table width='700px' border='1' cellpadding='2' cellspacing='0' style='border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px'>
                            <tr>
                              <th colspan='2'>Test Setup Information</th>
                            </tr>
                            <tr>
                              <td>Device Under Test</td>
                              <td>
                                <table width='100%' border='0' cellpadding='2' cellspacing='0' style='border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px'>
                                  <tr>
                                    <td>AP Name</td>
                                    <td colspan='3'>""" + ap_name + """</td>
                                  </tr>
                                  <tr>
                                    <td>SSID</td>
                                    <td colspan='3'>""" + ssid + """</td>
                                  </tr>
                                  <tr>
                                    <td>Number of Clients</td>
                                    <td colspan='3'>""" + num_client + """</td>
                                  </tr>
                                </table>
                              </td>
                            </tr>
                        </table>

                        <br>
                        """
    return str(setup_information)


# yet to test on dev level
def graph_html(graph_path=""):
    graph_html_obj = """
    <!-- Detection Time Graph -->
    <h3>Detection Time Graph</h3> 
      <img align='center' style='padding:15;margin:5;width:1000px;' src=""" + graph_path + """ border='1' />
    <br><br>
    """
    return str(graph_html_obj)


def bar_plot(ax, data, colors=None, total_width=0.8, single_width=1, legend=True):
    # Check if colors where provided, otherwhise use the default color cycle
    if colors is None:
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    # Number of bars per group
    n_bars = len(data)

    # The width of a single bar
    bar_width = total_width / n_bars

    # List containing handles for the drawn bars, used for the legend
    bars = []

    # Iterate over all data
    for i, (name, values) in enumerate(data.items()):
        # The offset in x direction of that bar
        x_offset = (i - n_bars / 2) * bar_width + bar_width / 2
        # print(values)

        # Draw a bar for every value of that type
        for x, y in enumerate(values):
            bar = ax.bar(x + x_offset, y, width=bar_width * single_width, color=colors[i % len(colors)])
        # Add a handle to the last drawn bar, which we'll need for the legend
        bars.append(bar[0])

    # Draw legend if we need
    if legend:
        ax.legend(bars, data.keys(), bbox_to_anchor=(1.1, 1.05))

    ax.set_ylabel('Time in seconds')
    ax.set_xlabel('Channels')
    # ax.set_xticks(1)
    channels = [52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140]
    idx = np.asarray([i for i in range(len(channels))])
    ax.set_xticks(idx)

    ax.set_xticklabels(
        ('52', '56', '60', '64', '100', '104', '108', '112', '116', '120', '124', '128', '132', '136', '140'))


def generate_graph(result_data, graph_path):
    detection_data = {
        "FCC0": result_data['FCC0']['detection_time_lst'],
        "FCC1": result_data['FCC1']['detection_time_lst'],
        "FCC2": result_data['FCC2']['detection_time_lst'],
        "FCC3": result_data['FCC3']['detection_time_lst'],
        "FCC4": result_data['FCC4']['detection_time_lst'],
        "FCC5": result_data['FCC5']['detection_time_lst'],
        "ETSI1": result_data['ETSI1']['detection_time_lst'],
        "ETSI2": result_data['ETSI2']['detection_time_lst'],
        "ETSI3": result_data['ETSI3']['detection_time_lst'],
        "ETSI4": result_data['ETSI4']['detection_time_lst'],
        "ETSI5": result_data['ETSI5']['detection_time_lst'],
        "ETSI6": result_data['ETSI6']['detection_time_lst']
    }

    fig, ax = plt.subplots()
    bar_plot(ax, detection_data, total_width=.8, single_width=1.2)

    my_dpi = 96
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(18, 6)

    # when saving, specify the DPI
    str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
    plt.savefig(graph_path + "/image.png", dpi=my_dpi)
    return str(graph_html(graph_path + "/image.png"))


# yet to test on dev level
def add_radar_table(result_data):
    radar_html_struct = dict.fromkeys(list(result_data.keys()))
    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["radar_lst"]
        final_data = ""
        for i in fcc_type:
            if i == "YES":
                final_data = final_data + "<td colspan='1' bgcolor='#90EE90'>YES</td>"

            else:
                final_data = final_data + "<td colspan='1' bgcolor='orange'>NO</td>"
        radar_html_struct[fcc] = final_data

    radar_html = """
                <!--  Radar Detected Table -->
                <table width='1000px' border='1' cellpadding='2' cellspacing='0' >
                  <tr>
                    <th colspan='2'>Radar Detected </th>
                  </tr>
                  <table width='1000px' border='1' >
                    <tr>
                      <th>

                      </th>
                      <th>52</th>
                      <th>56</th>
                      <th>60</th>
                      <th>64</th>
                      <th>100</th>
                      <th>104</th>
                      <th>108</th>
                      <th>112</th>
                      <th>116</th>
                      <th>120</th>
                      <th>124</th>
                      <th>128</th>
                      <th>132</th>
                      <th>136</th>
                      <th>140</th>
                    </tr>
                    <tr>
                      <td>FCC0</td>
                      <!-- Add Variable Here -->
                      """ + radar_html_struct["FCC0"] + """
                    <tr>
                      <td>FCC1</td>
                      """ + radar_html_struct["FCC1"] + """
                    </tr>
                      <td>FCC2</td>
                      """ + radar_html_struct["FCC2"] + """
                    </tr>
                    <tr>
                      <td>FCC3</td>
                      """ + radar_html_struct["FCC3"] + """
                    </tr>
                    <tr>
                      <td>FCC4</td>
                      """ + radar_html_struct["FCC4"] + """
                    </tr>
                    <tr>
                      <td>FCC5</td>
                      """ + radar_html_struct["FCC5"] + """
                    </tr>
                    <tr>
                      <td>ETSI1</td>
                      """ + radar_html_struct["ETSI1"] + """
                    </tr>
                    <tr>
                      <td>ETSI2</td>
                      """ + radar_html_struct["ETSI2"] + """
                    </tr>
                    <tr>
                      <td>ETSI3</td>
                      """ + radar_html_struct["ETSI3"] + """
                    </tr>
                    <tr>
                      <td>ETSI4</td>
                      """ + radar_html_struct["ETSI4"] + """
                    </tr>
                    <tr>
                      <td>ETSI5</td>
                      """ + radar_html_struct["ETSI5"] + """
                    </tr>
                    <tr>
                      <td>ETSI6</td>
                      """ + radar_html_struct["ETSI6"] + """
                    </tr>
                  </table>
                </table>
                <br><br><br><br><br><br><br>
                """
    return str(radar_html)


# yet to test on dev level
def add_client_cx_table(result_data):
    client_html_struct = dict.fromkeys(list(result_data.keys()))
    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["connection_time_lst"]
        final_data = ""
        for i in fcc_type:
            final_data = final_data + "<td colspan='1'>" + str(i) + "</td>"

        client_html_struct[fcc] = final_data

    client_cx_html = """
                     <!--  Client Connection Time -->
                    <table width='1000px' border='1' cellpadding='2' cellspacing='0' >
                      <tr>
                        <th colspan='2'>Client Connection Time (sec)</th>
                      </tr>
                      <table width='1000px' border='1' >
                        <tr>
                        <th>

                      </th>
                      <th>52</th>
                      <th>56</th>
                      <th>60</th>
                      <th>64</th>
                      <th>100</th>
                      <th>104</th>
                      <th>108</th>
                      <th>112</th>
                      <th>116</th>
                      <th>120</th>
                      <th>124</th>
                      <th>128</th>
                      <th>132</th>
                      <th>136</th>
                      <th>140</th>
                    </tr>
                    <tr>
                      <td>FCC0</td>
                      <!-- Add Variable Here -->
                      """ + client_html_struct["FCC0"] + """
                    <tr>
                      <td>FCC1</td>
                      """ + client_html_struct["FCC1"] + """
                    </tr>
                      <td>FCC2</td>
                      """ + client_html_struct["FCC2"] + """
                    </tr>
                    <tr>
                      <td>FCC3</td>
                      """ + client_html_struct["FCC3"] + """
                    </tr>
                    <tr>
                      <td>FCC4</td>
                      """ + client_html_struct["FCC4"] + """
                    </tr>
                    <tr>
                      <td>FCC5</td>
                      """ + client_html_struct["FCC5"] + """
                    </tr>
                    <tr>
                      <td>ETSI1</td>
                      """ + client_html_struct["ETSI1"] + """
                    </tr>
                    <tr>
                      <td>ETSI2</td>
                      """ + client_html_struct["ETSI2"] + """
                    </tr>
                    <tr>
                      <td>ETSI3</td>
                      """ + client_html_struct["ETSI3"] + """
                    </tr>
                    <tr>
                      <td>ETSI4</td>
                      """ + client_html_struct["ETSI4"] + """
                    </tr>
                    <tr>
                      <td>ETSI5</td>
                      """ + client_html_struct["ETSI5"] + """
                    </tr>
                    <tr>
                      <td>ETSI6</td>
                      """ + client_html_struct["ETSI6"] + """
                    </tr>
                  </table>
                </table>
                <br><br>
                     """
    return str(client_cx_html)


# yet to test on dev level
def add_detection_table(result_data):
    detection_html_struct = dict.fromkeys(list(result_data.keys()))
    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["detection_time_lst"]
        final_data = ""
        for i in fcc_type:
            final_data = final_data + "<td colspan='1'>" + str(i) + " </td>"

        detection_html_struct[fcc] = final_data

    detection_html = """
                    <!--  Detection Time -->
                    <table width='1000px' border='1' cellpadding='2' cellspacing='0' >
                      <tr>
                        <th colspan='2'>Detection Time (sec)</th>
                      </tr>
                      <table width='1000px' border='1' >
                        <tr>
                        <th>

                      </th>
                      <th>52</th>
                      <th>56</th>
                      <th>60</th>
                      <th>64</th>
                      <th>100</th>
                      <th>104</th>
                      <th>108</th>
                      <th>112</th>
                      <th>116</th>
                      <th>120</th>
                      <th>124</th>
                      <th>128</th>
                      <th>132</th>
                      <th>136</th>
                      <th>140</th>
                    </tr>
                    <tr>
                      <td>FCC0</td>
                      <!-- Add Variable Here -->
                      """ + detection_html_struct["FCC0"] + """
                    <tr>
                      <td>FCC1</td>
                      """ + detection_html_struct["FCC1"] + """
                    </tr>
                      <td>FCC2</td>
                      """ + detection_html_struct["FCC2"] + """
                    </tr>
                    <tr>
                      <td>FCC3</td>
                      """ + detection_html_struct["FCC3"] + """
                    </tr>
                    <tr>
                      <td>FCC4</td>
                      """ + detection_html_struct["FCC4"] + """
                    </tr>
                    <tr>
                      <td>FCC5</td>
                      """ + detection_html_struct["FCC5"] + """
                    </tr>
                    <tr>
                      <td>ETSI1</td>
                      """ + detection_html_struct["ETSI1"] + """
                    </tr>
                    <tr>
                      <td>ETSI2</td>
                      """ + detection_html_struct["ETSI2"] + """
                    </tr>
                    <tr>
                      <td>ETSI3</td>
                      """ + detection_html_struct["ETSI3"] + """
                    </tr>
                    <tr>
                      <td>ETSI4</td>
                      """ + detection_html_struct["ETSI4"] + """
                    </tr>
                    <tr>
                      <td>ETSI5</td>
                      """ + detection_html_struct["ETSI5"] + """
                    </tr>
                    <tr>
                      <td>ETSI6</td>
                      """ + detection_html_struct["ETSI6"] + """
                    </tr>
                  </table>
                </table>
                <br><br>
                    """
    return detection_html


# yet to test on dev level
def add_switched_channel_table(result_data):
    switched_html_struct = dict.fromkeys(list(result_data.keys()))
    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["switched_ch_lst"]
        final_data = ""
        for i in fcc_type:
            final_data = final_data + "<td colspan='1'>" + i + "</td>"

        switched_html_struct[fcc] = final_data
    switched_data = """
                    <!--  Switched Channel -->
                    <table width='1000px' border='1' cellpadding='2' cellspacing='0' >
                      <tr>
                        <th colspan='2'>Switched Channel</th>
                      </tr>
                      <table width='1000px' border='1' >
                        <tr>
                        <th>

                      </th>
                      <th>52</th>
                      <th>56</th>
                      <th>60</th>
                      <th>64</th>
                      <th>100</th>
                      <th>104</th>
                      <th>108</th>
                      <th>112</th>
                      <th>116</th>
                      <th>120</th>
                      <th>124</th>
                      <th>128</th>
                      <th>132</th>
                      <th>136</th>
                      <th>140</th>
                    </tr>
                    <tr>
                      <td>FCC0</td>
                      <!-- Add Variable Here -->
                      """ + switched_html_struct["FCC0"] + """
                    <tr>
                      <td>FCC1</td>
                      """ + switched_html_struct["FCC1"] + """
                    </tr>
                      <td>FCC2</td>
                      """ + switched_html_struct["FCC2"] + """
                    </tr>
                    <tr>
                      <td>FCC3</td>
                      """ + switched_html_struct["FCC3"] + """
                    </tr>
                    <tr>
                      <td>FCC4</td>
                      """ + switched_html_struct["FCC4"] + """
                    </tr>
                    <tr>
                      <td>FCC5</td>
                      """ + switched_html_struct["FCC5"] + """
                    </tr>
                    <tr>
                      <td>ETSI1</td>
                      """ + switched_html_struct["ETSI1"] + """
                    </tr>
                    <tr>
                      <td>ETSI2</td>
                      """ + switched_html_struct["ETSI2"] + """
                    </tr>
                    <tr>
                      <td>ETSI3</td>
                      """ + switched_html_struct["ETSI3"] + """
                    </tr>
                    <tr>
                      <td>ETSI4</td>
                      """ + switched_html_struct["ETSI4"] + """
                    </tr>
                    <tr>
                      <td>ETSI5</td>
                      """ + switched_html_struct["ETSI5"] + """
                    </tr>
                    <tr>
                      <td>ETSI6</td>
                      """ + switched_html_struct["ETSI6"] + """
                    </tr>
                  </table>
                </table>
                <br><br>
                    """

    return switched_data


def generate_report(result_data=None,
                    date=None,
                    ap_name="testap",
                    ssid="lexusdut",
                    num_client="1",
                    graph_path="/home/lanforge/html-reports/dfs"):
    date = str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
    """result_data = {'FCC0': {'switched_ch_lst': ['64', '140', '124', '108', '108', '108', '112', '40', '40', '120', '124', '128', '140', '136', '140'], 'detection_time_lst': [4, 5, 4, 5, 0, 4, 4, 4, 4, 0, 0, 0, 5, 0, 0], 'radar_lst': ['YES', 'YES', 'YES', 'YES', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO', 'NO', 'YES', 'NO', 'NO'],
                            'connection_time_lst': [73, 75, 614, 66, 0, 65, 74, 0, 0, 0, 0, 0, 66, 0, 0]},
                   'FCC1': {'switched_ch_lst': ['108', '132', '116', '120', '120', '100', '136', '124', '60', '120', '124', '128', '136', '136', '140'], 'detection_time_lst': [4, 4, 4, 4, 0, 5, 4, 4, 4, 0, 0, 0, 4, 0, 0], 'radar_lst': ['YES', 'YES', 'YES', 'YES', 'NO', 'YES', 'YES', 'YES', 'YES', 'NO', 'NO', 'NO', 'YES', 'NO', 'NO'],
                            'connection_time_lst': [67, 65, 64, 613, 0, 73, 67, 623, 74, 0, 0, 0, 74, 0, 0]},
                   'FCC2': {'switched_ch_lst': ['52', '56', '60', '64', '64', '104', '108', '112', '116', '120', '124', '128', '132', '136', '140'], 'detection_time_lst': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'radar_lst': ['NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO', 'NO'],
                            'connection_time_lst': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
                   'FCC3': {'switched_ch_lst': ['140', '128', '140', '40', '40', '100', '136', '112', '36', '120', '124', '128', '124', '136', '140'], 'detection_time_lst': [5, 5, 4, 4, 0, 4, 4, 0, 4, 0, 0, 0, 5, 0, 0], 'radar_lst': ['YES', 'YES', 'YES', 'YES', 'NO', 'YES', 'YES', 'NO', 'YES', 'NO', 'NO', 'NO', 'YES', 'NO', 'NO'],
                            'connection_time_lst': [67, 615, 75, 0, 0, 67, 74, 0, 0, 0, 0, 0, 618, 0, 0]},
                   'FCC4': {'switched_ch_lst': [], 'detection_time_lst': [], 'radar_lst': [],
                            'connection_time_lst': []},
                   'FCC5': {'switched_ch_lst': [], 'detection_time_lst': [], 'radar_lst': [],
                            'connection_time_lst': []},
                   'ETSI1': {'switched_ch_lst': [], 'detection_time_lst': [], 'radar_lst': [],
                             'connection_time_lst': []},
                   'ETSI2': {'switched_ch_lst': [], 'detection_time_lst': [],
                             'radar_lst': [],
                             'connection_time_lst': []},
                   'ETSI3': {'switched_ch_lst': [], 'detection_time_lst': [], 'radar_lst': [],
                             'connection_time_lst': []},
                   'ETSI4': {'switched_ch_lst': [], 'detection_time_lst': [],
                             'radar_lst': [],
                             'connection_time_lst': []},
                   'ETSI5': {'switched_ch_lst': [], 'detection_time_lst': [],
                             'radar_lst': [],
                             'connection_time_lst': []},
                   'ETSI6': {'switched_ch_lst': [], 'detection_time_lst': [], 'radar_lst': [],
                             'connection_time_lst': []}}"""
    for i in result_data:
        print(i)
    reports_root = graph_path + "/" + date
    if path.exists(graph_path):
        os.mkdir(reports_root)
        print("Reports Root is Created")

    else:
        os.mkdir(graph_path)
        os.mkdir(reports_root)
        print("Reports Root is created")
    print("Generating Reports in : ", reports_root)
    html_report = \
        report_banner(date) + \
        test_objective() + \
        test_setup_information(ap_name, ssid, num_client) + \
        generate_graph(result_data, reports_root) + \
        add_radar_table(result_data) + \
        add_client_cx_table(result_data) + \
        add_detection_table(result_data) + \
        add_switched_channel_table(result_data)

    # print(html_report)

    # write the html_report into a file in /home/lanforge/html_reports in a directory named DFS_TEST and html_report name should be having a timesnap with it
    f = open(reports_root + "/report.html", "a")
    f.write(html_report)
    f.close()
    # write logic to generate pdf here
    pdfkit.from_file(reports_root + "/report.html", reports_root + "/report.pdf")


# test blocks from here
if __name__ == '__main__':
    generate_report()
    # generate_graph()









