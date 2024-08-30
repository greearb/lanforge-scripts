import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import importlib

lf_dut_json = importlib.import_module("lf_create_dut_json")


class lf_create_dut_tab():
    def __init__(self, dut_tab, window_tooltip, current_working_directory):
        self.dut_tab = dut_tab
        self.window_tooltip = window_tooltip
        self.current_working_directory = current_working_directory

        # -----------------------------------------------------------------------------------
        #
        #  Create DUT json
        #
        # ------------------------------------------------------------------------------------

        self.lf_dut_tab_frame = tkinter.Frame(self.dut_tab)
        self.lf_dut_tab_frame.pack()

        # lanforge Information for json
        self.lf_dut_frame = tkinter.LabelFrame(self.lf_dut_tab_frame, text="Device Unter Test (DUT) Information")
        self.lf_dut_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)

        self.lf_dut_name = tkinter.Label(self.lf_dut_frame, text="DUT Name")
        self.lf_dut_name.grid(row=1, column=0)
        self.lf_dut_name_entry_var = tkinter.StringVar()
        self.lf_dut_name_entry_var.set("dut_name")
        self.lf_dut_name_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_name_entry_var)
        self.lf_dut_name_entry.grid(row=1, column=1)
        self.window_tooltip.bind(self.lf_dut_name_entry, 'Enter DUT Name with no spaces')

        self.lf_dut_hw_ver = tkinter.Label(self.lf_dut_frame, text='HW Version')
        self.lf_dut_hw_ver.grid(row=1, column=2)
        self.lf_dut_hw_ver_entry_var = tkinter.StringVar()
        self.lf_dut_hw_ver_entry_var.set("hw_ver_1.1")
        self.lf_dut_hw_ver_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_hw_ver_entry_var)
        self.lf_dut_hw_ver_entry.grid(row=1, column=3)
        self.window_tooltip.bind(self.lf_dut_hw_ver_entry, 'Enter DUT Hardware Version')

        self.lf_dut_sw_ver = tkinter.Label(self.lf_dut_frame, text="SW Version")
        self.lf_dut_sw_ver.grid(row=1, column=4)
        self.lf_dut_sw_ver_entry_var = tkinter.StringVar()
        self.lf_dut_sw_ver_entry_var.set("sw_ver_1.1")
        self.lf_dut_sw_ver_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_sw_ver_entry_var)
        self.lf_dut_sw_ver_entry.grid(row=1, column=5)
        self.window_tooltip.bind(self.lf_dut_sw_ver_entry, 'Enter DUT Software Version')

        # second row
        self.lf_dut_model = tkinter.Label(self.lf_dut_frame, text='Model')
        self.lf_dut_model.grid(row=2, column=0)
        self.lf_dut_model_entry_var = tkinter.StringVar()
        self.lf_dut_model_entry_var.set("dut_model")
        self.lf_dut_model_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_model_entry_var)
        self.lf_dut_model_entry.grid(row=2, column=1)
        self.window_tooltip.bind(self.lf_dut_model_entry, 'Enter DUT Model')

        self.lf_dut_serial_rig = tkinter.Label(self.lf_dut_frame, text="Serial Number")
        self.lf_dut_serial_rig.grid(row=2, column=2)
        self.lf_dut_serial_entry_var = tkinter.StringVar()
        self.lf_dut_serial_entry_var.set("serial_1.1")
        self.lf_dut_serial_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_serial_entry_var)
        self.lf_dut_serial_entry.grid(row=2, column=3)
        self.window_tooltip.bind(self.lf_dut_serial_entry, 'Enter DUT serial number')

        self.lf_dut_upstream_port = tkinter.Label(self.lf_dut_frame, text='Upstream Port')
        self.lf_dut_upstream_port.grid(row=2, column=4)
        self.lf_dut_upstream_port_entry_var = tkinter.StringVar()
        self.lf_dut_upstream_port_entry_var.set("1.1.eth2")
        self.lf_dut_upstream_port_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_upstream_port_entry_var)
        self.lf_dut_upstream_port_entry.grid(row=2, column=5)
        self.window_tooltip.bind(self.lf_dut_upstream_port_entry, 'Enter DUT upstream port example: 1.1.eth2')

        # third row
        self.lf_dut_upstream_alias = tkinter.Label(self.lf_dut_frame, text="Upstream Alias")
        self.lf_dut_upstream_alias.grid(row=3, column=0)
        self.lf_dut_upstream_alias_entry_var = tkinter.StringVar()
        self.lf_dut_upstream_alias_entry_var.set("eth2")
        self.lf_dut_upstream_alias_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_upstream_alias_entry_var)
        self.lf_dut_upstream_alias_entry.grid(row=3, column=1)
        self.window_tooltip.bind(self.lf_dut_upstream_alias_entry, 'Enter dut upstream port alias example: eth2')

        self.lf_dut_db = tkinter.Label(self.lf_dut_frame, text="DUT Database")
        self.lf_dut_db.grid(row=3, column=2)
        self.lf_dut_db_entry_var = tkinter.StringVar()
        self.lf_dut_db_entry_var.set("DUT_DB")
        self.lf_dut_db_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_db_entry_var)
        self.lf_dut_db_entry.grid(row=3, column=3)
        self.window_tooltip.bind(self.lf_dut_db_entry, 'Enter SQLite Database for DUT this superseeds DB entered for LANforge Rig information')

        self.lf_dut_file = tkinter.Label(self.lf_dut_frame, text='json file')
        self.lf_dut_file.grid(row=3, column=4)
        self.lf_dut_file_entry_var = tkinter.StringVar()
        self.lf_dut_file_entry_var.set("ct_dut.json")
        self.lf_dut_file_entry = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_dut_file_entry_var)
        self.lf_dut_file_entry.grid(row=3, column=5)
        dut_file_tool_tip_text = "Specify directory in 'json file' entry or will create \n In Current Working Directory: {}".format(self.current_working_directory)
        self.window_tooltip.bind(self.lf_dut_file_entry, dut_file_tool_tip_text)

        # forth row
        self.use_idx_entry_var_dict = {}
        self.use_idx_var_dict = {}
        self.use_idx_check_dict = {}

        self.lf_idx_ssid_dict = {}
        self.lf_idx_ssid_entry_var_dict = {}
        self.lf_idx_ssid_entry_dict = {}

        self.lf_idx_ssid_pw_dict = {}
        self.lf_idx_ssid_pw_entry_var_dict = {}
        self.lf_idx_ssid_pw_entry_dict = {}

        self.lf_idx_bssid_dict = {}
        self.lf_idx_bssid_entry_var_dict = {}
        self.lf_idx_bssid_entry_dict = {}

        self.lf_idx_security_dict = {}
        self.lf_idx_security_entry_var_dict = {}
        self.lf_idx_security_entry_dict = {}

        self.lf_radio_label_dict = {}

        self.lf_idx_type_dict = {}
        self.lf_idx_type_list = ["", "2g", "5g", "6g"]

        # Dut Information
        dut_row = 6

        self.lf_idx_ssid = tkinter.Label(self.lf_dut_frame, text='SSID')
        self.lf_idx_ssid.grid(row=dut_row, column=1)

        self.lf_idx_ssid_pw = tkinter.Label(self.lf_dut_frame, text='SSID Password')
        self.lf_idx_ssid_pw.grid(row=dut_row, column=2)

        self.lf_idx_bssid = tkinter.Label(self.lf_dut_frame, text='BSSID')
        self.lf_idx_bssid.grid(row=dut_row, column=3)

        self.lf_idx_security = tkinter.Label(self.lf_dut_frame, text='security')
        self.lf_idx_security.grid(row=dut_row, column=4)

        # self.lf_idx_mode = tkinter.Label(self.lf_dut_frame, text='mode')
        # self.lf_idx_mode.grid(row=dut_row, column= 5)

        self.lf_dut_last_row = 0

        # TODO have ability to create multiple strings
        self.lf_idx_upper_range = 4
        for idx in range(0, self.lf_idx_upper_range):

            self.use_idx_entry_var_dict[idx] = tkinter.StringVar(value="Use")
            # self.use_idx_entry_var_dict[idx].set("Use")
            self.use_idx_var_dict[idx] = self.use_idx_entry_var_dict[idx]
            use_idx_check = tkinter.Checkbutton(self.lf_dut_frame, text="Use Index", variable=self.use_idx_entry_var_dict[idx],
                                                onvalue="Use", offvalue="Do Not Use")
            use_idx_check.grid(row=idx + dut_row + 1, column=0)

            self.lf_idx_ssid_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_ssid_entry_var_dict[idx].set("ssid")
            self.lf_idx_ssid_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_idx_ssid_entry_var_dict[idx])
            self.lf_idx_ssid_entry_dict[idx].grid(row=idx + dut_row + 1, column=1)
            self.window_tooltip.bind(self.lf_idx_ssid_entry_dict[idx], 'Enter SSID')

            self.lf_idx_ssid_pw_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_ssid_pw_entry_var_dict[idx].set("ssid_pw")
            self.lf_idx_ssid_pw_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_idx_ssid_pw_entry_var_dict[idx])
            self.lf_idx_ssid_pw_entry_dict[idx].grid(row=idx + dut_row + 1, column=2)
            self.window_tooltip.bind(self.lf_idx_ssid_pw_entry_dict[idx], 'Enter SSID Password')

            self.lf_idx_bssid_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_bssid_entry_var_dict[idx].set("00:00:00:00:00:00")
            self.lf_idx_bssid_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_idx_bssid_entry_var_dict[idx])
            self.lf_idx_bssid_entry_dict[idx].grid(row=idx + dut_row + 1, column=3)
            self.window_tooltip.bind(self.lf_idx_bssid_entry_dict[idx], 'Enter BSSID')

            self.lf_idx_security_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_security_entry_var_dict[idx].set("wpa2")
            self.lf_idx_security_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable=self.lf_idx_security_entry_var_dict[idx])
            self.lf_idx_security_entry_dict[idx].grid(row=idx + dut_row + 1, column=4)
            self.window_tooltip.bind(self.lf_idx_security_entry_dict[idx], 'Enter security example: wpa2')

            radio_text = "Radio-{num}".format(num=idx + 1)
            self.lf_radio_label_dict[idx] = tkinter.Label(self.lf_dut_frame, text=radio_text)
            self.lf_radio_label_dict[idx].grid(row=idx + dut_row + 1, column=5)

            self.lf_dut_last_row = idx + dut_row + 1

        self.lf_radio_2g = tkinter.Label(self.lf_dut_frame, text='Radio 2g')
        self.lf_radio_2g.grid(row=self.lf_dut_last_row + 1, column=0)
        self.lf_radio_2g_combobox = ttk.Combobox(self.lf_dut_frame, values=["<Custom>", "Radio-1", "Radio-2", "Radio-3", "Radio-4"])
        self.lf_radio_2g_combobox.current(1)
        self.lf_radio_2g_combobox.grid(row=self.lf_dut_last_row + 1, column=1)
        self.window_tooltip.bind(self.lf_radio_2g_combobox, '''Select the Radio to be used by 2g
                           Note the syntax is Radio-X for chamberview tests''')

        self.lf_radio_5g = tkinter.Label(self.lf_dut_frame, text='Radio 5g')
        self.lf_radio_5g.grid(row=self.lf_dut_last_row + 1, column=2)
        self.lf_radio_5g_combobox = ttk.Combobox(self.lf_dut_frame, values=["<Custom>", "Radio-1", "Radio-2", "Radio-3", "Radio-4"])
        self.lf_radio_5g_combobox.current(2)
        self.lf_radio_5g_combobox.grid(row=self.lf_dut_last_row + 1, column=3)
        self.window_tooltip.bind(self.lf_radio_5g_combobox, '''Select the Radio to be used by 5g
                           Note the syntax is Radio-X for chamberview tests''')

        self.lf_radio_6g = tkinter.Label(self.lf_dut_frame, text='Radio 6g')
        self.lf_radio_6g.grid(row=self.lf_dut_last_row + 1, column=4)
        self.lf_radio_6g_combobox = ttk.Combobox(self.lf_dut_frame, values=["<Custom>", "Radio-1", "Radio-2", "Radio-3", "Radio-4"])
        self.lf_radio_6g_combobox.current(3)
        self.lf_radio_6g_combobox.grid(row=self.lf_dut_last_row + 1, column=5)
        self.window_tooltip.bind(self.lf_radio_6g_combobox, '''Select the Radio to be used by 6g
                           Note the syntax is Radio-X for chamberview tests''')

        self.lf_dut_save = ttk.Button(self.lf_dut_frame, text='Create DUT Json', command=self.create_dut_json)
        self.lf_dut_save.grid(row=self.lf_dut_last_row + 2, column=0, sticky="news", padx=20, pady=10)
        dut_tool_tip_text = "Specify directory in 'json file' entry or will create \n In Current Working Directory: {}".format(self.current_working_directory)
        self.window_tooltip.bind(self.lf_dut_save, dut_tool_tip_text)

        # Max Stations
        for widget in self.lf_dut_frame.winfo_children():
            widget.grid_configure(padx=5, pady=5)

        # -----------------------------------------------------------------------------------
        #
        #  END Create DUT json
        #
        # ------------------------------------------------------------------------------------

    def create_dut_json(self):

        for idx in range(0, self.lf_idx_upper_range):

            self.use_idx_entry_var_dict[idx].get()
            self.lf_idx_ssid_entry_var_dict[idx].get()
            self.lf_idx_ssid_pw_entry_var_dict[idx].get()
            self.lf_idx_bssid_entry_var_dict[idx].get()
            self.lf_idx_security_entry_var_dict[idx].get()

        dut_json = lf_dut_json.lf_create_dut_json(
            _file=self.lf_dut_file_entry_var.get(),
            _dut_name=self.lf_dut_name_entry_var.get(),
            _dut_hw=self.lf_dut_hw_ver_entry_var.get(),
            _dut_sw=self.lf_dut_sw_ver_entry_var.get(),
            _dut_model=self.lf_dut_model_entry_var.get(),
            _dut_serial=self.lf_dut_serial_entry_var.get(),
            _use_idx_entry_var_dict=self.use_idx_entry_var_dict,
            _lf_idx_ssid_entry_var_dict=self.lf_idx_ssid_entry_var_dict,
            _lf_idx_ssid_pw_entry_var_dict=self.lf_idx_ssid_pw_entry_var_dict,
            _lf_idx_bssid_entry_var_dict=self.lf_idx_bssid_entry_var_dict,
            _lf_idx_security_entry_var_dict=self.lf_idx_security_entry_var_dict,
            _dut_upstream_port=self.lf_dut_upstream_port_entry_var.get(),
            _dut_upstream_alias=self.lf_dut_upstream_alias_entry_var.get(),
            _dut_database=self.lf_dut_db_entry_var.get()
        )

        dut_json.create()
        dut_dir = dut_json.get_dir()
        dut_file = dut_json.get_file()
        # tkinter.messagebox.showinfo(title="success", message= self.lf_dut_file_entry_var.get() + " created")
        tkinter.messagebox.showinfo(title="success", message=dut_dir + "/" + dut_file + " created")
