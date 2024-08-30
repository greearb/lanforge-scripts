#!/usr/bin/python3

import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import requests
import importlib
import sys
import os
import logging
import argparse

try:
    import Pmw
except BaseException:
    print("Pmw module needed, Please do: pip install Pmw ")
    exit(1)


if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

lf_rig_tab = importlib.import_module("lf_create_rig_tab")
lf_radio_frame = importlib.import_module("lf_create_radio_frame")
lf_dut_tab = importlib.import_module("lf_create_dut_tab")
lf_wc_tab = importlib.import_module("lf_create_wc_tab")
lf_dp_rvr_tab = importlib.import_module("lf_create_dp_rvr_tab")
lf_create_wc_json = importlib.import_module("lf_create_wc_json")
lf_create_ap_auto_json = importlib.import_module("lf_create_ap_auto_json")
lf_create_dp_rvr_json = importlib.import_module("lf_create_dp_rvr_json")

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


# TODO make the GUI into mulitple files using the widgets
# possibly do for the next iteration
# https://stackoverflow.com/questions/43208723/how-do-i-split-up-python-tkinter-code-in-multiple-files
# https://stackoverflow.com/questions/66470340/how-to-work-on-tkinter-code-and-split-in-multiple-files
class json_gen_gui():

    def __init__(self,
                 radio_count=8):

        self.radio_count = radio_count

        self.window = tkinter.Tk()  # window is equivalent to root , pass around window
        self.window.title("LANforge Test Json Generator")

        self.window_tooltip = Pmw.Balloon(self.window)

        # tool tip
        # https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
        # https://stackoverflow.com/questions/63681382/how-to-add-hover-feature-for-text-description-on-a-tkinter-button
        # tool tips
        Pmw.initialise(self.window)

        self.current_working_directory = os.getcwd()

        self.max_radios = self.radio_count

        # create the either pack, place, grid
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()

        self.tabControl = ttk.Notebook(self.frame)
        self.rig_tab = ttk.Frame(self.tabControl)
        self.dut_tab = ttk.Frame(self.tabControl)
        self.wc_tab = ttk.Frame(self.tabControl)
        self.dp_rvr_tab = ttk.Frame(self.tabControl)
        self.ap_auto_tab = ttk.Frame(self.tabControl)
        self.functional_tab = ttk.Frame(self.tabControl)
        self.practice_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.rig_tab, text='LANforge')
        self.tabControl.add(self.dut_tab, text='Device Under Test')
        self.tabControl.add(self.wc_tab, text='Wifi Capacity')
        self.tabControl.add(self.dp_rvr_tab, text='Data Plane , RvR')
        # self.tabControl.add(self.ap_auto_tab, text = 'AP Auto')
        # self.tabControl.add(self.functional_tab, text = 'Functional Tests')

        # self.tabControl.add(self.practice_tab, text = 'Practice') # Please Do not Delete.
        self.tabControl.pack(expand=1, fill="both")

        self.file_2g = ""
        self.file_5g = ""
        self.file_6g = ""

        # -----------------------------------------------------------------------------------
        #  Create Rig Json
        # ------------------------------------------------------------------------------------
        self.lf_rig_frame = lf_rig_tab.lf_create_rig_tab(self.rig_tab, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #  Create DUT json
        # ------------------------------------------------------------------------------------
        self.lf_dut_tab = lf_dut_tab.lf_create_dut_tab(self.dut_tab, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #  Create Radios
        # ------------------------------------------------------------------------------------
        self.lf_radio_frame = lf_radio_frame.lf_create_radio_frame(self.rig_tab, self.lf_rig_frame, self.max_radios, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #  Create Wifi Capacity
        # ------------------------------------------------------------------------------------
        lf_wc_tab.lf_create_wc_tab(self.wc_tab, self.lf_dut_tab, self.lf_radio_frame, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #  Create Data Plane or RvR
        # ------------------------------------------------------------------------------------
        lf_dp_rvr_tab.lf_create_dp_rvr_tab(self.dp_rvr_tab, self.lf_dut_tab, self.lf_radio_frame, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #
        #  Create AP Auto Tests
        #
        # ------------------------------------------------------------------------------------
        self.lf_ap_auto_tab_frame = tkinter.Frame(self.ap_auto_tab)
        self.lf_ap_auto_tab_frame.pack()

        # lanforge Information for json
        self.lf_ap_auto_frame = tkinter.LabelFrame(self.lf_ap_auto_tab_frame, text="AP Auto - Under development")
        self.lf_ap_auto_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)

        self.lf_ap_auto_2g_file = tkinter.Label(self.lf_ap_auto_frame, text='2g json file')
        self.lf_ap_auto_2g_file.grid(row=1, column=0)
        self.lf_ap_auto_2g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_2g_file_entry_var.set("")
        self.lf_ap_auto_2g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_2g_file_entry_var, width=48)
        self.lf_ap_auto_2g_file_entry.grid(row=1, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_2g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_5g_file = tkinter.Label(self.lf_ap_auto_frame, text='5g json file')
        self.lf_ap_auto_5g_file.grid(row=2, column=0)
        self.lf_ap_auto_5g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_5g_file_entry_var.set("")
        self.lf_ap_auto_5g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_5g_file_entry_var, width=48)
        self.lf_ap_auto_5g_file_entry.grid(row=2, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_5g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_6g_file = tkinter.Label(self.lf_ap_auto_frame, text='6g json file')
        self.lf_ap_auto_6g_file.grid(row=3, column=0)
        self.lf_ap_auto_6g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_6g_file_entry_var.set("")
        self.lf_ap_auto_6g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_6g_file_entry_var, width=48)
        self.lf_ap_auto_6g_file_entry.grid(row=3, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_6g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_duration = tkinter.Label(self.lf_ap_auto_frame, text='test duration (ms)')
        self.lf_ap_auto_duration.grid(row=4, column=0)
        self.lf_ap_auto_duration_combobox = ttk.Combobox(self.lf_ap_auto_frame, values=["<Custom>", "5000 (5 sec)", "10000 (10 sec)", "15000 (15 sec)", "20000 (20 sec)", "30000 (30 sec)", "60000 (1 min)", "300000 (5min)"])
        self.lf_ap_auto_duration_combobox.current(3)
        self.lf_ap_auto_duration_combobox.grid(row=4, column=1)
        self.window_tooltip.bind(self.lf_ap_auto_duration_combobox, '''Select the duration of each iteration  ''')

        # Column 0
        self.lf_ap_auto_basic_client_connectivity_var = tkinter.StringVar(value="Use")
        self.lf_ap_auto_basic_client_connectivity_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Basic Client Connectivity", variable=self.lf_ap_auto_basic_client_connectivity_var,
                                                                              onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_basic_client_connectivity_check.grid(row=5, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_basic_client_connectivity_check, '''Basic Client Connectivity Estimatede duration: 12 minutes.
Creates stations, associates them, and measures connection time.
Supports mulitple loops''')

        self.lf_ap_auto_multi_band_performance_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_multi_band_performance_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Multi Band Performance", variable=self.lf_ap_auto_multi_band_performance_var,
                                                                           onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_multi_band_performance_check.grid(row=6, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_multi_band_performance_check, '''Multi Band Performance Estimated duration: 4 minutes.
Single_station throughput test each band, using single-band
rates found in the Throughput test as offered load.
Supports multiple loops''')

        self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_multi_station_throughput_vs_pkt_size_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Stability", variable=self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var,
                                                                                         onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_multi_station_throughput_vs_pkt_size_check.grid(row=7, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_multi_station_throughput_vs_pkt_size_check, '''Multi-Station Throughput vs Pkt Size Estimated duration: 50 minutes * number-of-stations-counts minutes.
Hunt to find best throughput at different frame sizes and different numbers of stations.
Supports multiple loops''')

        self.lf_ap_auto_stability_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_stability_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Multi-Station Throughput vs Pkt Size", variable=self.lf_ap_auto_stability_var,
                                                              onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_stability_check.grid(row=8, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_stability_check, '''Stability Bring up stations, run VOIP, emulated video, and slow-speed UDP traffic.
Reset stations if so configured.
Check station connection stability and throughput hangs''')

        self.lf_ap_auto_channel_switching_test_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_channel_switching_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Channel Switching Test", variable=self.lf_ap_auto_channel_switching_test_var,
                                                                      onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_channel_switching_check.grid(row=9, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_channel_switching_check, '''Channel Switching Test''')

        # column 2
        self.lf_ap_auto_throughput_vs_pkt_size_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_throughput_vs_pkt_size_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Throughtput vs Pkt Size", variable=self.lf_ap_auto_throughput_vs_pkt_size_var,
                                                                           onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_throughput_vs_pkt_size_check.grid(row=6, column=1, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_throughput_vs_pkt_size_check, '''Throughput vs Pkt Size Estimated duration: 49 minutes.
Hunt to find best throughput at different frame sizes using a single station.
Supports multiple loops''')

        self.lf_ap_auto_capacity_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_capacity_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Capacity", variable=self.lf_ap_auto_capacity_var,
                                                             onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_capacity_check.grid(row=7, column=1)
        self.window_tooltip.bind(self.lf_ap_auto_capacity_check, '''Capacity Estimated duration: 27 minutes.
Throughput with different numbers of stations, and optionally,
different /1/b/g/n/AC modes, NSS, and packet sizes.
Supports mulitple loops''')

        self.lf_ap_auto_band_steering_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_band_steering_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Band-Steering", variable=self.lf_ap_auto_band_steering_var,
                                                                  onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_band_steering_check.grid(row=8, column=1)
        self.window_tooltip.bind(self.lf_ap_auto_band_steering_check, '''Band-Steering Estimated duration: 10 minutes.
Test weather AP will direct stations to lesser utilized channel.
Requires that SSID are same for all DUT radios
and that BSSIDs are configured properly in the DUT''')

        self.lf_ap_auto_long_term_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_long_term_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Stability", variable=self.lf_ap_auto_long_term_var,
                                                              onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_long_term_check.grid(row=9, column=1)
        self.window_tooltip.bind(self.lf_ap_auto_long_term_check, '''Long-Term Estimated duration: depends on configured duration.
Bring up stations and start traffic, let ststem run in  this configuration for sppecified amount of time.
Does NOT support multiple loops''')

        # row 10
        self.lf_ap_auto_use_qa_var = tkinter.StringVar(value="Use")
        self.lf_ap_auto_use_qa_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="lf_qa (report)", variable=self.lf_ap_auto_use_qa_var,
                                                           onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_use_qa_check.grid(row=10, column=0)
        self.window_tooltip.bind(self.lf_ap_auto_use_qa_check, '''Recommended: AP Auto Test Suite Json will include lf_qa.
lf_qa will compare performance over multiple runs for Chamber View tests and tests that include kpi''')

        self.lf_ap_auto_use_inspect_var = tkinter.StringVar(value="Use")
        self.lf_ap_auto_use_inspect_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="lf_inspect (report)", variable=self.lf_ap_auto_use_inspect_var,
                                                                onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_use_inspect_check.grid(row=10, column=1)
        self.window_tooltip.bind(self.lf_ap_auto_use_inspect_check, '''Recommended: AP Auto Test Suite Json will include lf_inspect.
lf_inspect will compare performance between two individual runs for Chamber View tests and tests that include kpi''')

        self.lf_ap_auto_save = ttk.Button(self.lf_ap_auto_frame, text='Create AP Auto Test Suite Json', command=self.create_ap_auto_json)
        self.lf_ap_auto_save.grid(row=11, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_ap_auto_save, 'Save Wifi Capacity Json File')

        self.lf_ap_auto_clear = ttk.Button(self.lf_ap_auto_frame, text='Clear AP Auto Info', command=self.ap_auto_clear_information)
        self.lf_ap_auto_clear.grid(row=11, column=1, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_ap_auto_clear, 'Clear AP Auto Information, use between test suite generation')

        # Max Stations
        for widget in self.lf_ap_auto_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # -----------------------------------------------------------------------------------
        #
        #  End AP Auto Tests
        #
        # ------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------
        #
        #  Create Functional Tests
        #
        # ------------------------------------------------------------------------------------
        self.lf_functional_tab_frame = tkinter.Frame(self.functional_tab)
        self.lf_functional_tab_frame.pack()

        # create then either pack, place, grid
        self.test_l3_frame = tkinter.Frame(self.lf_functional_tab_frame)
        self.test_l3_frame.pack()

        # lanforge Radio Information
        self.lf_test_l3_frame = tkinter.LabelFrame(self.test_l3_frame, text="Radio Information")
        self.lf_test_l3_frame.grid(row=1, column=0, sticky="news", padx=20, pady=10)

        # -----------------------------------------------------------------------------------
        #
        #  End Functional Tests
        #
        # ------------------------------------------------------------------------------------

        # ------------------------------------------------------------------------------------
        #
        #  Menu Bar
        #
        # ------------------------------------------------------------------------------------

        self.menubar = tkinter.Menu(self.window)

        self.filemenu = tkinter.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Close", command=self.on_closing)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Close without Question", command=exit)

        self.actionmenu = tkinter.Menu(self.menubar, tearoff=0)
        self.actionmenu.add_command(label="Show Message", command=self.show_message)

        self.menubar.add_cascade(menu=self.filemenu, label="File")
        self.menubar.add_cascade(menu=self.actionmenu, label="Action")

        self.window.config(menu=self.menubar)

        # -------------------------------------------------------------------------------------
        #
        # Pratice Tab Begin
        #
        # -------------------------------------------------------------------------------------

        self.label = tkinter.Label(self.practice_tab, text="Your Message", font=('Arial', 18))
        self.label.pack(padx=10, pady=10)

        self.textbox = tkinter.Text(self.practice_tab, font=('Arial', 16))
        self.textbox.bind("<KeyPress>", self.short_cut)
        self.textbox.pack(padx=10, pady=10)

        self.check_state = tkinter.IntVar()

        self.check = tkinter.Checkbutton(self.practice_tab, text="Show Messagebox", font=('Arial', 16), variable=self.check_state)
        self.check.pack(padx=10, pady=10)

        self.button = tkinter.Button(self.practice_tab, text="Show Meassage", font=('Arial', 18), command=self.show_message)
        self.button.pack(padx=10, pady=10)

        self.clearbtn = tkinter.Button(self.practice_tab, text="Clear", font=('Arial', 18), command=self.clear)
        self.clearbtn.pack(padx=10, pady=10)

        # -------------------------------------------------------------------------------------
        #
        # Practice Tab End
        #
        # -------------------------------------------------------------------------------------

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def show_message(self):
        if self.check_state.get() == 0:
            print(self.textbox.get('1.0', tkinter.END))
        else:
            messagebox.showinfo(title="Message", message=self.textbox.get('1.0', tkinter.END))

    def short_cut(self, event):
        if event.state == 20 and event.keysym == "Return":
            self.show_message()

    def on_closing(self):
        if messagebox.askyesno(title="Quit?", message="Do you really want to quit?"):
            self.window.destroy()

    def clear(self):
        self.textbox.delete('1.0', tkinter.END)

    def ap_auto_clear_information(self):
        self.lf_ap_auto_2g_file_entry_var.set("")
        self.lf_ap_auto_5g_file_entry_var.set("")
        self.lf_ap_auto_6g_file_entry_var.set("")
        self.lf_ap_auto_duration_combobox.set("")

    def create_ap_auto_json(self):
        # use the auto generated name
        self.ap_auto_clear_information()
        self.lf_ap_auto_2g_file_entry_var.get()
        self.lf_ap_auto_5g_file_entry_var.get()
        self.lf_ap_auto_6g_file_entry_var.get()
        ap_auto_duration = self.lf_ap_auto_duration_combobox.get()
        if ap_auto_duration == "":
            self.lf_ap_auto_duration_combobox.set("20000")

        self.lf_ap_auto_basic_client_connectivity_var.get()
        self.lf_ap_auto_multi_band_performance_var.get()
        self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var.get()
        self.lf_ap_auto_stability_var.get()
        self.lf_ap_auto_channel_switching_test_var.get()
        self.lf_ap_auto_throughput_vs_pkt_size_var.get()
        self.lf_ap_auto_capacity_var.get()
        self.lf_ap_auto_band_steering_var.get()
        self.lf_ap_auto_long_term_var.get()

        self.lf_ap_auto_use_qa_var.get()
        self.lf_ap_auto_use_inspect_var.get()

        dictionary_length = len(self.radio_dict)
        logger.debug("radio_dict length = {length}".format(length=dictionary_length))
        ap_auto_json = lf_create_ap_auto_json.lf_create_ap_auto_json(
            _file_2g=self.lf_ap_auto_2g_file_entry_var.get(),
            _file_5g=self.lf_ap_auto_5g_file_entry_var.get(),
            _file_6g=self.lf_ap_auto_6g_file_entry_var.get(),
            _ap_auto_duration=self.lf_ap_auto_duration_combobox.get(),
            _use_radio_dict=self.use_radio_var_dict,
            _radio_dict=self.radio_dict,
            _radio_type_dict=self.radio_type_dict,
            _radio_max_sta_dict=self.radio_max_sta_dict,
            _use_radio_var_dict=self.use_radio_var_dict,
            _use_radio_2g_var_dict=self.use_radio_2g_var_dict,
            _use_radio_5g_var_dict=self.use_radio_5g_var_dict,
            _use_radio_6g_var_dict=self.use_radio_6g_var_dict,
            _suite_radios_2g=self.suite_radios_2g,
            _suite_radios_5g=self.suite_radios_5g,
            _suite_radios_6g=self.suite_radios_6g,
            _suite_test_name_2g_dict=self.suite_test_name_2g_dict,
            _suite_test_name_5g_dict=self.suite_test_name_5g_dict,
            _suite_test_name_6g_dict=self.suite_test_name_6g_dict,
            _radio_count=self.radio_count,
            _radio_batch_dict=self.radio_batch_dict,
            _lf_ap_auto_basic_client_connectivity=self.lf_ap_auto_basic_client_connectivity_var,
            _lf_ap_auto_multi_band_performance=self.lf_ap_auto_multi_band_performance_var,
            _lf_ap_auto_multi_station_throughput_vs_pkt_size=self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var,
            _lf_ap_auto_stability=self.lf_ap_auto_stability_var,
            _lf_ap_auto_channel_switching_test=self.lf_ap_auto_channel_switching_test_var,
            _lf_ap_auto_throughput_vs_pkt_size=self.lf_ap_auto_throughput_vs_pkt_size_var,
            _lf_ap_auto_capacity=self.lf_ap_auto_capacity_var,
            _lf_ap_auto_band_steering=self.lf_ap_auto_band_steering_var,
            _lf_ap_auto_long_term=self.lf_ap_auto_long_term_var,
            _lf_ap_auto_use_qa_var=self.lf_ap_auto_use_qa_var,
            _lf_ap_auto_use_inspect_var=self.lf_ap_auto_use_inspect_var
        )

        if self.suite_radios_2g != "":
            ap_auto_json.test_suite_band = "2g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_2g_file_entry_var.set(ap_auto_json.get_file_2g())
        if self.suite_radios_5g != "":
            ap_auto_json.test_suite_band = "5g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_5g_file_entry_var.set(ap_auto_json.get_file_5g())
        if self.suite_radios_6g != "":
            ap_auto_json.test_suite_band = "6g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_6g_file_entry_var.set(ap_auto_json.get_file_6g())

        if self.suite_radios_2g == "" and self.suite_radios_5g == "" and self.suite_radios_6g == "":
            tkinter.messagebox.showinfo(title="message", message="Please Read or Select LANforge Radios on LANforge tab")
        else:
            tkinter.messagebox.showinfo(title="success", message="created \n" + self.lf_ap_auto_2g_file_entry_var.get() + "\n" + self.lf_ap_auto_5g_file_entry_var.get() + "\n" + self.lf_ap_auto_6g_file_entry.get())


def main():

    parser = argparse.ArgumentParser(
        prog='lf_check_json_gen.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        lf_check_json_gen.py is a tkinter GUI that can create rig, dut and test json used as an input to lf_check.py

            ''',
        description='''\
NAME: lf_check_json_gen.py

PURPOSE:
     This script is a tkinter GUI that can create rig, dut and test json used as an input to lf_check.py

EXAMPLE:
    ./lf_check_json_gen.py --radio_count 12



SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:


STATUS: Pre ALPHA , Rig json, DUT json, and Wifi Capacity, Dataplane, RvR test json supported

VERIFIED_ON:

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2024 Candela Technologies Inc

INCLUDE_IN_README: False
''')
    parser.add_argument('--radio_count', help='Number of radios to display on GUI', default='16')

    args = parser.parse_args()
    _radio_count = args.radio_count

    my_gui = json_gen_gui(radio_count=int(_radio_count))
    # TODO allow log level to be sets
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level='debug')


if __name__ == '__main__':
    main()
