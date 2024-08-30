import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import importlib
import logging

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


lf_create_wc_json = importlib.import_module("lf_create_wc_json")


class lf_create_wc_tab():
    def __init__(self, wc_tab, dut_tab, radio_frame, window_tooltip, current_working_directory):
        self.wc_tab = wc_tab
        self.dut_tab = dut_tab
        self.radio_frame = radio_frame
        self.window_tooltip = window_tooltip
        self.current_working_directory = current_working_directory

        # -----------------------------------------------------------------------------------
        #
        #  Create Wifi Capacity
        #
        # ------------------------------------------------------------------------------------
        self.lf_wc_tab_frame = tkinter.Frame(self.wc_tab)
        self.lf_wc_tab_frame.pack()

        # lanforge Information for json
        self.lf_wc_frame = tkinter.LabelFrame(self.lf_wc_tab_frame, text="Wifi Capacity")
        self.lf_wc_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)

        self.lf_wc_2g_file = tkinter.Label(self.lf_wc_frame, text='2g json file')
        self.lf_wc_2g_file.grid(row=1, column=0)
        self.lf_wc_2g_file_entry_var = tkinter.StringVar()
        self.lf_wc_2g_file_entry_var.set("")
        self.lf_wc_2g_file_entry = tkinter.Entry(self.lf_wc_frame, textvariable=self.lf_wc_2g_file_entry_var, width=48)
        self.lf_wc_2g_file_entry.grid(row=1, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_wc_2g_file_entry, '''Auto generated name for Wifi Capacity Test Suite''')

        self.lf_wc_2g_dir = tkinter.Label(self.lf_wc_frame, text='2g json dir')
        self.lf_wc_2g_dir.grid(row=1, column=3)
        self.lf_wc_2g_dir_entry_var = tkinter.StringVar()
        self.lf_wc_2g_dir_entry_var.set("")
        self.lf_wc_2g_dir_entry = tkinter.Entry(self.lf_wc_frame, textvariable=self.lf_wc_2g_dir_entry_var, width=48)
        self.lf_wc_2g_dir_entry.grid(row=1, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_wc_2g_dir_entry, '''Directory for Wifi Capacity Test Suite, if blank will show dir created in''')

        self.lf_wc_5g_file = tkinter.Label(self.lf_wc_frame, text='5g json file')
        self.lf_wc_5g_file.grid(row=2, column=0)
        self.lf_wc_5g_file_entry_var = tkinter.StringVar()
        self.lf_wc_5g_file_entry_var.set("")
        self.lf_wc_5g_file_entry = tkinter.Entry(self.lf_wc_frame, textvariable=self.lf_wc_5g_file_entry_var, width=48)
        self.lf_wc_5g_file_entry.grid(row=2, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_wc_5g_file_entry, '''Auto generated name for Wifi Capacity Test Suite''')

        self.lf_wc_5g_dir = tkinter.Label(self.lf_wc_frame, text='5g json dir')
        self.lf_wc_5g_dir.grid(row=2, column=3)
        self.lf_wc_5g_dir_entry_var = tkinter.StringVar()
        self.lf_wc_5g_dir_entry_var.set("")
        self.lf_wc_5g_dir_entry = tkinter.Entry(self.lf_wc_frame, textvariable=self.lf_wc_5g_dir_entry_var, width=48)
        self.lf_wc_5g_dir_entry.grid(row=2, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_wc_5g_dir_entry, '''Directory for Wifi Capacity Test Suite, if blank will show dir created in''')

        self.lf_wc_6g_file = tkinter.Label(self.lf_wc_frame, text='6g json file')
        self.lf_wc_6g_file.grid(row=3, column=0)
        self.lf_wc_6g_file_entry_var = tkinter.StringVar()
        self.lf_wc_6g_file_entry_var.set("")
        self.lf_wc_6g_file_entry = tkinter.Entry(self.lf_wc_frame, textvariable=self.lf_wc_6g_file_entry_var, width=48)
        self.lf_wc_6g_file_entry.grid(row=3, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_wc_6g_file_entry, '''Auto generated name for Wifi Capacity Test Suite''')

        self.lf_wc_6g_dir = tkinter.Label(self.lf_wc_frame, text='6g json dir')
        self.lf_wc_6g_dir.grid(row=3, column=3)
        self.lf_wc_6g_dir_entry_var = tkinter.StringVar()
        self.lf_wc_6g_dir_entry_var.set("")
        self.lf_wc_6g_dir_entry = tkinter.Entry(self.lf_wc_frame, textvariable=self.lf_wc_6g_dir_entry_var, width=48)
        self.lf_wc_6g_dir_entry.grid(row=3, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_wc_6g_file_entry, '''Directory for Wifi Capacity Test Suite, if blank will show dir created in''')

        self.lf_wc_duration = tkinter.Label(self.lf_wc_frame, text='test duration (ms)')
        self.lf_wc_duration.grid(row=4, column=0)
        self.lf_wc_duration_combobox = ttk.Combobox(self.lf_wc_frame, values=["<Custom>", "5000 (5 sec)", "10000 (10 sec)", "15000 (15 sec)", "20000 (20 sec)", "30000 (30 sec)", "60000 (1 min)", "300000 (5min)"])
        self.lf_wc_duration_combobox.current(3)
        self.lf_wc_duration_combobox.grid(row=4, column=1)
        self.window_tooltip.bind(self.lf_wc_duration_combobox, '''Select the duration of each iteration  ''')

        self.lf_wc_number_dut_indexes = tkinter.Label(self.lf_wc_frame, text="Number DUT Indexes")
        self.lf_wc_number_dut_indexes.grid(row=4, column=2)
        self.lf_wc_number_dut_indexes_combobox = ttk.Combobox(self.lf_wc_frame, values=["1", "2", "3", "4"])
        self.lf_wc_number_dut_indexes_combobox.current(2)
        self.lf_wc_number_dut_indexes_combobox.grid(row=4, column=3)
        self.window_tooltip.bind(self.lf_wc_number_dut_indexes_combobox, '''Number of DUT indexes valid in the DUT json''')

        self.lf_wc_sta_profile = tkinter.Label(self.lf_wc_frame, text="Station Profile")
        self.lf_wc_sta_profile.grid(row=5, column=0)
        self.lf_wc_sta_profile_combobox = ttk.Combobox(self.lf_wc_frame, values=["STA-AUTO", "STA-AC", "STA-AX", "STA-AX-160", "STA-BE", "STA-abg", "STA-n"])
        self.lf_wc_sta_profile_combobox.current(0)
        self.lf_wc_sta_profile_combobox.grid(row=5, column=1)
        self.window_tooltip.bind(self.lf_wc_sta_profile_combobox, '''Station profile,  when using stations greater then 1 ,
MU MIMO will perform poor for AX radios for virtual stations greater then one, use STA-AC''')

        self.lf_wc_sta_protocol = tkinter.Label(self.lf_wc_frame, text="Protocol")
        self.lf_wc_sta_protocol.grid(row=5, column=2)
        self.lf_wc_sta_protocol_combobox = ttk.Combobox(self.lf_wc_frame, values=["UDP", "TCP", "UDP-IPv4", "TCP and UDP"])
        self.lf_wc_sta_protocol_combobox.current(2)
        self.lf_wc_sta_protocol_combobox.grid(row=5, column=3)
        self.window_tooltip.bind(self.lf_wc_sta_protocol_combobox, '''The network traffic protocal type to be generated''')

        self.lf_wc_dl_rate = tkinter.Label(self.lf_wc_frame, text="dl_rate")
        self.lf_wc_dl_rate.grid(row=6, column=0)
        self.lf_wc_dl_rate_combobox = ttk.Combobox(self.lf_wc_frame, values=["custom>", "0", "9.6K", "56K", "128K", "256K", "384K", "768K", "1M",
                                                                             "1.544M", "2M", "6M", "10M", "30M", "37M", "44.736M", "100M", "152M", "155.52M", "304M", "622.08M", "1G", "2.488G", "4.97664G",
                                                                             "5G", "9.94328G", "10G", "20G", "25G", "40G", "50G", "100G"])
        self.lf_wc_dl_rate_combobox.current(8)
        self.lf_wc_dl_rate_combobox.grid(row=6, column=1)
        self.window_tooltip.bind(self.lf_wc_dl_rate_combobox, '''Download Rate enter number or number followed by K M or G''')

        self.lf_wc_ul_rate = tkinter.Label(self.lf_wc_frame, text="ul_rate")
        self.lf_wc_ul_rate.grid(row=6, column=2)
        self.lf_wc_ul_rate_combobox = ttk.Combobox(self.lf_wc_frame, values=["custom>", "0", "9.6K", "56K", "128K", "256K", "384K", "768K", "1M",
                                                                             "1.544M", "2M", "6M", "10M", "30M", "37M", "44.736M", "100M", "152M", "155.52M", "304M", "622.08M", "1G", "2.488G", "4.97664G",
                                                                             "5G", "9.94328G", "10G", "20G", "25G", "40G", "50G", "100G"])
        self.lf_wc_ul_rate_combobox.current(8)
        self.lf_wc_ul_rate_combobox.grid(row=6, column=3)
        self.window_tooltip.bind(self.lf_wc_ul_rate_combobox, '''Upload Rate enter number or number followed by K M or G''')

        self.lf_wc_dut_traffic_direction_label = tkinter.Label(self.lf_wc_frame, text="Traffic Direction")
        self.lf_wc_dut_traffic_direction_label.grid(row=6, column=4)
        self.lf_wc_dut_traffic_direction_combobox = ttk.Combobox(self.lf_wc_frame, values=["DUT DL", "DUT UL", "DUT DL;DUT UL"])
        self.lf_wc_dut_traffic_direction_combobox.current(2)
        self.lf_wc_dut_traffic_direction_combobox.grid(row=6, column=5)
        self.window_tooltip.bind(self.lf_wc_dut_traffic_direction_combobox, '''Select DUT Download or DUT Upload''')

        self.lf_wc_use_qa_var = tkinter.StringVar(value="Use")
        self.lf_wc_use_qa_check = tkinter.Checkbutton(self.lf_wc_frame, text="lf_qa", variable=self.lf_wc_use_qa_var,
                                                      onvalue="Use", offvalue="Do Not Use")
        self.lf_wc_use_qa_check.grid(row=7, column=0)
        self.window_tooltip.bind(self.lf_wc_use_qa_check, '''Recommended: Wifi Capacity Test Suite Json will include lf_qa.
lf_qa will compare performance over multiple runs for Chamber View tests and tests that include kpi''')

        self.lf_wc_use_inspect_var = tkinter.StringVar(value="Use")
        self.lf_wc_use_inspect_check = tkinter.Checkbutton(self.lf_wc_frame, text="lf_inspect", variable=self.lf_wc_use_inspect_var,
                                                           onvalue="Use", offvalue="Do Not Use")
        self.lf_wc_use_inspect_check.grid(row=7, column=1)
        self.window_tooltip.bind(self.lf_wc_use_inspect_check, '''Recommended: Wifi Capacity Test Suite Json will include lf_inspect.
lf_inspect will compare performance between two individual runs for Chamber View tests and tests that include kpi''')

        self.lf_wc_save = ttk.Button(self.lf_wc_frame, text='Create Wifi Capacity Test Suite Json', command=self.create_wc_json)
        self.lf_wc_save.grid(row=8, column=0, sticky="news", padx=20, pady=10)
        wc_tool_tip_text = "Save Wifi Capacity Json File in directory specified in 'json dir' entry or will create \n In Current Working Directory: {}".format(self.current_working_directory)
        self.window_tooltip.bind(self.lf_wc_save, wc_tool_tip_text)

        self.lf_wc_clear = ttk.Button(self.lf_wc_frame, text='Clear WC Info', command=self.wc_clear_information)
        self.lf_wc_clear.grid(row=8, column=1, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_wc_clear, 'Clear Wifi Capacity Information, use between test suite generation')

        # Max Stations
        for widget in self.lf_wc_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # -----------------------------------------------------------------------------------
        #
        #  End Wifi Capacity
        #
        # ------------------------------------------------------------------------------------

    def wc_clear_information(self):
        self.lf_wc_2g_file_entry_var.set("")
        self.lf_wc_5g_file_entry_var.set("")
        self.lf_wc_6g_file_entry_var.set("")
        self.lf_wc_2g_dir_entry_var.set("")
        self.lf_wc_5g_dir_entry_var.set("")
        self.lf_wc_6g_dir_entry_var.set("")

    def create_wc_json(self):
        # use the auto generated name
        # self.wc_clear_information()

        wc_duration = self.lf_wc_duration_combobox.get()
        if wc_duration == "":
            self.lf_wc_duration_combobox.set("20000")

        self.lf_wc_use_qa_var.get()
        self.lf_wc_use_inspect_var.get()

        self.dut_tab.lf_radio_2g_combobox.get()
        self.dut_tab.lf_radio_5g_combobox.get()
        self.dut_tab.lf_radio_6g_combobox.get()

        self.lf_wc_number_dut_indexes_combobox.get()
        self.lf_wc_sta_profile_combobox.get()
        self.lf_wc_dut_traffic_direction_combobox.get()
        self.lf_wc_sta_protocol_combobox.get()

        ul_rate = self.lf_wc_ul_rate_combobox.get()

        dl_rate = self.lf_wc_dl_rate_combobox.get()

        dictionary_length = len(self.radio_frame.radio_dict)
        logger.debug("radio_dict length = {length}".format(length=dictionary_length))
        wc_json = lf_create_wc_json.lf_create_wc_json(
            _file_2g=self.lf_wc_2g_file_entry_var.get(),
            _file_5g=self.lf_wc_5g_file_entry_var.get(),
            _file_6g=self.lf_wc_6g_file_entry_var.get(),
            _dir_2g=self.lf_wc_2g_dir_entry_var.get(),
            _dir_5g=self.lf_wc_5g_dir_entry_var.get(),
            _dir_6g=self.lf_wc_6g_dir_entry_var.get(),
            _wc_duration=self.lf_wc_duration_combobox.get(),
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
            _lf_wc_use_qa_var=self.lf_wc_use_qa_var,
            _lf_wc_use_inspect_var=self.lf_wc_use_inspect_var,
            _lf_radio_2g=self.dut_tab.lf_radio_2g_combobox.get(),
            _lf_radio_5g=self.dut_tab.lf_radio_5g_combobox.get(),
            _lf_radio_6g=self.dut_tab.lf_radio_6g_combobox.get(),
            _lf_wc_number_dut_indexes_combobox=self.lf_wc_number_dut_indexes_combobox,
            _lf_wc_sta_profile_combobox=self.lf_wc_sta_profile_combobox,
            _ul_rate=ul_rate,
            _dl_rate=dl_rate,
            _lf_wc_dut_traffic_direction_combobox=self.lf_wc_dut_traffic_direction_combobox,
            _lf_wc_sta_protocol_combobox=self.lf_wc_sta_protocol_combobox
        )

        if self.radio_frame.suite_radios_2g != "":
            wc_json.test_suite_band = "2g"
            wc_json.create_suite()
            self.lf_wc_2g_file_entry_var.set(wc_json.get_file_2g())
            self.lf_wc_2g_dir_entry_var.set(wc_json.get_dir_2g())
        if self.radio_frame.suite_radios_5g != "":
            wc_json.test_suite_band = "5g"
            wc_json.create_suite()
            self.lf_wc_5g_file_entry_var.set(wc_json.get_file_5g())
            self.lf_wc_5g_dir_entry_var.set(wc_json.get_dir_5g())
        if self.radio_frame.suite_radios_6g != "":
            wc_json.test_suite_band = "6g"
            wc_json.create_suite()
            self.lf_wc_6g_file_entry_var.set(wc_json.get_file_6g())
            self.lf_wc_6g_dir_entry_var.set(wc_json.get_dir_6g())

        if self.radio_frame.suite_radios_2g == "" and self.radio_frame.suite_radios_5g == "" and self.radio_frame.suite_radios_6g == "":
            tkinter.messagebox.showinfo(title="message", message="Please Read or Select LANforge Radios on LANforge tab")
        else:
            tkinter.messagebox.showinfo(title="success", message="created \n" +
                                        self.lf_wc_2g_dir_entry_var.get() + "/" + self.lf_wc_2g_file_entry_var.get() + "\n" +
                                        self.lf_wc_5g_dir_entry_var.get() + "/" + self.lf_wc_5g_file_entry_var.get() + "\n" +
                                        self.lf_wc_6g_dir_entry_var.get() + "/" + self.lf_wc_6g_file_entry.get())
