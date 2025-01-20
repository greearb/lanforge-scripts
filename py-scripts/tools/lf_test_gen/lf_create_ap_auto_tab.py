#!/usr/bin/env python3
# flake8: noqa
import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import importlib
import logging

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


lf_create_ap_auto_json = importlib.import_module("lf_create_ap_auto_json")


class lf_create_ap_auto_tab():
    def __init__(self, ap_auto_tab, dut_tab, radio_frame, window_tooltip, current_working_directory):
        self.ap_auto_tab = ap_auto_tab
        self.dut_tab = dut_tab
        self.radio_frame = radio_frame
        self.window_tooltip = window_tooltip
        self.current_working_directory = current_working_directory

        # -----------------------------------------------------------------------------------
        #
        #  Create AP Auto Capacity
        #
        # ------------------------------------------------------------------------------------

        self.lf_ap_auto_tab_frame = tkinter.Frame(self.ap_auto_tab)
        self.lf_ap_auto_tab_frame.pack()

        # file and directory
        self.lf_ap_auto_tab_frame = tkinter.Frame(self.ap_auto_tab)
        self.lf_ap_auto_tab_frame.pack()

        # lanforge Information for json
        self.lf_ap_auto_frame = tkinter.LabelFrame(self.lf_ap_auto_tab_frame, text="AP Auto")
        self.lf_ap_auto_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)

        self.lf_ap_auto_2g_file = tkinter.Label(self.lf_ap_auto_frame, text='2g json file')
        self.lf_ap_auto_2g_file.grid(row=1, column=0)
        self.lf_ap_auto_2g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_2g_file_entry_var.set("")
        self.lf_ap_auto_2g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_2g_file_entry_var, width=48)
        self.lf_ap_auto_2g_file_entry.grid(row=1, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_2g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_2g_dir = tkinter.Label(self.lf_ap_auto_frame, text='2g json dir')
        self.lf_ap_auto_2g_dir.grid(row=1, column=3)
        self.lf_ap_auto_2g_dir_entry_var = tkinter.StringVar()
        self.lf_ap_auto_2g_dir_entry_var.set("")
        self.lf_ap_auto_2g_dir_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_2g_dir_entry_var, width=48)
        self.lf_ap_auto_2g_dir_entry.grid(row=1, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_2g_dir_entry, '''Directory for AP Auto Test Suite, if blank will show dir created in''')

        self.lf_ap_auto_5g_file = tkinter.Label(self.lf_ap_auto_frame, text='5g json file')
        self.lf_ap_auto_5g_file.grid(row=2, column=0)
        self.lf_ap_auto_5g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_5g_file_entry_var.set("")
        self.lf_ap_auto_5g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_5g_file_entry_var, width=48)
        self.lf_ap_auto_5g_file_entry.grid(row=2, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_5g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_5g_dir = tkinter.Label(self.lf_ap_auto_frame, text='5g json dir')
        self.lf_ap_auto_5g_dir.grid(row=2, column=3)
        self.lf_ap_auto_5g_dir_entry_var = tkinter.StringVar()
        self.lf_ap_auto_5g_dir_entry_var.set("")
        self.lf_ap_auto_5g_dir_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_5g_dir_entry_var, width=48)
        self.lf_ap_auto_5g_dir_entry.grid(row=2, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_5g_dir_entry, '''Directory for AP Auto Test Suite, if blank will show dir created in''')

        self.lf_ap_auto_6g_file = tkinter.Label(self.lf_ap_auto_frame, text='6g json file')
        self.lf_ap_auto_6g_file.grid(row=3, column=0)
        self.lf_ap_auto_6g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_6g_file_entry_var.set("")
        self.lf_ap_auto_6g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_6g_file_entry_var, width=48)
        self.lf_ap_auto_6g_file_entry.grid(row=3, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_6g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_6g_dir = tkinter.Label(self.lf_ap_auto_frame, text='6g json dir')
        self.lf_ap_auto_6g_dir.grid(row=3, column=3)
        self.lf_ap_auto_6g_dir_entry_var = tkinter.StringVar()
        self.lf_ap_auto_6g_dir_entry_var.set("")
        self.lf_ap_auto_6g_dir_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable=self.lf_ap_auto_6g_dir_entry_var, width=48)
        self.lf_ap_auto_6g_dir_entry.grid(row=3, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_ap_auto_6g_file_entry, '''Directory for AP Auto Test Suite, if blank will show dir created in''')

        self.lf_ap_auto_duration = tkinter.Label(self.lf_ap_auto_frame, text='test duration (ms)')
        self.lf_ap_auto_duration.grid(row=4, column=0)
        self.lf_ap_auto_duration_combobox = ttk.Combobox(self.lf_ap_auto_frame, values=["<Custom>", "5000 (5 sec)", "10000 (10 sec)", "15000 (15 sec)", "20000 (20 sec)", "30000 (30 sec)", "60000 (1 min)", "300000 (5min)"])
        self.lf_ap_auto_duration_combobox.current(3)
        self.lf_ap_auto_duration_combobox.grid(row=4, column=1)
        self.window_tooltip.bind(self.lf_ap_auto_duration_combobox, '''Select the duration of each iteration  ''')

        # Column 0
        self.lf_ap_auto_basic_client_connectivity_var = tkinter.StringVar(value="Use")
        self.lf_ap_auto_basic_client_connectivity_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Basic Client Connectivity (basic_cx)", variable=self.lf_ap_auto_basic_client_connectivity_var,
                                                                              onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_basic_client_connectivity_check.grid(row=5, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_basic_client_connectivity_check, '''Basic Client Connectivity (basic_cx)
        Creates stations, associates them, and measures connection time.
        Supports multiple loops.
        Estimated duration: 12 minutes.
        Configuration key: basic_cx''')

        self.lf_ap_auto_band_steering_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_band_steering_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Band Steering (band_steering)", variable=self.lf_ap_auto_band_steering_var,
                                                                           onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_band_steering_check.grid(row=6, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_band_steering_check, '''Band Steering
        Test weather AP will direct stations to lesser utilized channel.
        Requires that SSID are the same for all DUT radios
        and that BSSIDs are configured properly in the DUT.
        Estimated duration: 10 minutes.
        Configuration key: band_steering''')

        self.lf_ap_auto_capacity_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_capacity_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Capacity (capacity)", variable=self.lf_ap_auto_capacity_var,
                                                             onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_capacity_check.grid(row=7, column=0)
        self.window_tooltip.bind(self.lf_ap_auto_capacity_check, '''Capacity
Throughput with different numbers of stations, and optionally,
different /a/b/g/n/AC modes, NSS, and packet sizes.
Supports mulitple loops
Estimated duration: 27 minutes.
Configuration key: capacity''')




        self.lf_ap_auto_channel_switching_test_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_channel_switching_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Channel Switching (channel_switch)", variable=self.lf_ap_auto_channel_switching_test_var,
                                                                      onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_channel_switching_check.grid(row=8, column=0, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_channel_switching_check, '''Channel Switching
Configuration key: channel_switch''')



        self.lf_ap_auto_long_term_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_long_term_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Long Term (long_term)", variable=self.lf_ap_auto_long_term_var,
                                                              onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_long_term_check.grid(row=9, column=0)
        self.window_tooltip.bind(self.lf_ap_auto_long_term_check, '''Long Term
Bring up stations and start traffic, let system run in this configuration
''')

        # column 2
        self.lf_ap_auto_stability_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_stability_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Stability (mix_stability)", variable=self.lf_ap_auto_stability_var,
                                                              onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_stability_check.grid(row=5, column=1, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_stability_check, '''Stability
Bring up stations, run VOIP, emulated video, and slow-speed UDP traffi.
Reset stationsif so configured.
Check station connection stability and throughput hangs.
Configurationkey: mix_stability
''')

        self.lf_ap_auto_throughput_vs_pkt_size_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_throughput_vs_pkt_size_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Single STA Throughtput vs Pkt Size (tput_single_sta)", variable=self.lf_ap_auto_throughput_vs_pkt_size_var,
                                                                           onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_throughput_vs_pkt_size_check.grid(row=6, column=1, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_throughput_vs_pkt_size_check, '''Single STA Throughput vs Pkt Size
Hunt to find best throughput at different frames sizes using a single station.
Supports multiple loops.
Estimbated duration: 49 minutes.
Configuration key: tput_single_sta''')

        self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var = tkinter.StringVar(value="Do Not Use")
        self.lf_ap_auto_multi_station_throughput_vs_pkt_size_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Multi STA Throughput vs Pkt Size (tput_multi_sta)", variable=self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var,
                                                                                         onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_multi_station_throughput_vs_pkt_size_check.grid(row=7, column=1, sticky="news")
        self.window_tooltip.bind(self.lf_ap_auto_multi_station_throughput_vs_pkt_size_check, '''Multi STA Throughput vs Pkt Size
Throughput vs Pkt Size Estimated duration: 50 minutes * number-of-stations-counts minutes.
Hunt to find best throughput at different frame sizes and different numbers of stations.
Supports multiple loops''')



#        self.lf_ap_auto_band_steering_var = tkinter.StringVar(value="Do Not Use")
#        self.lf_ap_auto_band_steering_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="Band-Steering", variable=self.lf_ap_auto_band_steering_var,
#                                                                  onvalue="Use", offvalue="Do Not Use")
#        self.lf_ap_auto_band_steering_check.grid(row=8, column=1)
#        self.window_tooltip.bind(self.lf_ap_auto_band_steering_check, '''Band-Steering Estimated duration: 10 minutes.
#Test weather AP will direct stations to lesser utilized channel.
#Requires that SSID are same for all DUT radios
#and that BSSIDs are configured properly in the DUT''')

        # row 11
        self.lf_ap_auto_use_qa_var = tkinter.StringVar(value="Use")
        self.lf_ap_auto_use_qa_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="lf_qa (report)", variable=self.lf_ap_auto_use_qa_var,
                                                           onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_use_qa_check.grid(row=11, column=0)
        self.window_tooltip.bind(self.lf_ap_auto_use_qa_check, '''Recommended: AP Auto Test Suite Json will include lf_qa.
lf_qa will compare performance over multiple runs for Chamber View tests and tests that include kpi''')

        self.lf_ap_auto_use_inspect_var = tkinter.StringVar(value="Use")
        self.lf_ap_auto_use_inspect_check = tkinter.Checkbutton(self.lf_ap_auto_frame, text="lf_inspect (report)", variable=self.lf_ap_auto_use_inspect_var,
                                                                onvalue="Use", offvalue="Do Not Use")
        self.lf_ap_auto_use_inspect_check.grid(row=11, column=1)
        self.window_tooltip.bind(self.lf_ap_auto_use_inspect_check, '''Recommended: AP Auto Test Suite Json will include lf_inspect.
lf_inspect will compare performance between two individual runs for Chamber View tests and tests that include kpi''')

        # row 12
        self.lf_ap_auto_save = ttk.Button(self.lf_ap_auto_frame, text='Create AP Auto Test Suite Json', command=self.create_ap_auto_json)
        self.lf_ap_auto_save.grid(row=12, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_ap_auto_save, 'Save Wifi Capacity Json File')

        self.lf_ap_auto_clear = ttk.Button(self.lf_ap_auto_frame, text='Clear AP Auto Info', command=self.ap_auto_clear_information)
        self.lf_ap_auto_clear.grid(row=12, column=1, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_ap_auto_clear, 'Clear AP Auto Information, use between test suite generation')

        self.lf_ap_auto_number_dut_indexes = tkinter.Label(self.lf_ap_auto_frame, text="Number DUT Indexes")
        self.lf_ap_auto_number_dut_indexes.grid(row=4, column=2)
        self.lf_ap_auto_number_dut_indexes_combobox = ttk.Combobox(self.lf_ap_auto_frame, values=["1", "2", "3", "4"])
        self.lf_ap_auto_number_dut_indexes_combobox.current(2)
        self.lf_ap_auto_number_dut_indexes_combobox.grid(row=4, column=3)
        self.window_tooltip.bind(self.lf_ap_auto_number_dut_indexes_combobox, '''Number of DUT indexes valid in the DUT json''')

        # Max Stations
        for widget in self.lf_ap_auto_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # -----------------------------------------------------------------------------------
        #
        #  End AP Auto Tests
        #
        # ------------------------------------------------------------------------------------

    def ap_auto_clear_information(self):
        self.lf_ap_auto_2g_file_entry_var.set("")
        self.lf_ap_auto_5g_file_entry_var.set("")
        self.lf_ap_auto_6g_file_entry_var.set("")
        self.lf_ap_auto_2g_dir_entry_var.set("")
        self.lf_ap_auto_5g_dir_entry_var.set("")
        self.lf_ap_auto_6g_dir_entry_var.set("")

    def create_ap_auto_json(self):
        # use the auto generated name
        # self.ap_auto_clear_information()

        ap_auto_duration = self.lf_ap_auto_duration_combobox.get()
        if ap_auto_duration == "":
            self.lf_ap_auto_duration_combobox.set("20000")

        self.lf_ap_auto_use_qa_var.get()
        self.lf_ap_auto_use_inspect_var.get()

        self.dut_tab.lf_radio_2g_combobox.get()
        self.dut_tab.lf_radio_5g_combobox.get()
        self.dut_tab.lf_radio_6g_combobox.get()

        self.lf_ap_auto_number_dut_indexes_combobox.get()

        dictionary_length = len(self.radio_frame.radio_dict)
        logger.debug("radio_dict length = {length}".format(length=dictionary_length))
        ap_auto_json = lf_create_ap_auto_json.lf_create_ap_auto_json(
            _file_2g=self.lf_ap_auto_2g_file_entry_var.get(),
            _file_5g=self.lf_ap_auto_5g_file_entry_var.get(),
            _file_6g=self.lf_ap_auto_6g_file_entry_var.get(),
            _dir_2g=self.lf_ap_auto_2g_dir_entry_var.get(),
            _dir_5g=self.lf_ap_auto_5g_dir_entry_var.get(),
            _dir_6g=self.lf_ap_auto_6g_dir_entry_var.get(),
            _ap_auto_duration=self.lf_ap_auto_duration_combobox.get(),
            _use_radio_dict=self.radio_frame.use_radio_var_dict,
            _radio_dict=self.radio_frame.radio_dict,
            _radio_type_dict=self.radio_frame.radio_type_dict,
            _radio_max_sta_dict=self.radio_frame.radio_max_sta_dict,
            _use_radio_var_dict=self.radio_frame.use_radio_var_dict,
            _use_radio_2g_var_dict=self.radio_frame.use_radio_2g_var_dict,
            _use_radio_5g_var_dict=self.radio_frame.use_radio_5g_var_dict,
            _use_radio_6g_var_dict=self.radio_frame.use_radio_6g_var_dict,
            _suite_radios_2g=self.radio_frame.suite_radios_2g,
            _suite_radios_5g=self.radio_frame.suite_radios_5g,
            _suite_radios_6g=self.radio_frame.suite_radios_6g,
            _suite_test_name_2g_dict=self.radio_frame.suite_test_name_2g_dict,
            _suite_test_name_5g_dict=self.radio_frame.suite_test_name_5g_dict,
            _suite_test_name_6g_dict=self.radio_frame.suite_test_name_6g_dict,
            _radio_count=self.radio_frame.radio_count,
            _radio_batch_dict=self.radio_frame.radio_batch_dict,
            _lf_ap_auto_use_qa_var=self.lf_ap_auto_use_qa_var,
            _lf_ap_auto_use_inspect_var=self.lf_ap_auto_use_inspect_var,
            _lf_radio_2g=self.dut_tab.lf_radio_2g_combobox.get(),
            _lf_radio_5g=self.dut_tab.lf_radio_5g_combobox.get(),
            _lf_radio_6g=self.dut_tab.lf_radio_6g_combobox.get(),
            _lf_ap_auto_number_dut_indexes_combobox=self.lf_ap_auto_number_dut_indexes_combobox,
            _lf_ap_auto_basic_client_connectivity=self.lf_ap_auto_basic_client_connectivity_var,
            _lf_ap_auto_band_steering=self.lf_ap_auto_band_steering_var,
            _lf_ap_auto_multi_station_throughput_vs_pkt_size=self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var,
            _lf_ap_auto_stability=self.lf_ap_auto_stability_var,
            _lf_ap_auto_channel_switching_test=self.lf_ap_auto_channel_switching_test_var,
            _lf_ap_auto_throughput_vs_pkt_size=self.lf_ap_auto_throughput_vs_pkt_size_var,
            _lf_ap_auto_capacity=self.lf_ap_auto_capacity_var,
            #_lf_ap_auto_band_steering=self.lf_ap_auto_band_steering_var,
            _lf_ap_auto_long_term=self.lf_ap_auto_long_term_var
        )

        if self.radio_frame.suite_radios_2g != "":
            ap_auto_json.test_suite_band = "2g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_2g_file_entry_var.set(ap_auto_json.get_file_2g())
            self.lf_ap_auto_2g_dir_entry_var.set(ap_auto_json.get_dir_2g())
        if self.radio_frame.suite_radios_5g != "":
            ap_auto_json.test_suite_band = "5g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_5g_file_entry_var.set(ap_auto_json.get_file_5g())
            self.lf_ap_auto_5g_dir_entry_var.set(ap_auto_json.get_dir_5g())
        if self.radio_frame.suite_radios_6g != "":
            ap_auto_json.test_suite_band = "6g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_6g_file_entry_var.set(ap_auto_json.get_file_6g())
            self.lf_ap_auto_6g_dir_entry_var.set(ap_auto_json.get_dir_6g())

        if self.radio_frame.suite_radios_2g == "" and self.radio_frame.suite_radios_5g == "" and self.radio_frame.suite_radios_6g == "":
            tkinter.messagebox.showinfo(title="message", message="Please Read or Select LANforge Radios on LANforge tab")
        else:
            tkinter.messagebox.showinfo(title="success", message="created \n" +
                                        self.lf_ap_auto_2g_dir_entry_var.get() + "/" + self.lf_ap_auto_2g_file_entry_var.get() + "\n" +
                                        self.lf_ap_auto_5g_dir_entry_var.get() + "/" + self.lf_ap_auto_5g_file_entry_var.get() + "\n" +
                                        self.lf_ap_auto_6g_dir_entry_var.get() + "/" + self.lf_ap_auto_6g_file_entry.get())
