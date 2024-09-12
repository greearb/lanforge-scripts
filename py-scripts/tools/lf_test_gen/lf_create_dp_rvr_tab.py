import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import importlib
import logging

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


lf_create_dp_rvr_json = importlib.import_module("lf_create_dp_rvr_json")


class lf_create_dp_rvr_tab():
    def __init__(self, dp_rvr_tab, dut_tab, radio_frame, window_tooltip, current_working_directory):
        self.dp_rvr_tab = dp_rvr_tab
        self.dut_tab = dut_tab
        self.radio_frame = radio_frame
        self.window_tooltip = window_tooltip
        self.current_working_directory = current_working_directory

        # -----------------------------------------------------------------------------------
        #
        #  Create Data Plane or RvR
        #
        # ------------------------------------------------------------------------------------
        self.lf_dp_rvr_tab_frame = tkinter.Frame(self.dp_rvr_tab)
        self.lf_dp_rvr_tab_frame.pack()

        self.dp_rvr_suite_type = ""
        self.dp_rvr_previous_suite_type = ""

        # lanforge Information for json
        self.lf_dp_rvr_frame = tkinter.LabelFrame(self.lf_dp_rvr_tab_frame, text="Data Plane / RvR Configuration")
        self.lf_dp_rvr_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)

        row = 1
        # row 1
        self.lf_dp_rvr_traffic_type_label = tkinter.Label(self.lf_dp_rvr_frame, text="Traffic Type")
        self.lf_dp_rvr_traffic_type_label.grid(row=row, column=0)
        self.lf_dp_rvr_traffic_type_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["UDP", "TCP", "UDP;TCP"])
        self.lf_dp_rvr_traffic_type_combobox.current(0)
        self.lf_dp_rvr_traffic_type_combobox.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_traffic_type_combobox, '''Select the traffic type''')

        self.lf_dp_rvr_dut_traffic_direction_label = tkinter.Label(self.lf_dp_rvr_frame, text="Traffic Direction")
        self.lf_dp_rvr_dut_traffic_direction_label.grid(row=1, column=2)
        self.lf_dp_rvr_dut_traffic_direction_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["DUT Transmit", "DUT Receive", "DUT Transmit;DUT Receive"])
        self.lf_dp_rvr_dut_traffic_direction_combobox.current(0)
        self.lf_dp_rvr_dut_traffic_direction_combobox.grid(row=1, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_dut_traffic_direction_combobox, '''Select DUT Traffic Direction''')

        # Row 2
        row += 1
        self.lf_dp_rvr_pkt_size_label = tkinter.Label(self.lf_dp_rvr_frame, text="Packet Size")
        self.lf_dp_rvr_pkt_size_label.grid(row=row, column=0)
        self.lf_dp_rvr_pkt_size_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["Custom", "64", "172", "256", "512", "1024", "MTU", "4000"])
        self.lf_dp_rvr_pkt_size_combobox.current(6)
        self.lf_dp_rvr_pkt_size_combobox.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_pkt_size_combobox, '''Enter Data Plane or RvR pkt size separated by semi colons
When using Custom Packet Sizes need to append: ;Custom  , min UDP size 64, min TCP size 172''')

        self.lf_dp_rvr_pkt_size_custom_label = tkinter.Label(self.lf_dp_rvr_frame, text="Custom Pkt Size")
        self.lf_dp_rvr_pkt_size_custom_label.grid(row=row, column=2)
        self.lf_dp_rvr_pkt_size_custom_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["", "<custom>", "172;256;512;768;1024;MTU", "64;172;256;512;768;1024;MTU"])
        self.lf_dp_rvr_pkt_size_custom_combobox.current(0)
        self.lf_dp_rvr_pkt_size_custom_combobox.grid(row=row, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_pkt_size_custom_combobox, '''Enter Data Plane or RvR Custom Packet Sized pkt size
The Packet Size needs end in Custom for example   64:Custom''')

        # Row 3
        row += 1
        self.lf_dp_rvr_download_speed_label = tkinter.Label(self.lf_dp_rvr_frame, text="Download Speed")
        self.lf_dp_rvr_download_speed_label.grid(row=row, column=0)
        self.lf_dp_rvr_download_speed_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>", "100%", "85%", "75%", "65%", "50%", "25%", "10%", "5%", "1%", "0"])
        self.lf_dp_rvr_download_speed_combobox.current(1)
        self.lf_dp_rvr_download_speed_combobox.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_download_speed_combobox, '''Download speed is assoicated with DUT Transmit
if on DUT Receive is choosen the Download speed is set to 0''')

        self.lf_dp_rvr_upload_speed_label = tkinter.Label(self.lf_dp_rvr_frame, text="Upload Speed")
        self.lf_dp_rvr_upload_speed_label.grid(row=row, column=2)
        self.lf_dp_rvr_upload_speed_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>", "100%", "85%", "75%", "65%", "50%", "25%", "10%", "5%", "1%", "0"])
        self.lf_dp_rvr_upload_speed_combobox.current(1)
        self.lf_dp_rvr_upload_speed_combobox.grid(row=row, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_upload_speed_combobox, '''Upload speed is associated with with DUT Receive
if only DUT Transmit is choosen the upload speed is set to 0''')

        # Row 4
        row += 1
        self.lf_dp_rvr_bandwidth_label = tkinter.Label(self.lf_dp_rvr_frame, text="Bandwidth")
        self.lf_dp_rvr_bandwidth_label.grid(row=row, column=0)
        self.lf_dp_rvr_bandwidth_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["AUTO", "20", "40", "80", "160"])
        self.lf_dp_rvr_bandwidth_combobox.current(0)
        self.lf_dp_rvr_bandwidth_combobox.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_bandwidth_combobox, '''Bandwidth AUTO, 20, 40, 80, 160''')

        self.lf_dp_rvr_spatial_streams_label = tkinter.Label(self.lf_dp_rvr_frame, text="Spatial Streams")
        self.lf_dp_rvr_spatial_streams_label.grid(row=row, column=2)
        self.lf_dp_rvr_spatial_streams_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["AUTO", "1", "2", "3", "4"])
        self.lf_dp_rvr_spatial_streams_combobox.current(0)
        self.lf_dp_rvr_spatial_streams_combobox.grid(row=row, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_spatial_streams_combobox, '''Spatial Streams Auto, 1x1, 2x2, 3x3, 4x4''')

        # Row 5
        row += 1
        self.lf_dp_rvr_attenuator_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuator")
        self.lf_dp_rvr_attenuator_label.grid(row=row, column=0)
        self.lf_dp_rvr_attenuator_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["", "ATTENUATOR_1", "ATTENUATOR_2", "ATTENUATOR_3"])
        self.lf_dp_rvr_attenuator_combobox.current(0)
        self.lf_dp_rvr_attenuator_combobox.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_attenuator_combobox, "The ATTENUATOR is definded in the test_rig.json file")

        # Row 6
        row += 1
        self.lf_dp_rvr_attenuation_2g_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuation 2g")
        self.lf_dp_rvr_attenuation_2g_label.grid(row=row, column=0)
        self.lf_dp_rvr_attenuation_2g_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>", "0..+100..500", "0..+100..600", "0..+100..700", "400,450,460,470,490,500"])
        self.lf_dp_rvr_attenuation_2g_combobox.current(1)
        self.lf_dp_rvr_attenuation_2g_combobox.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_attenuation_2g_combobox, '''Select the atteunation range  <start>..+<step>..<end>
May also enter custom Example 0..+100..700''')

        self.lf_dp_rvr_attenuation_5g_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuation 5g")
        self.lf_dp_rvr_attenuation_5g_label.grid(row=row, column=2)
        self.lf_dp_rvr_attenuation_5g_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>", "0..+100..500", "0..+100..600", "0..+100..700", "400,450,460,470,490,500"])
        self.lf_dp_rvr_attenuation_5g_combobox.current(1)
        self.lf_dp_rvr_attenuation_5g_combobox.grid(row=row, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_attenuation_5g_combobox, '''Select the atteunation range  <start>..+<step>..<end>
May also enter custom Example 0..+100..700''')

        self.lf_dp_rvr_attenuation_6g_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuation 6g")
        self.lf_dp_rvr_attenuation_6g_label.grid(row=row, column=4)
        self.lf_dp_rvr_attenuation_6g_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>", "0..+100..500", "0..+100..600", "0..+100..700", "400,450,460,470,490,500"])
        self.lf_dp_rvr_attenuation_6g_combobox.current(1)
        self.lf_dp_rvr_attenuation_6g_combobox.grid(row=row, column=5)
        self.window_tooltip.bind(self.lf_dp_rvr_attenuation_6g_combobox, '''Select the atteunation range  <start>..+<step>..<end>
May also enter custom Example 0..+100..700''')

        # row 7
        row += 1
        self.lf_dp_rvr_2g_file = tkinter.Label(self.lf_dp_rvr_frame, text='2g json file')
        self.lf_dp_rvr_2g_file.grid(row=row, column=0)
        self.lf_dp_rvr_2g_file_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_2g_file_entry_var.set("")
        self.lf_dp_rvr_2g_file_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable=self.lf_dp_rvr_2g_file_entry_var, width=64)
        self.lf_dp_rvr_2g_file_entry.grid(row=row, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_dp_rvr_2g_file_entry, '''Auto Generated json file name to be used by lf_check.py would be:
./lf_check.py  --json_test <QA generated name>.json:<Qa generated name>''')

        self.lf_dp_rvr_2g_dir = tkinter.Label(self.lf_dp_rvr_frame, text='2g json dir')
        self.lf_dp_rvr_2g_dir.grid(row=row, column=3)
        self.lf_dp_rvr_2g_dir_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_2g_dir_entry_var.set("")
        self.lf_dp_rvr_2g_dir_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable=self.lf_dp_rvr_2g_dir_entry_var, width=64)
        self.lf_dp_rvr_2g_dir_entry.grid(row=row, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_dp_rvr_2g_dir_entry, '''directory to place json, if blank will auto gen''')

        # row 8
        row += 1
        self.lf_dp_rvr_5g_file = tkinter.Label(self.lf_dp_rvr_frame, text='5g json file')
        self.lf_dp_rvr_5g_file.grid(row=row, column=0)
        self.lf_dp_rvr_5g_file_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_5g_file_entry_var.set("")
        self.lf_dp_rvr_5g_file_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable=self.lf_dp_rvr_5g_file_entry_var, width=64)
        self.lf_dp_rvr_5g_file_entry.grid(row=row, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_dp_rvr_5g_file_entry, '''Auto Generated json file name to be used by lf_check.py would be:
./lf_check.py  --json_test <QA generated name>.json:<Qa generated name>''')

        self.lf_dp_rvr_5g_dir = tkinter.Label(self.lf_dp_rvr_frame, text='5g json dir')
        self.lf_dp_rvr_5g_dir.grid(row=row, column=3)
        self.lf_dp_rvr_5g_dir_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_5g_dir_entry_var.set("")
        self.lf_dp_rvr_5g_dir_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable=self.lf_dp_rvr_5g_dir_entry_var, width=64)
        self.lf_dp_rvr_5g_dir_entry.grid(row=row, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_dp_rvr_5g_dir_entry, '''directory to place json, if blank will auto gen''')

        # row 9
        row += 1
        self.lf_dp_rvr_6g_file = tkinter.Label(self.lf_dp_rvr_frame, text='6g json file')
        self.lf_dp_rvr_6g_file.grid(row=row, column=0)
        self.lf_dp_rvr_6g_file_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_6g_file_entry_var.set("")
        self.lf_dp_rvr_6g_file_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable=self.lf_dp_rvr_6g_file_entry_var, width=64)
        self.lf_dp_rvr_6g_file_entry.grid(row=row, column=1, columnspan=2)
        self.window_tooltip.bind(self.lf_dp_rvr_6g_file_entry, ''''Auto Generated json file name to be used by lf_check.py would be:
./lf_check.py  --json_test <QA generated name>.json:<Qa generated name>''')

        self.lf_dp_rvr_6g_dir = tkinter.Label(self.lf_dp_rvr_frame, text='6g json dir')
        self.lf_dp_rvr_6g_dir.grid(row=row, column=3)
        self.lf_dp_rvr_6g_dir_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_6g_dir_entry_var.set("")
        self.lf_dp_rvr_6g_dir_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable=self.lf_dp_rvr_6g_dir_entry_var, width=64)
        self.lf_dp_rvr_6g_dir_entry.grid(row=row, column=4, columnspan=2)
        self.window_tooltip.bind(self.lf_dp_rvr_6g_dir_entry, '''directory to place json, if blank will auto gen''')

        # row 10
        row += 1
        self.lf_dp_rvr_duration = tkinter.Label(self.lf_dp_rvr_frame, text='test duration')
        self.lf_dp_rvr_duration.grid(row=row, column=0)
        self.lf_dp_rvr_duration_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<Custom>", "5000 (5 sec)", "10000 (10 sec)", "15000 (15 sec)", "20000 (20 sec)", "30000 (30 sec)", "60000 (1 min)", "180000 (3 min)", "300000 (5min)"])
        self.lf_dp_rvr_duration_combobox.current(3)
        self.lf_dp_rvr_duration_combobox.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_duration_combobox, '''Enter the test duration , for custom it is in ms
Example:  20000 milli seconds will run the test for 20 seconds
if left blank will default to 20000''')

        self.lf_dp_rvr_number_dut_indexes = tkinter.Label(self.lf_dp_rvr_frame, text="Number DUT Indexes")
        self.lf_dp_rvr_number_dut_indexes.grid(row=row, column=2)
        self.lf_dp_rvr_number_dut_indexes_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["1", "2", "3", "4"])
        self.lf_dp_rvr_number_dut_indexes_combobox.current(2)
        self.lf_dp_rvr_number_dut_indexes_combobox.grid(row=row, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_number_dut_indexes_combobox, '''Number of DUT indexes valid in the DUT json''')

        # row 11
        row += 1
        self.lf_dp_rvr_use_qa_var = tkinter.StringVar(value="Use")
        self.lf_dp_rvr_use_qa_var_check = tkinter.Checkbutton(self.lf_dp_rvr_frame, text="lf_qa", variable=self.lf_dp_rvr_use_qa_var,
                                                              onvalue="Use", offvalue="Do Not Use")
        self.lf_dp_rvr_use_qa_var_check.grid(row=row, column=0)
        self.window_tooltip.bind(self.lf_dp_rvr_use_qa_var_check, '''Recommended: Wifi Capacity Test Suite Json will include lf_qa.
lf_qa will compare performance over multiple runs for Chamber View tests and tests that include kpi''')

        self.lf_dp_rvr_use_inspect_var = tkinter.StringVar(value="Use")
        self.lf_dp_rvr_use_inspect_check = tkinter.Checkbutton(self.lf_dp_rvr_frame, text="lf_inspect", variable=self.lf_dp_rvr_use_inspect_var,
                                                               onvalue="Use", offvalue="Do Not Use")
        self.lf_dp_rvr_use_inspect_check.grid(row=row, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_use_inspect_check, '''Recommended: Wifi Capacity Test Suite Json will include lf_inspect.
lf_inspect will compare performance between two individual runs for Chamber View tests and tests that include kpi''')

        # row 12
        row += 1
        self.lf_dp_rvr_save = ttk.Button(self.lf_dp_rvr_frame, text='Create DP Suite', command=self.create_dp_json)
        self.lf_dp_rvr_save.grid(row=row, column=0, sticky="news", padx=20, pady=10)
        dp_tool_tip_text = "Save Data Plane Json File in directory specified in 'json dir' entry or will create \n In Current Working Directory: {}".format(self.current_working_directory)
        self.window_tooltip.bind(self.lf_dp_rvr_save, dp_tool_tip_text)

        self.lf_dp_rvr_save = ttk.Button(self.lf_dp_rvr_frame, text='Create RvR Suite', command=self.create_rvr_json)
        self.lf_dp_rvr_save.grid(row=row, column=1, sticky="news", padx=20, pady=10)
        rvr_tool_tip_text = "Save RvR test suite Json File in directory specified in 'json dir' entry or will create \n In Current Working Directory: {}".format(self.current_working_directory)
        self.window_tooltip.bind(self.lf_dp_rvr_save, rvr_tool_tip_text)

        self.lf_dp_rvr_clear = ttk.Button(self.lf_dp_rvr_frame, text='Clear DP, RvR Info', command=self.dp_rvr_clear_information)
        self.lf_dp_rvr_clear.grid(row=row, column=2, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_dp_rvr_clear, 'Clear File Names , use between test suite generation')

        # Max Stations
        for widget in self.lf_dp_rvr_frame.winfo_children():
            widget.grid_configure(padx=5, pady=5)

        # -----------------------------------------------------------------------------------
        #
        #  End Data Plane or RvR
        #
        # ------------------------------------------------------------------------------------

    def dp_rvr_clear_information(self):
        self.lf_dp_rvr_2g_file_entry_var.set("")
        self.lf_dp_rvr_5g_file_entry_var.set("")
        self.lf_dp_rvr_6g_file_entry_var.set("")
        self.lf_dp_rvr_2g_dir_entry_var.set("")
        self.lf_dp_rvr_5g_dir_entry_var.set("")
        self.lf_dp_rvr_6g_dir_entry_var.set("")

        # self.lf_dp_rvr_duration_entry_var.set("")

    def create_dp_json(self):
        self.dp_rvr_suite_type = "dp"
        self.create_dp_rvr_json()

    def create_rvr_json(self):
        self.dp_rvr_suite_type = "rvr"
        self.create_dp_rvr_json()

    def create_dp_rvr_json(self):
        # set file names
        self.lf_dp_rvr_2g_file_entry_var.get()
        self.lf_dp_rvr_5g_file_entry_var.get()
        self.lf_dp_rvr_6g_file_entry_var.get()
        self.lf_dp_rvr_duration_combobox.get()
        self.lf_dp_rvr_number_dut_indexes_combobox.get()

        self.lf_dp_rvr_use_qa_var.get()
        self.lf_dp_rvr_use_inspect_var.get()

        self.lf_dp_rvr_traffic_type_combobox.get()
        self.lf_dp_rvr_dut_traffic_direction_combobox.get()
        self.lf_dp_rvr_pkt_size_combobox.get()
        self.lf_dp_rvr_pkt_size_custom_combobox.get()
        self.lf_dp_rvr_download_speed_combobox.get()
        self.lf_dp_rvr_upload_speed_combobox.get()
        self.lf_dp_rvr_bandwidth_combobox.get()
        self.lf_dp_rvr_spatial_streams_combobox.get()
        self.lf_dp_rvr_attenuator_combobox.get()
        self.lf_dp_rvr_attenuation_2g_combobox.get()
        self.lf_dp_rvr_attenuation_5g_combobox.get()
        self.lf_dp_rvr_attenuation_6g_combobox.get()

        dictionary_length = len(self.radio_frame.radio_dict)
        logger.debug("radio_dict length = {length}".format(length=dictionary_length))
        dp_rvr_json = lf_create_dp_rvr_json.lf_create_dp_rvr_json(
            _suite_type=self.dp_rvr_suite_type,
            _file_2g=self.lf_dp_rvr_2g_file_entry_var.get(),
            _file_5g=self.lf_dp_rvr_5g_file_entry_var.get(),
            _file_6g=self.lf_dp_rvr_6g_file_entry_var.get(),
            _dir_2g=self.lf_dp_rvr_2g_dir_entry_var.get(),
            _dir_5g=self.lf_dp_rvr_5g_dir_entry_var.get(),
            _dir_6g=self.lf_dp_rvr_6g_dir_entry_var.get(),
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
            _lf_dp_rvr_use_qa_var=self.lf_dp_rvr_use_qa_var,
            _lf_dp_rvr_use_inspect_var=self.lf_dp_rvr_use_inspect_var,
            _lf_dp_rvr_duration_combobox=self.lf_dp_rvr_duration_combobox,
            _lf_dp_rvr_traffic_type_combobox=self.lf_dp_rvr_traffic_type_combobox,
            _lf_dp_rvr_dut_traffic_direction_combobox=self.lf_dp_rvr_dut_traffic_direction_combobox,
            _lf_dp_rvr_pkt_size_combobox=self.lf_dp_rvr_pkt_size_combobox,
            _lf_dp_rvr_pkt_size_custom_combobox=self.lf_dp_rvr_pkt_size_custom_combobox,
            _lf_dp_rvr_download_speed_combobox=self.lf_dp_rvr_download_speed_combobox,
            _lf_dp_rvr_upload_speed_combobox=self.lf_dp_rvr_upload_speed_combobox,
            _lf_dp_rvr_bandwidth_combobox=self.lf_dp_rvr_bandwidth_combobox,
            _lf_dp_rvr_spatial_streams_combobox=self.lf_dp_rvr_spatial_streams_combobox,
            _lf_dp_rvr_attenuator_combobox=self.lf_dp_rvr_attenuator_combobox,
            _lf_dp_rvr_attenuation_2g_combobox=self.lf_dp_rvr_attenuation_2g_combobox,
            _lf_dp_rvr_attenuation_5g_combobox=self.lf_dp_rvr_attenuation_5g_combobox,
            _lf_dp_rvr_attenuation_6g_combobox=self.lf_dp_rvr_attenuation_6g_combobox,
            _lf_radio_2g=self.dut_tab.lf_radio_2g_combobox.get(),
            _lf_radio_5g=self.dut_tab.lf_radio_5g_combobox.get(),
            _lf_radio_6g=self.dut_tab.lf_radio_6g_combobox.get(),
            _lf_dp_rvr_number_dut_indexes_combobox=self.lf_dp_rvr_number_dut_indexes_combobox
        )

        if self.radio_frame.suite_radios_2g != "":
            dp_rvr_json.test_suite_band = "2g"
            dp_rvr_json.create_suite()
            self.lf_dp_rvr_2g_file_entry_var.set(dp_rvr_json.get_file_2g())
            self.lf_dp_rvr_2g_dir_entry_var.set(dp_rvr_json.get_dir_2g())
        else:
            self.lf_dp_rvr_2g_file_entry_var.set("")

        if self.radio_frame.suite_radios_5g != "":
            dp_rvr_json.test_suite_band = "5g"
            dp_rvr_json.create_suite()
            self.lf_dp_rvr_5g_file_entry_var.set(dp_rvr_json.get_file_5g())
            self.lf_dp_rvr_5g_dir_entry_var.set(dp_rvr_json.get_dir_5g())
        else:
            self.lf_dp_rvr_5g_file_entry_var.set("")

        if self.radio_frame.suite_radios_6g != "":
            dp_rvr_json.test_suite_band = "6g"
            dp_rvr_json.create_suite()
            self.lf_dp_rvr_6g_file_entry_var.set(dp_rvr_json.get_file_6g())
            self.lf_dp_rvr_6g_dir_entry_var.set(dp_rvr_json.get_dir_6g())
        else:
            self.lf_dp_rvr_6g_file_entry_var.set("")

        if self.radio_frame.suite_radios_2g == "" and self.radio_frame.suite_radios_5g == "" and self.radio_frame.suite_radios_6g == "":
            tkinter.messagebox.showinfo(title="message", message="Please Read or Select LANforge Radios on LANforge tab")
        else:
            tkinter.messagebox.showinfo(title="success", message="created \n" +
                                        self.lf_dp_rvr_2g_dir_entry_var.get() + "/" + self.lf_dp_rvr_2g_file_entry_var.get() + "\n" +
                                        self.lf_dp_rvr_5g_dir_entry_var.get() + "/" + self.lf_dp_rvr_5g_file_entry_var.get() + "\n" +
                                        self.lf_dp_rvr_6g_dir_entry_var.get() + "/" + self.lf_dp_rvr_6g_file_entry.get())
