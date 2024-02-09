#!/usr/bin/python3

import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import requests
import importlib
import sys
import logging
import argparse

try:
    import Pmw
except:
    print("Pmw module needed, Please do: pip install Pmw ")
    exit(1)



if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

lf_rig_json = importlib.import_module("lf_create_rig_json")
lf_dut_json = importlib.import_module("lf_create_dut_json")
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
                radio_count = 8):
        
        self.radio_count = radio_count

        self.window = tkinter.Tk()
        self.window.title("LANforge Test Json Generator")

        self.window_tooltip = Pmw.Balloon(self.window)

        # tool tip
        # https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
        # https://stackoverflow.com/questions/63681382/how-to-add-hover-feature-for-text-description-on-a-tkinter-button
        # tool tips
        Pmw.initialise(self.window)

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
        
        self.tabControl.add(self.rig_tab, text = 'LANforge')
        self.tabControl.add(self.dut_tab, text = 'Device Under Test')
        self.tabControl.add(self.wc_tab, text = 'Wifi Capacity')
        self.tabControl.add(self.dp_rvr_tab, text = 'Data Plane , RvR')
        # self.tabControl.add(self.ap_auto_tab, text = 'AP Auto')
        # self.tabControl.add(self.functional_tab, text = 'Functional Tests')

        # self.tabControl.add(self.practice_tab, text = 'Practice') # Please Do not Delete.
        self.tabControl.pack(expand = 1, fill ="both")

        self.file_2g = ""
        self.file_5g = ""
        self.file_6g = ""

        #-----------------------------------------------------------------------------------
        #
        #  Create Rig Json
        #
        #------------------------------------------------------------------------------------

        self.lf_rig_tab_frame = tkinter.Frame(self.rig_tab)
        self.lf_rig_tab_frame.pack()


        # lanforge Information for json
        self.lf_rig_frame = tkinter.LabelFrame(self.lf_rig_tab_frame, text="LANforge Rig Information")
        self.lf_rig_frame.grid(row= 0, column= 0, sticky="news", padx=20, pady=10)

        self.lf_mgr = tkinter.Label(self.lf_rig_frame, text="IP")
        self.lf_mgr.grid(row=1, column=0)
        self.lf_mgr_entry_var = tkinter.StringVar()
        # self.lf_mgr_entry_var.set("192.168.100.116")
        self.lf_mgr_entry_var.set("")
        self.lf_mgr_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_mgr_entry_var)
        self.lf_mgr_entry.grid(row=1, column=1)
        self.window_tooltip.bind(self.lf_mgr_entry, 'Enter LANforge Manager IP')
        
        self.lf_mgr_port = tkinter.Label(self.lf_rig_frame, text='PORT')
        self.lf_mgr_port.grid(row= 1, column= 2)
        self.lf_mgr_port_entry_var = tkinter.StringVar()
        self.lf_mgr_port_entry_var.set("8080")
        self.lf_mgr_port_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_mgr_port_entry_var)
        self.lf_mgr_port_entry.grid(row=1, column=3)
        self.window_tooltip.bind(self.lf_mgr_port_entry, 'Enter LANforge Manager Port')

        self.lf_user = tkinter.Label(self.lf_rig_frame, text="USER")
        self.lf_user.grid(row=1, column=4)
        self.lf_user_entry_var = tkinter.StringVar()
        self.lf_user_entry_var.set("lanforge")
        self.lf_user_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_user_entry_var)
        self.lf_user_entry.grid(row=1, column=5)
        self.window_tooltip.bind(self.lf_user_entry, 'Enter Lanforge Username')

        self.lf_passwd = tkinter.Label(self.lf_rig_frame, text='PASSWORD')
        self.lf_passwd.grid(row= 1, column= 6)
        self.lf_passwd_entry_var = tkinter.StringVar()
        self.lf_passwd_entry_var.set("lanforge")
        self.lf_passwd_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_passwd_entry_var)
        self.lf_passwd_entry.grid(row=1, column=7)
        self.window_tooltip.bind(self.lf_passwd_entry, 'Enter Lanforge Password')

        # second row
        self.lf_test_rig = tkinter.Label(self.lf_rig_frame, text="TEST RIG")
        self.lf_test_rig.grid(row=2, column=0)
        self.lf_test_rig_entry_var = tkinter.StringVar()
        self.lf_test_rig_entry_var.set("LANforge")
        self.lf_test_rig_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_test_rig_entry_var)
        self.lf_test_rig_entry.grid(row=2, column=1)
        self.window_tooltip.bind(self.lf_test_rig_entry, 'Enter Test RIG NAME')
        
        self.lf_test_bed = tkinter.Label(self.lf_rig_frame, text='TEST BED')
        self.lf_test_bed.grid(row= 2, column= 2)
        self.lf_test_bed_entry_var = tkinter.StringVar()
        self.lf_test_bed_entry_var.set("TESTBED")
        self.lf_test_bed_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_test_bed_entry_var)
        self.lf_test_bed_entry.grid(row=2, column=3)
        self.window_tooltip.bind(self.lf_test_bed_entry, 'Enter Test Bed Name')

        self.lf_test_server = tkinter.Label(self.lf_rig_frame, text="TEST SERVER")
        self.lf_test_server.grid(row=2, column=4)
        self.lf_test_server_entry_var = tkinter.StringVar()
        self.lf_test_server_entry_var.set("localhost")
        self.lf_test_server_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_test_server_entry_var)
        self.lf_test_server_entry.grid(row=2, column=5)
        self.window_tooltip.bind(self.lf_test_server_entry, 'Enter ip of test reports server can be lanforge ip, default set to lanforge ip input')


        # third row
        self.lf_test_db = tkinter.Label(self.lf_rig_frame, text="SQLite Database")
        self.lf_test_db.grid(row=3, column=0)
        self.lf_test_db_entry_var = tkinter.StringVar()
        self.lf_test_db_entry_var.set("LANforge")
        self.lf_test_db_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_test_db_entry_var)
        self.lf_test_db_entry.grid(row=3, column=1)
        self.window_tooltip.bind(self.lf_test_db_entry, 'Enter SQLite Database')
        
        self.lf_upstream_port = tkinter.Label(self.lf_rig_frame, text='UPSTREAM PORT')
        self.lf_upstream_port.grid(row= 3, column= 2)
        self.lf_upstream_port_entry_var = tkinter.StringVar()
        self.lf_upstream_port_entry_var.set("1.1.eth2")
        self.lf_upstream_port_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_upstream_port_entry_var)
        self.lf_upstream_port_entry.grid(row=3, column=3)
        self.window_tooltip.bind(self.lf_upstream_port_entry, 'Enter Upstream Port')


        self.lf_test_timeout = tkinter.Label(self.lf_rig_frame, text="TEST TIMEOUT")
        self.lf_test_timeout.grid(row=3, column=4)
        self.lf_test_timeout_entry_var = tkinter.StringVar()
        self.lf_test_timeout_entry_var.set("600")
        self.lf_test_timeout_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_test_timeout_entry_var)
        self.lf_test_timeout_entry.grid(row=3, column=5)
        self.window_tooltip.bind(self.lf_test_timeout_entry, 'Enter test timeout in seconds')


        self.lf_file = tkinter.Label(self.lf_rig_frame, text='json file')
        self.lf_file.grid(row= 3, column= 6)
        self.lf_rig_file_entry_var = tkinter.StringVar()
        self.lf_rig_file_entry_var.set("ct_auto_gen_rig.json")
        self.lf_file_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_rig_file_entry_var)
        self.lf_file_entry.grid(row=3, column=7)
        self.window_tooltip.bind(self.lf_file_entry, 'Enter rig json file name and/or path and rig json file name  /home/user/ct_auto_gen_rig.json')
        
        # forth row #TODO can the ATTEN values be read
        self.lf_atten_1 = tkinter.Label(self.lf_rig_frame, text="Atten 1")
        self.lf_atten_1.grid(row=4, column=0)
        self.lf_atten_1_entry_var = tkinter.StringVar()
        self.lf_atten_1_entry_var.set("1.1.3360")
        self.lf_atten_1_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_atten_1_entry_var)
        self.lf_atten_1_entry.grid(row=4, column=1)
        self.window_tooltip.bind(self.lf_atten_1_entry, 'LANforge Atten 1 example 1.1.3360, for test rig uses ATTENUATOR_1')
        
        self.lf_atten_2 = tkinter.Label(self.lf_rig_frame, text="Atten 2")
        self.lf_atten_2.grid(row=4, column=2)
        self.lf_atten_2_entry_var = tkinter.StringVar()
        self.lf_atten_2_entry_var.set("")
        self.lf_atten_2_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_atten_2_entry_var)
        self.lf_atten_2_entry.grid(row=4, column=3)
        self.window_tooltip.bind(self.lf_atten_2_entry, 'LANforge Atten 2 example 1.1.3360, for the test rig json uses ATTENUATOR_2')

        self.lf_atten_3 = tkinter.Label(self.lf_rig_frame, text="Atten 3")
        self.lf_atten_3.grid(row=4, column=4)
        self.lf_atten_3_entry_var = tkinter.StringVar()
        self.lf_atten_3_entry_var.set("")
        self.lf_atten_3_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_atten_3_entry_var)
        self.lf_atten_3_entry.grid(row=4, column=5)
        self.window_tooltip.bind(self.lf_atten_3_entry, 'LANforge Atten 3 example 1.1.3360, for the test rig json uses ATTENUATOR_3')

        self.lf_email = tkinter.Label(self.lf_rig_frame, text='Email Results:')
        self.lf_email.grid(row= 5, column= 0)
        self.lf_email_entry_var = tkinter.StringVar()
        self.lf_email_entry_var.set("")
        self.lf_email_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_email_entry_var, width = 80)
        self.lf_email_entry.grid(row= 5, column=1, columnspan=4 )
        self.window_tooltip.bind(self.lf_email_entry, '''Enter emails to receive notification of test results and completion. Comma separated list''')

        self.lf_email_production = tkinter.Label(self.lf_rig_frame, text='Email Results Production:')
        self.lf_email_production.grid(row= 6, column= 0)
        self.lf_email_production_entry_var = tkinter.StringVar()
        self.lf_email_production_entry_var.set("")
        self.lf_email_production_entry = tkinter.Entry(self.lf_rig_frame, textvariable = self.lf_email_production_entry_var, width = 80)
        self.lf_email_production_entry.grid(row= 6, column=1, columnspan=4 )
        self.window_tooltip.bind(self.lf_email_production_entry, '''Enter emails for Production results. Comma separated list''')


        # Max Stations
        for widget in self.lf_rig_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)



        # save = ttk.Button(self.lf_rig_frame, text = 'Create Test Rig Json', command = lambda : messagebox.askyesno('Confirm', 'Do you want to save?'))
        self.lf_rig_save = ttk.Button(self.lf_rig_frame, text = 'Create Test Rig Json', command = self.create_rig_json)
        self.lf_rig_save.grid(row=7, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_rig_save, 'Create Rig Json')


        #-----------------------------------------------------------------------------------
        #
        #  End of Create Rig Json
        #
        #------------------------------------------------------------------------------------




        #-----------------------------------------------------------------------------------
        #
        #  Create DUT json
        #
        #------------------------------------------------------------------------------------

        self.lf_dut_tab_frame = tkinter.Frame(self.dut_tab)
        self.lf_dut_tab_frame.pack()

        # lanforge Information for json
        self.lf_dut_frame = tkinter.LabelFrame(self.lf_dut_tab_frame, text="Device Unter Test (DUT) Information")
        self.lf_dut_frame.grid(row= 0, column= 0, sticky="news", padx=5, pady=5)

        self.lf_dut_name = tkinter.Label(self.lf_dut_frame, text="DUT Name")
        self.lf_dut_name.grid(row=1, column=0)
        self.lf_dut_name_entry_var = tkinter.StringVar()
        self.lf_dut_name_entry_var.set("dut_name")
        self.lf_dut_name_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_name_entry_var)
        self.lf_dut_name_entry.grid(row=1, column=1)
        self.window_tooltip.bind(self.lf_dut_name_entry, 'Enter DUT Name with no spaces')
        
        self.lf_dut_hw_ver = tkinter.Label(self.lf_dut_frame, text='HW Version')
        self.lf_dut_hw_ver.grid(row= 1, column= 2)
        self.lf_dut_hw_ver_entry_var = tkinter.StringVar()
        self.lf_dut_hw_ver_entry_var.set("hw_ver_1.1")
        self.lf_dut_hw_ver_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_hw_ver_entry_var)
        self.lf_dut_hw_ver_entry.grid(row=1, column=3)
        self.window_tooltip.bind(self.lf_dut_hw_ver_entry, 'Enter DUT Hardware Version')

        self.lf_dut_sw_ver = tkinter.Label(self.lf_dut_frame, text="SW Version")
        self.lf_dut_sw_ver.grid(row=1, column=4)
        self.lf_dut_sw_ver_entry_var = tkinter.StringVar()
        self.lf_dut_sw_ver_entry_var.set("sw_ver_1.1")
        self.lf_dut_sw_ver_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_sw_ver_entry_var)
        self.lf_dut_sw_ver_entry.grid(row=1, column=5)
        self.window_tooltip.bind(self.lf_dut_sw_ver_entry, 'Enter DUT Software Version')

        # second row
        self.lf_dut_model = tkinter.Label(self.lf_dut_frame, text='Model')
        self.lf_dut_model.grid(row= 2, column= 0)
        self.lf_dut_model_entry_var = tkinter.StringVar()
        self.lf_dut_model_entry_var.set("dut_model")
        self.lf_dut_model_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_model_entry_var)
        self.lf_dut_model_entry.grid(row=2, column=1)
        self.window_tooltip.bind(self.lf_dut_model_entry, 'Enter DUT Model')

        self.lf_dut_serial_rig = tkinter.Label(self.lf_dut_frame, text="Serial Number")
        self.lf_dut_serial_rig.grid(row=2, column=2)
        self.lf_dut_serial_entry_var = tkinter.StringVar()
        self.lf_dut_serial_entry_var.set("serial_1.1")
        self.lf_dut_serial_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_serial_entry_var)
        self.lf_dut_serial_entry.grid(row=2, column=3)
        self.window_tooltip.bind(self.lf_dut_serial_entry, 'Enter DUT serial number')
        
        self.lf_dut_upstream_port = tkinter.Label(self.lf_dut_frame, text='Upstream Port')
        self.lf_dut_upstream_port.grid(row= 2, column= 4)
        self.lf_dut_upstream_port_entry_var = tkinter.StringVar()
        self.lf_dut_upstream_port_entry_var.set("1.1.eth2")
        self.lf_dut_upstream_port_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_upstream_port_entry_var)
        self.lf_dut_upstream_port_entry.grid(row=2, column=5)
        self.window_tooltip.bind(self.lf_dut_upstream_port_entry, 'Enter DUT upstream port example: 1.1.eth2')

        # third row
        self.lf_dut_upstream_alias = tkinter.Label(self.lf_dut_frame, text="Upstream Alias")
        self.lf_dut_upstream_alias.grid(row=3, column=0)
        self.lf_dut_upstream_alias_entry_var = tkinter.StringVar()
        self.lf_dut_upstream_alias_entry_var.set("eth2")
        self.lf_dut_upstream_alias_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_upstream_alias_entry_var)
        self.lf_dut_upstream_alias_entry.grid(row=3, column=1)
        self.window_tooltip.bind(self.lf_dut_upstream_alias_entry, 'Enter dut upstream port alias example: eth2')

        self.lf_dut_db = tkinter.Label(self.lf_dut_frame, text="DUT Database")
        self.lf_dut_db.grid(row=3, column=2)
        self.lf_dut_db_entry_var = tkinter.StringVar()
        self.lf_dut_db_entry_var.set("DUT_DB")
        self.lf_dut_db_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_db_entry_var)
        self.lf_dut_db_entry.grid(row=3, column=3)
        self.window_tooltip.bind(self.lf_dut_db_entry, 'Enter SQLite Database for DUT this superseeds DB entered for LANforge Rig information')

        self.lf_dut_file = tkinter.Label(self.lf_dut_frame, text='json file')
        self.lf_dut_file.grid(row= 3, column= 4)
        self.lf_dut_file_entry_var = tkinter.StringVar()
        self.lf_dut_file_entry_var.set("ct_dut.json")
        self.lf_dut_file_entry = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_dut_file_entry_var)
        self.lf_dut_file_entry.grid(row=3, column=5)
        self.window_tooltip.bind(self.lf_dut_file_entry, 'Enter dut json file name and/or path and dut json file name  /home/user/ct_dut.json')


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
        self.lf_idx_type_list = ["","2g","5g","6g"]

        # Dut Information
        dut_row = 6

        self.lf_idx_ssid = tkinter.Label(self.lf_dut_frame, text='SSID')
        self.lf_idx_ssid.grid(row=dut_row, column= 1)

        self.lf_idx_ssid_pw = tkinter.Label(self.lf_dut_frame, text='SSID Password')
        self.lf_idx_ssid_pw.grid(row=dut_row, column= 2)

        self.lf_idx_bssid = tkinter.Label(self.lf_dut_frame, text='BSSID')
        self.lf_idx_bssid.grid(row=dut_row, column= 3)

        self.lf_idx_security = tkinter.Label(self.lf_dut_frame, text='security')
        self.lf_idx_security.grid(row=dut_row, column= 4)

        # self.lf_idx_mode = tkinter.Label(self.lf_dut_frame, text='mode')
        # self.lf_idx_mode.grid(row=dut_row, column= 5)
        
        self.lf_dut_last_row = 0

        # TODO have ability to create multiple strings
        self.lf_idx_upper_range = 4
        for idx in range(0,self.lf_idx_upper_range):

            self.use_idx_entry_var_dict[idx] = tkinter.StringVar(value="Use")
            #self.use_idx_entry_var_dict[idx].set("Use")
            self.use_idx_var_dict[idx] = self.use_idx_entry_var_dict[idx]
            use_idx_check = tkinter.Checkbutton(self.lf_dut_frame, text="Use Index", variable=self.use_idx_entry_var_dict[idx],
                                            onvalue="Use", offvalue="Do Not Use")
            use_idx_check.grid(row=idx+dut_row+1, column=0)


            self.lf_idx_ssid_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_ssid_entry_var_dict[idx].set("ssid")
            self.lf_idx_ssid_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_idx_ssid_entry_var_dict[idx])
            self.lf_idx_ssid_entry_dict[idx].grid(row=idx+dut_row+1, column=1)
            self.window_tooltip.bind(self.lf_idx_ssid_entry_dict[idx], 'Enter SSID')

            self.lf_idx_ssid_pw_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_ssid_pw_entry_var_dict[idx].set("ssid_pw")
            self.lf_idx_ssid_pw_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_idx_ssid_pw_entry_var_dict[idx])
            self.lf_idx_ssid_pw_entry_dict[idx].grid(row=idx+dut_row+1, column=2)
            self.window_tooltip.bind(self.lf_idx_ssid_pw_entry_dict[idx], 'Enter SSID Password')

            self.lf_idx_bssid_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_bssid_entry_var_dict[idx].set("00:00:00:00:00:00")
            self.lf_idx_bssid_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_idx_bssid_entry_var_dict[idx])
            self.lf_idx_bssid_entry_dict[idx].grid(row=idx+dut_row+1, column=3)
            self.window_tooltip.bind(self.lf_idx_bssid_entry_dict[idx], 'Enter BSSID')

            self.lf_idx_security_entry_var_dict[idx] = tkinter.StringVar()
            self.lf_idx_security_entry_var_dict[idx].set("wpa2")
            self.lf_idx_security_entry_dict[idx] = tkinter.Entry(self.lf_dut_frame, textvariable = self.lf_idx_security_entry_var_dict[idx])
            self.lf_idx_security_entry_dict[idx].grid(row=idx+dut_row+1, column=4)
            self.window_tooltip.bind(self.lf_idx_security_entry_dict[idx], 'Enter security example: wpa2')

            radio_text = "Radio-{num}".format(num=idx+1)
            self.lf_radio_label_dict[idx] = tkinter.Label(self.lf_dut_frame, text=radio_text)
            self.lf_radio_label_dict[idx].grid(row=idx+dut_row+1, column= 5)


            self.lf_dut_last_row = idx+dut_row+1

        self.lf_radio_2g = tkinter.Label(self.lf_dut_frame, text='Radio 2g')
        self.lf_radio_2g.grid(row= self.lf_dut_last_row+1, column= 0)
        self.lf_radio_2g_combobox = ttk.Combobox(self.lf_dut_frame, values=["<Custom>","Radio-1","Radio-2","Radio-3","Radio-4"])
        self.lf_radio_2g_combobox.current(1)
        self.lf_radio_2g_combobox.grid(row= self.lf_dut_last_row+1, column=1)
        self.window_tooltip.bind(self.lf_radio_2g_combobox, '''Select the Radio to be used by 2g
                            Note the syntax is Radio-X for chamberview tests''')

        self.lf_radio_5g = tkinter.Label(self.lf_dut_frame, text='Radio 5g')
        self.lf_radio_5g.grid(row= self.lf_dut_last_row+1, column= 2)
        self.lf_radio_5g_combobox = ttk.Combobox(self.lf_dut_frame, values=["<Custom>","Radio-1","Radio-2","Radio-3","Radio-4"])
        self.lf_radio_5g_combobox.current(2)
        self.lf_radio_5g_combobox.grid(row= self.lf_dut_last_row+1, column=3)
        self.window_tooltip.bind(self.lf_radio_5g_combobox, '''Select the Radio to be used by 5g  
                            Note the syntax is Radio-X for chamberview tests''')

        self.lf_radio_6g = tkinter.Label(self.lf_dut_frame, text='Radio 6g')
        self.lf_radio_6g.grid(row= self.lf_dut_last_row+1, column= 4)
        self.lf_radio_6g_combobox = ttk.Combobox(self.lf_dut_frame, values=["<Custom>","Radio-1","Radio-2","Radio-3","Radio-4"])
        self.lf_radio_6g_combobox.current(3)
        self.lf_radio_6g_combobox.grid(row= self.lf_dut_last_row+1, column=5)
        self.window_tooltip.bind(self.lf_radio_6g_combobox, '''Select the Radio to be used by 6g  
                            Note the syntax is Radio-X for chamberview tests''')


        self.lf_dut_save = ttk.Button(self.lf_dut_frame, text = 'Create DUT Json', command = self.create_dut_json)
        self.lf_dut_save.grid(row=self.lf_dut_last_row+2, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_dut_save, 'Create DUT Json')


                
        # Max Stations
        for widget in self.lf_dut_frame.winfo_children():
             widget.grid_configure(padx=5, pady=5)


            


        #-----------------------------------------------------------------------------------
        #
        #  END Create DUT json
        #
        #------------------------------------------------------------------------------------


        #-----------------------------------------------------------------------------------
        #
        #  Create Radios
        #
        #------------------------------------------------------------------------------------

        # create then either pack, place, grid
        self.radio_frame = tkinter.Frame(self.rig_tab)
        self.radio_frame.pack()


        # lanforge Radio Information
        self.lf_radio_frame = tkinter.LabelFrame(self.radio_frame, text="Radio Information")
        self.lf_radio_frame.grid(row= 1, column= 0, sticky="news", padx=20, pady=10)

        # TO DO have the shelf and resource so there may be a realm
        self.radio_status_label = tkinter.Label(self.lf_radio_frame, text="Radio Status")
        self.radio_status_label.grid(row=1, column=0)

        self.radio_label = tkinter.Label(self.lf_radio_frame, text="Radio")
        self.radio_label.grid(row=1, column=1)

        self.radio_type_label = tkinter.Label(self.lf_radio_frame, text="Radio Type")
        self.radio_type_label.grid(row=1, column=2)

        self.radio_type_label = tkinter.Label(self.lf_radio_frame, text="Radio Model")
        self.radio_type_label.grid(row=1, column=3)

        self.radio_type_label = tkinter.Label(self.lf_radio_frame, text="Radio Max Sta")
        self.radio_type_label.grid(row=1, column=4)

        self.radio_type_label = tkinter.Label(self.lf_radio_frame, text="Radio Batch")
        self.radio_type_label.grid(row=1, column=5)

        self.radio_2g_label = tkinter.Label(self.lf_radio_frame, text="2g")
        self.radio_2g_label.grid(row=1, column=6)

        self.radio_5g_label = tkinter.Label(self.lf_radio_frame, text="5g")
        self.radio_5g_label.grid(row=1, column=7)

        self.radio_6g_label = tkinter.Label(self.lf_radio_frame, text="6g")
        self.radio_6g_label.grid(row=1, column=8)


        # Capabilities
        # https://stackoverflow.com/questions/28736028/python-tkinter-reference-in-comboboxes-created-in-for-loop
        # radio_type_list Not used read from the LANforge
        self.radio_type_list = ["","AX200_abgn_AX","AX210_abgn_AX","MTK7915_abgn_AX","MTK7921_abgn_AX","ATH9K_abgn","ATH10K_bgn_AC","ATH10K_an_AC"]


        self.use_radio_var_dict = {}
        self.radio_dict = {}
        self.radio_type_dict = {}
        self.radio_model_dict = {}
        self.radio_max_sta_dict = {}
        self.radio_batch_dict = {}
        self.radio_count = 0
        self.use_radio_2g_var_dict = {}
        self.use_radio_5g_var_dict = {}
        self.use_radio_6g_var_dict = {}

        # helpers
        self.suite_radios_2g = ""
        self.suite_radios_5g = ""
        self.suite_radios_6g = ""

        self.suite_test_name_2g_dict = {}
        self.suite_test_name_5g_dict = {}
        self.suite_test_name_6g_dict = {}

        for radio in range(0,self.max_radios):


            use_radio_var = tkinter.StringVar(value="Do Not Use")
            self.use_radio_var_dict[radio] = use_radio_var
            use_radio_check = tkinter.Checkbutton(self.lf_radio_frame, text="Use Radio", variable=self.use_radio_var_dict[radio],
                                            onvalue="Use", offvalue="Do Not Use")
            use_radio_check.grid(row=radio+2, column=0)

            radio_entry_var = tkinter.StringVar()
            self.radio_dict[radio] = radio_entry_var
            radio_entry_var.set("")
            radio_entry  = tkinter.Entry(self.lf_radio_frame, textvariable = self.radio_dict[radio])
            radio_entry.grid(row=radio+2, column= 1)
            self.window_tooltip.bind(radio_entry, 'Enter LANforge radio shelf.resource.radio, example: 1.1.wiphy0')

            radio_type_entry_var = tkinter.StringVar()
            self.radio_type_dict[radio] = radio_type_entry_var
            radio_type_entry_var.set("")
            radio_type_entry  = tkinter.Entry(self.lf_radio_frame, textvariable = self.radio_type_dict[radio])
            radio_type_entry.grid(row=radio+2, column= 2)
            self.window_tooltip.bind(radio_type_entry, 'Enter Radio Type, example: 802.11abgn-AX')


            radio_model_entry_var = tkinter.StringVar()
            self.radio_model_dict[radio] = radio_model_entry_var
            radio_model_entry_var.set("")
            radio_model_entry  = tkinter.Entry(self.lf_radio_frame, textvariable = self.radio_model_dict[radio])
            radio_model_entry.grid(row=radio+2, column= 3)
            self.window_tooltip.bind(radio_model_entry, 'Enter Radio Model Type, example: AX210')


            radio_max_sta_entry_var = tkinter.StringVar()
            self.radio_max_sta_dict[radio] = radio_max_sta_entry_var
            radio_max_sta_entry_var.set("")
            radio_max_sta_entry  = tkinter.Entry(self.lf_radio_frame, textvariable = self.radio_max_sta_dict[radio])
            radio_max_sta_entry.grid(row=radio+2, column= 4)
            self.window_tooltip.bind(radio_max_sta_entry, 'Enter Radio Maximum Stations supported')

            radio_batch_entry_var = tkinter.StringVar()
            self.radio_batch_dict[radio] = radio_batch_entry_var
            radio_batch_entry_var.set("")
            radio_batch_entry  = tkinter.Entry(self.lf_radio_frame, textvariable = self.radio_batch_dict[radio])
            radio_batch_entry.grid(row=radio+2, column= 5)

            use_radio_2g_var = tkinter.StringVar(value="Do Not Use")
            self.use_radio_2g_var_dict[radio] = use_radio_2g_var
            use_radio_2g_check = tkinter.Checkbutton(self.lf_radio_frame, text="2g", variable=self.use_radio_2g_var_dict[radio],
                                            onvalue="Use", offvalue="Do Not Use")
            use_radio_2g_check.grid(row=radio+2, column=6)
            self.window_tooltip.bind(use_radio_2g_check, '''Read Radio info will select 2g band as capability if applicable
The check box may be selected to allow the band to be included in the test json
or deselect to remove from the test json''')


            use_radio_5g_var = tkinter.StringVar(value="Do Not Use")
            self.use_radio_5g_var_dict[radio] = use_radio_5g_var
            use_radio_5g_check = tkinter.Checkbutton(self.lf_radio_frame, text="5g", variable=self.use_radio_5g_var_dict[radio],
                                            onvalue="Use", offvalue="Do Not Use")
            use_radio_5g_check.grid(row=radio+2, column=7)
            self.window_tooltip.bind(use_radio_5g_check, '''Read Radio info will select 5g band as capability if applicable
The check box may be selected to allow the band to be included in the test json
or deselect to remove from the test json''')


            use_radio_6g_var = tkinter.StringVar(value="Do Not Use")
            self.use_radio_6g_var_dict[radio] = use_radio_6g_var
            use_radio_6g_check = tkinter.Checkbutton(self.lf_radio_frame, text="6g", variable=self.use_radio_6g_var_dict[radio],
                                            onvalue="Use", offvalue="Do Not Use")
            use_radio_6g_check.grid(row=radio+2, column=8)
            self.window_tooltip.bind(use_radio_6g_check, '''Read Radio info will select 6g band as capability if applicable
The check box may be selected to allow the band to be included in the test json
or deselect to remove from the test json''')



        self.lf_read_radio = ttk.Button(self.lf_radio_frame, text = 'Read Radio Info', command = self.get_lanforge_radio_information)
        self.lf_read_radio.grid(row=radio+3, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_read_radio, 'Read LANforge Radio Information')

        self.lf_apply_radio = ttk.Button(self.lf_radio_frame, text = 'Apply Radio Info', command = self.apply_lanforge_radio_information)
        self.lf_apply_radio.grid(row=radio+3, column=1, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_apply_radio, 'Apply Radio Information based on updates')

        self.lf_clear_radio = ttk.Button(self.lf_radio_frame, text = 'Clear Radio Info', command = self.clear_lanforge_radio_information)
        self.lf_clear_radio.grid(row=radio+3, column=2, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_clear_radio, 'Clear Radio Information')



        # Max Stations
        for widget in self.lf_radio_frame.winfo_children():
            widget.grid_configure(padx=5, pady=5)




        #-----------------------------------------------------------------------------------
        #
        #  End of Create Radios
        #
        #------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------------
        #
        #  Create Wifi Capacity
        #
        #------------------------------------------------------------------------------------
        self.lf_wc_tab_frame = tkinter.Frame(self.wc_tab)
        self.lf_wc_tab_frame.pack()


        # lanforge Information for json
        self.lf_wc_frame = tkinter.LabelFrame(self.lf_wc_tab_frame, text="Wifi Capacity")
        self.lf_wc_frame.grid(row= 0, column= 0, sticky="news", padx=20, pady=10)

        self.lf_wc_2g_file = tkinter.Label(self.lf_wc_frame, text='2g json file')
        self.lf_wc_2g_file.grid(row= 1, column= 0)
        self.lf_wc_2g_file_entry_var = tkinter.StringVar()
        self.lf_wc_2g_file_entry_var.set("")
        self.lf_wc_2g_file_entry = tkinter.Entry(self.lf_wc_frame, textvariable = self.lf_wc_2g_file_entry_var, width = 48)
        self.lf_wc_2g_file_entry.grid(row= 1, column=1, columnspan = 2)
        self.window_tooltip.bind(self.lf_wc_2g_file_entry, '''Auto generated name for Wifi Capacity Test Suite''')

        self.lf_wc_2g_dir = tkinter.Label(self.lf_wc_frame, text='2g json dir')
        self.lf_wc_2g_dir.grid(row= 1, column= 3)
        self.lf_wc_2g_dir_entry_var = tkinter.StringVar()
        self.lf_wc_2g_dir_entry_var.set("")
        self.lf_wc_2g_dir_entry = tkinter.Entry(self.lf_wc_frame, textvariable = self.lf_wc_2g_dir_entry_var, width = 48)
        self.lf_wc_2g_dir_entry.grid(row= 1, column=4, columnspan = 2)
        self.window_tooltip.bind(self.lf_wc_2g_dir_entry, '''Directory for Wifi Capacity Test Suite, if blank will show dir created in''')

        self.lf_wc_5g_file = tkinter.Label(self.lf_wc_frame, text='5g json file')
        self.lf_wc_5g_file.grid(row= 2, column= 0)
        self.lf_wc_5g_file_entry_var = tkinter.StringVar()
        self.lf_wc_5g_file_entry_var.set("")
        self.lf_wc_5g_file_entry = tkinter.Entry(self.lf_wc_frame, textvariable = self.lf_wc_5g_file_entry_var, width = 48)
        self.lf_wc_5g_file_entry.grid(row= 2, column=1, columnspan = 2)
        self.window_tooltip.bind(self.lf_wc_5g_file_entry, '''Auto generated name for Wifi Capacity Test Suite''')

        self.lf_wc_5g_dir = tkinter.Label(self.lf_wc_frame, text='5g json dir')
        self.lf_wc_5g_dir.grid(row= 2, column= 3)
        self.lf_wc_5g_dir_entry_var = tkinter.StringVar()
        self.lf_wc_5g_dir_entry_var.set("")
        self.lf_wc_5g_dir_entry = tkinter.Entry(self.lf_wc_frame, textvariable = self.lf_wc_5g_dir_entry_var, width = 48)
        self.lf_wc_5g_dir_entry.grid(row= 2, column=4, columnspan = 2)
        self.window_tooltip.bind(self.lf_wc_5g_dir_entry, '''Directory for Wifi Capacity Test Suite, if blank will show dir created in''')

        self.lf_wc_6g_file = tkinter.Label(self.lf_wc_frame, text='6g json file')
        self.lf_wc_6g_file.grid(row= 3, column= 0)
        self.lf_wc_6g_file_entry_var = tkinter.StringVar()
        self.lf_wc_6g_file_entry_var.set("")
        self.lf_wc_6g_file_entry = tkinter.Entry(self.lf_wc_frame, textvariable = self.lf_wc_6g_file_entry_var, width = 48)
        self.lf_wc_6g_file_entry.grid(row= 3, column=1, columnspan = 2)
        self.window_tooltip.bind(self.lf_wc_6g_file_entry, '''Auto generated name for Wifi Capacity Test Suite''')

        self.lf_wc_6g_dir = tkinter.Label(self.lf_wc_frame, text='6g json dir')
        self.lf_wc_6g_dir.grid(row= 3, column= 3)
        self.lf_wc_6g_dir_entry_var = tkinter.StringVar()
        self.lf_wc_6g_dir_entry_var.set("")
        self.lf_wc_6g_dir_entry = tkinter.Entry(self.lf_wc_frame, textvariable = self.lf_wc_6g_dir_entry_var, width = 48)
        self.lf_wc_6g_dir_entry.grid(row= 3, column=4, columnspan = 2)
        self.window_tooltip.bind(self.lf_wc_6g_file_entry, '''Directory for Wifi Capacity Test Suite, if blank will show dir created in''')

        self.lf_wc_duration = tkinter.Label(self.lf_wc_frame, text='test duration (ms)')
        self.lf_wc_duration.grid(row= 4, column= 0)
        self.lf_wc_duration_combobox = ttk.Combobox(self.lf_wc_frame, values=["<Custom>","5000 (5 sec)","10000 (10 sec)","15000 (15 sec)","20000 (20 sec)","30000 (30 sec)","60000 (1 min)","300000 (5min)"])
        self.lf_wc_duration_combobox.current(3)
        self.lf_wc_duration_combobox.grid(row= 4, column=1)
        self.window_tooltip.bind(self.lf_wc_duration_combobox, '''Select the duration of each iteration  ''')

        self.lf_wc_number_dut_indexes = tkinter.Label(self.lf_wc_frame, text="Number DUT Indexes")
        self.lf_wc_number_dut_indexes.grid(row=4, column=2)
        self.lf_wc_number_dut_indexes_combobox = ttk.Combobox(self.lf_wc_frame, values=["1","2","3","4"])
        self.lf_wc_number_dut_indexes_combobox.current(2)
        self.lf_wc_number_dut_indexes_combobox.grid(row= 4, column=3)
        self.window_tooltip.bind(self.lf_wc_number_dut_indexes_combobox, '''Number of DUT indexes valid in the DUT json''')

        self.lf_wc_sta_profile = tkinter.Label(self.lf_wc_frame, text="Station Profile")
        self.lf_wc_sta_profile.grid(row=5, column=0)
        self.lf_wc_sta_profile_combobox = ttk.Combobox(self.lf_wc_frame, values=["STA-AUTO","STA-AC","STA-AX","STA-AX-160","STA-BE","STA-abg","STA-n"])
        self.lf_wc_sta_profile_combobox.current(0)
        self.lf_wc_sta_profile_combobox.grid(row= 5, column=1)
        self.window_tooltip.bind(self.lf_wc_sta_profile_combobox, '''Station profile,  when using stations greater then 1 , 
MU MIMO will perform poor for AX radios for virtual stations greater then one, use STA-AC''')

        self.lf_wc_dl_rate = tkinter.Label(self.lf_wc_frame, text="dl_rate")
        self.lf_wc_dl_rate.grid(row=6, column=0)
        self.lf_wc_dl_rate_combobox = ttk.Combobox(self.lf_wc_frame, values=["custom>","0","9.6K","56K","128K","256K","384K","768K","1M",
            "1.544M","2M","6M","10M","30M","37M","44.736M","100M","152M","155.52M","304M","622.08M","1G","2.488G","4.97664G",
            "5G","9.94328G","10G","20G","25G","40G","50G","100G"])
        self.lf_wc_dl_rate_combobox.current(8)
        self.lf_wc_dl_rate_combobox.grid(row= 6, column=1)
        self.window_tooltip.bind(self.lf_wc_dl_rate_combobox, '''Download Rate enter number or number followed by K M or G''')

        self.lf_wc_ul_rate = tkinter.Label(self.lf_wc_frame, text="ul_rate")
        self.lf_wc_ul_rate.grid(row=6, column=2)
        self.lf_wc_ul_rate_combobox = ttk.Combobox(self.lf_wc_frame, values=["custom>","0","9.6K","56K","128K","256K","384K","768K","1M",
            "1.544M","2M","6M","10M","30M","37M","44.736M","100M","152M","155.52M","304M","622.08M","1G","2.488G","4.97664G",
            "5G","9.94328G","10G","20G","25G","40G","50G","100G"])
        self.lf_wc_ul_rate_combobox.current(8)
        self.lf_wc_ul_rate_combobox.grid(row= 6, column=3)
        self.window_tooltip.bind(self.lf_wc_ul_rate_combobox, '''Upload Rate enter number or number followed by K M or G''')

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


        self.lf_wc_save = ttk.Button(self.lf_wc_frame, text = 'Create Wifi Capacity Test Suite Json', command = self.create_wc_json)
        self.lf_wc_save.grid(row=8, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_wc_save, 'Save Wifi Capacity Json File')


        self.lf_wc_clear = ttk.Button(self.lf_wc_frame, text = 'Clear WC Info', command = self.wc_clear_information)
        self.lf_wc_clear.grid(row=8, column=1, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_wc_clear, 'Clear Wifi Capacity Information, use between test suite generation')
        

        # Max Stations
        for widget in self.lf_wc_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        



        #-----------------------------------------------------------------------------------
        #
        #  End Wifi Capacity
        #
        #------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------------
        #
        #  Create Data Plane or RvR 
        #
        #------------------------------------------------------------------------------------
        self.lf_dp_rvr_tab_frame = tkinter.Frame(self.dp_rvr_tab)
        self.lf_dp_rvr_tab_frame.pack()

        

        self.dp_rvr_suite_type=""
        self.dp_rvr_previous_suite_type=""


        # lanforge Information for json
        self.lf_dp_rvr_frame = tkinter.LabelFrame(self.lf_dp_rvr_tab_frame, text="Data Plane / RvR Configuration")
        self.lf_dp_rvr_frame.grid(row= 0, column= 0, sticky="news", padx=20, pady=10)
        
        # Row 1
        self.lf_dp_rvr_traffic_type_label = tkinter.Label(self.lf_dp_rvr_frame, text="Traffic Type")
        self.lf_dp_rvr_traffic_type_label.grid(row=1, column=0)
        self.lf_dp_rvr_traffic_type_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["UDP","TCP","UDP;TCP"])
        self.lf_dp_rvr_traffic_type_combobox.current(0)
        self.lf_dp_rvr_traffic_type_combobox.grid(row= 1, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_traffic_type_combobox, '''Select the traffic type''')

        self.lf_dp_rvr_dut_traffic_direction_label = tkinter.Label(self.lf_dp_rvr_frame, text="Traffic Direction")
        self.lf_dp_rvr_dut_traffic_direction_label.grid(row=1, column=2)
        self.lf_dp_rvr_dut_traffic_direction_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["DUT Transmit","DUT Receive","DUT Transmit;DUT Receive"])
        self.lf_dp_rvr_dut_traffic_direction_combobox.current(0)
        self.lf_dp_rvr_dut_traffic_direction_combobox.grid(row= 1, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_dut_traffic_direction_combobox, '''Select DUT Traffic Direction''')

        # Row 2        
        self.lf_dp_rvr_pkt_size_label = tkinter.Label(self.lf_dp_rvr_frame, text="Packet Size")
        self.lf_dp_rvr_pkt_size_label.grid(row=2, column=0)
        self.lf_dp_rvr_pkt_size_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["Custom","60","142","256","512","1024","MTU","4000"])
        self.lf_dp_rvr_pkt_size_combobox.current(6)
        self.lf_dp_rvr_pkt_size_combobox.grid(row= 2, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_pkt_size_combobox, '''Enter Data Plane or RvR pkt size separated by semi colons
When using Custom Packet Sizes need to append: ;Custom''')

        self.lf_dp_rvr_pkt_size_custom_label = tkinter.Label(self.lf_dp_rvr_frame, text="Custom Pkt Size")
        self.lf_dp_rvr_pkt_size_custom_label.grid(row=2, column=2)
        self.lf_dp_rvr_pkt_size_custom_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["","<custom>","256,512,768,1024,MTU","768,1024,MTU"])
        self.lf_dp_rvr_pkt_size_custom_combobox.current(0)
        self.lf_dp_rvr_pkt_size_custom_combobox.grid(row= 2, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_pkt_size_custom_combobox, '''Enter Data Plane or RvR Custom Packet Sized pkt size
The Packet Size needs end in Custom for example   60:Custom''')

        # Row 3
        self.lf_dp_rvr_download_speed_label = tkinter.Label(self.lf_dp_rvr_frame, text="Download Speed")
        self.lf_dp_rvr_download_speed_label.grid(row=3, column=0)
        self.lf_dp_rvr_download_speed_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>","85%","75%","65%","50%","25%","10%","5%","1%","0"])
        self.lf_dp_rvr_download_speed_combobox.current(1)
        self.lf_dp_rvr_download_speed_combobox.grid(row= 3, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_download_speed_combobox, '''Download speed is assoicated with DUT Transmit
if on DUT Receive is choosen the Download speed is set to 0''')

        self.lf_dp_rvr_upload_speed_label = tkinter.Label(self.lf_dp_rvr_frame, text="Upload Speed")
        self.lf_dp_rvr_upload_speed_label.grid(row=3, column=2)
        self.lf_dp_rvr_upload_speed_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>","85%","75%","65%","50%","25%","10%","5%","1%","0"])
        self.lf_dp_rvr_upload_speed_combobox.current(1)
        self.lf_dp_rvr_upload_speed_combobox.grid(row= 3, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_upload_speed_combobox, '''Upload speed is associated with with DUT Receive
if only DUT Transmit is choosen the upload speed is set to 0''')

        # Row 4
        self.lf_dp_rvr_attenuator_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuator")
        self.lf_dp_rvr_attenuator_label.grid(row=4, column=0)
        self.lf_dp_rvr_attenuator_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["","ATTENUATOR_1","ATTENUATOR_2","ATTENUATOR_3"])
        self.lf_dp_rvr_attenuator_combobox.current(0)
        self.lf_dp_rvr_attenuator_combobox.grid(row= 4, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_upload_speed_combobox, "The ATTENUATOR is definded in the test_rig.json file")

        self.lf_dp_rvr_attenuation_2g_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuation 2g")
        self.lf_dp_rvr_attenuation_2g_label.grid(row=5, column=0)
        self.lf_dp_rvr_attenuation_2g_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>","0..+100..500","0..+100..600","0..+100..700","400,450,460,470,490,500"])
        self.lf_dp_rvr_attenuation_2g_combobox.current(1)
        self.lf_dp_rvr_attenuation_2g_combobox.grid(row= 5, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_attenuation_2g_combobox, '''Select the atteunation range  <start>..+<step>..<end> 
May also enter custom Example 0..+100..700''')

        self.lf_dp_rvr_attenuation_5g_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuation 5g")
        self.lf_dp_rvr_attenuation_5g_label.grid(row=5, column=2)
        self.lf_dp_rvr_attenuation_5g_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>","0..+100..500","0..+100..600","0..+100..700","400,450,460,470,490,500"])
        self.lf_dp_rvr_attenuation_5g_combobox.current(1)
        self.lf_dp_rvr_attenuation_5g_combobox.grid(row= 5, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_attenuation_5g_combobox, '''Select the atteunation range  <start>..+<step>..<end> 
May also enter custom Example 0..+100..700''')

        self.lf_dp_rvr_attenuation_6g_label = tkinter.Label(self.lf_dp_rvr_frame, text="Attenuation 6g")
        self.lf_dp_rvr_attenuation_6g_label.grid(row=5, column=4)
        self.lf_dp_rvr_attenuation_6g_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<custom>","0..+100..500","0..+100..600","0..+100..700","400,450,460,470,490,500"])
        self.lf_dp_rvr_attenuation_6g_combobox.current(1)
        self.lf_dp_rvr_attenuation_6g_combobox.grid(row= 5, column=5)
        self.window_tooltip.bind(self.lf_dp_rvr_attenuation_6g_combobox, '''Select the atteunation range  <start>..+<step>..<end> 
May also enter custom Example 0..+100..700''')

        self.lf_dp_rvr_2g_file = tkinter.Label(self.lf_dp_rvr_frame, text='2g json file')
        self.lf_dp_rvr_2g_file.grid(row= 6, column= 0)
        self.lf_dp_rvr_2g_file_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_2g_file_entry_var.set("")
        self.lf_dp_rvr_2g_file_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable = self.lf_dp_rvr_2g_file_entry_var, width = 64)
        self.lf_dp_rvr_2g_file_entry.grid(row= 6, column=1, columnspan = 3)
        self.window_tooltip.bind(self.lf_dp_rvr_2g_file_entry, '''Auto Generated json file name to be used by lf_check.py would be:
./lf_check.py  --json_test <QA generated name>.json:<Qa generated name>''')

        self.lf_dp_rvr_5g_file = tkinter.Label(self.lf_dp_rvr_frame, text='5g json file')
        self.lf_dp_rvr_5g_file.grid(row= 7, column= 0)
        self.lf_dp_rvr_5g_file_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_5g_file_entry_var.set("")
        self.lf_dp_rvr_5g_file_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable = self.lf_dp_rvr_5g_file_entry_var, width = 64)
        self.lf_dp_rvr_5g_file_entry.grid(row= 7, column=1, columnspan=3)
        self.window_tooltip.bind(self.lf_dp_rvr_5g_file_entry, ''''Auto Generated json file name to be used by lf_check.py would be:
./lf_check.py  --json_test <QA generated name>.json:<Qa generated name>''')

        self.lf_dp_rvr_6g_file = tkinter.Label(self.lf_dp_rvr_frame, text='6g json file')
        self.lf_dp_rvr_6g_file.grid(row=8, column= 0)
        self.lf_dp_rvr_6g_file_entry_var = tkinter.StringVar()
        self.lf_dp_rvr_6g_file_entry_var.set("")
        self.lf_dp_rvr_6g_file_entry = tkinter.Entry(self.lf_dp_rvr_frame, textvariable = self.lf_dp_rvr_6g_file_entry_var, width = 64)
        self.lf_dp_rvr_6g_file_entry.grid(row=8, column=1, columnspan = 3)
        self.window_tooltip.bind(self.lf_dp_rvr_6g_file_entry, ''''Auto Generated json file name to be used by lf_check.py would be:
./lf_check.py  --json_test <QA generated name>.json:<Qa generated name>''')

        self.lf_dp_rvr_duration = tkinter.Label(self.lf_dp_rvr_frame, text='test duration')
        self.lf_dp_rvr_duration.grid(row= 9, column= 0)
        self.lf_dp_rvr_duration_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["<Custom>","5000 (5 sec)","10000 (10 sec)","15000 (15 sec)","20000 (20 sec)","30000 (30 sec)","60000 (1 min)","300000 (5min)"])
        self.lf_dp_rvr_duration_combobox.current(3)
        self.lf_dp_rvr_duration_combobox.grid(row= 9, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_duration_combobox, '''Enter the test duration , for custom it is in ms
Example:  20000 milli seconds will run the test for 20 seconds
if left blank will default to 20000''')

        self.lf_dp_rvr_number_dut_indexes = tkinter.Label(self.lf_dp_rvr_frame, text="Number DUT Indexes")
        self.lf_dp_rvr_number_dut_indexes.grid(row=9, column=2)
        self.lf_dp_rvr_number_dut_indexes_combobox = ttk.Combobox(self.lf_dp_rvr_frame, values=["1","2","3","4"])
        self.lf_dp_rvr_number_dut_indexes_combobox.current(2)
        self.lf_dp_rvr_number_dut_indexes_combobox.grid(row= 9, column=3)
        self.window_tooltip.bind(self.lf_dp_rvr_number_dut_indexes_combobox, '''Number of DUT indexes valid in the DUT json''')


        self.lf_dp_rvr_use_qa_var = tkinter.StringVar(value="Use")
        self.lf_dp_rvr_use_qa_var_check = tkinter.Checkbutton(self.lf_dp_rvr_frame, text="lf_qa", variable=self.lf_dp_rvr_use_qa_var,
                                        onvalue="Use", offvalue="Do Not Use")
        self.lf_dp_rvr_use_qa_var_check.grid(row=10, column=0)
        self.window_tooltip.bind(self.lf_dp_rvr_use_qa_var_check, '''Recommended: Wifi Capacity Test Suite Json will include lf_qa.
lf_qa will compare performance over multiple runs for Chamber View tests and tests that include kpi''')

        self.lf_dp_rvr_use_inspect_var = tkinter.StringVar(value="Use")
        self.lf_dp_rvr_use_inspect_check = tkinter.Checkbutton(self.lf_dp_rvr_frame, text="lf_inspect", variable=self.lf_dp_rvr_use_inspect_var,
                                        onvalue="Use", offvalue="Do Not Use")
        self.lf_dp_rvr_use_inspect_check.grid(row=10, column=1)
        self.window_tooltip.bind(self.lf_dp_rvr_use_inspect_check, '''Recommended: Wifi Capacity Test Suite Json will include lf_inspect. 
lf_inspect will compare performance between two individual runs for Chamber View tests and tests that include kpi''')

        self.lf_dp_rvr_save = ttk.Button(self.lf_dp_rvr_frame, text = 'Create DP Suite', command = self.create_dp_json)
        self.lf_dp_rvr_save.grid(row=11, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_dp_rvr_save, 'Save Data Plane suite Json File')

        self.lf_dp_rvr_save = ttk.Button(self.lf_dp_rvr_frame, text = 'Create RvR Suite', command = self.create_rvr_json)
        self.lf_dp_rvr_save.grid(row=11, column=1, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_dp_rvr_save, 'Save RvR test suite Json File')


        self.lf_dp_rvr_clear = ttk.Button(self.lf_dp_rvr_frame, text = 'Clear DP, RvR Info', command = self.dp_rvr_clear_information)
        self.lf_dp_rvr_clear.grid(row=11, column=2, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_dp_rvr_clear, 'Clear File Names , use between test suite generation')


        # Max Stations
        for widget in self.lf_dp_rvr_frame.winfo_children():
            widget.grid_configure(padx=5, pady=5)
        

        #-----------------------------------------------------------------------------------
        #
        #  End Data Plane or RvR
        #
        #------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------------
        #
        #  Create AP Auto Tests
        #
        #------------------------------------------------------------------------------------
        self.lf_ap_auto_tab_frame = tkinter.Frame(self.ap_auto_tab)
        self.lf_ap_auto_tab_frame.pack()

        # lanforge Information for json
        self.lf_ap_auto_frame = tkinter.LabelFrame(self.lf_ap_auto_tab_frame, text="AP Auto - Under development")
        self.lf_ap_auto_frame.grid(row= 0, column= 0, sticky="news", padx=20, pady=10)

        self.lf_ap_auto_2g_file = tkinter.Label(self.lf_ap_auto_frame, text='2g json file')
        self.lf_ap_auto_2g_file.grid(row= 1, column= 0)
        self.lf_ap_auto_2g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_2g_file_entry_var.set("")
        self.lf_ap_auto_2g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable = self.lf_ap_auto_2g_file_entry_var, width = 48)
        self.lf_ap_auto_2g_file_entry.grid(row= 1, column=1, columnspan = 2)
        self.window_tooltip.bind(self.lf_ap_auto_2g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_5g_file = tkinter.Label(self.lf_ap_auto_frame, text='5g json file')
        self.lf_ap_auto_5g_file.grid(row= 2, column= 0)
        self.lf_ap_auto_5g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_5g_file_entry_var.set("")
        self.lf_ap_auto_5g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable = self.lf_ap_auto_5g_file_entry_var, width = 48)
        self.lf_ap_auto_5g_file_entry.grid(row= 2, column=1, columnspan = 2)
        self.window_tooltip.bind(self.lf_ap_auto_5g_file_entry, '''Auto generated name for AP Auto Test Suite''')

        self.lf_ap_auto_6g_file = tkinter.Label(self.lf_ap_auto_frame, text='6g json file')
        self.lf_ap_auto_6g_file.grid(row= 3, column= 0)
        self.lf_ap_auto_6g_file_entry_var = tkinter.StringVar()
        self.lf_ap_auto_6g_file_entry_var.set("")
        self.lf_ap_auto_6g_file_entry = tkinter.Entry(self.lf_ap_auto_frame, textvariable = self.lf_ap_auto_6g_file_entry_var, width = 48)
        self.lf_ap_auto_6g_file_entry.grid(row= 3, column=1, columnspan = 2)
        self.window_tooltip.bind(self.lf_ap_auto_6g_file_entry, '''Auto generated name for AP Auto Test Suite''')


        self.lf_ap_auto_duration = tkinter.Label(self.lf_ap_auto_frame, text='test duration (ms)')
        self.lf_ap_auto_duration.grid(row= 4, column= 0)
        self.lf_ap_auto_duration_combobox = ttk.Combobox(self.lf_ap_auto_frame, values=["<Custom>","5000 (5 sec)","10000 (10 sec)","15000 (15 sec)","20000 (20 sec)","30000 (30 sec)","60000 (1 min)","300000 (5min)"])
        self.lf_ap_auto_duration_combobox.current(3)
        self.lf_ap_auto_duration_combobox.grid(row= 4, column=1)
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


        self.lf_ap_auto_save = ttk.Button(self.lf_ap_auto_frame, text = 'Create AP Auto Test Suite Json', command = self.create_ap_auto_json)
        self.lf_ap_auto_save.grid(row=11, column=0, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_ap_auto_save, 'Save Wifi Capacity Json File')


        self.lf_ap_auto_clear = ttk.Button(self.lf_ap_auto_frame, text = 'Clear AP Auto Info', command = self.ap_auto_clear_information)
        self.lf_ap_auto_clear.grid(row=11, column=1, sticky="news", padx=20, pady=10)
        self.window_tooltip.bind(self.lf_ap_auto_clear, 'Clear AP Auto Information, use between test suite generation')
        

        # Max Stations
        for widget in self.lf_ap_auto_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        



        #-----------------------------------------------------------------------------------
        #
        #  End AP Auto Tests
        #
        #------------------------------------------------------------------------------------

        #-----------------------------------------------------------------------------------
        #
        #  Create Functional Tests
        #
        #------------------------------------------------------------------------------------
        self.lf_functional_tab_frame = tkinter.Frame(self.functional_tab)
        self.lf_functional_tab_frame.pack()

        # create then either pack, place, grid
        self.test_l3_frame = tkinter.Frame(self.lf_functional_tab_frame)
        self.test_l3_frame.pack()


        # lanforge Radio Information
        self.lf_test_l3_frame = tkinter.LabelFrame(self.test_l3_frame, text="Radio Information")
        self.lf_test_l3_frame.grid(row= 1, column= 0, sticky="news", padx=20, pady=10)



        #-----------------------------------------------------------------------------------
        #
        #  End Functional Tests
        #
        #------------------------------------------------------------------------------------



        #------------------------------------------------------------------------------------
        #
        #  Menu Bar
        #
        #------------------------------------------------------------------------------------

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


        #-------------------------------------------------------------------------------------
        #
        # Pratice Tab Begin
        #
        #-------------------------------------------------------------------------------------

        self.label = tkinter.Label(self.practice_tab, text="Your Message", font=('Arial', 18))
        self.label.pack(padx=10, pady=10)


        self.textbox = tkinter.Text(self.practice_tab, font=('Arial',16))
        self.textbox.bind("<KeyPress>", self.short_cut)
        self.textbox.pack(padx=10, pady=10)
      
        self.check_state = tkinter.IntVar()

        self.check  = tkinter.Checkbutton(self.practice_tab, text="Show Messagebox", font=('Arial',16), variable=self.check_state)
        self.check.pack(padx=10, pady=10)

        self.button = tkinter.Button(self.practice_tab, text="Show Meassage", font=('Arial',18), command=self.show_message)
        self.button.pack(padx=10, pady=10)

        self.clearbtn = tkinter.Button(self.practice_tab, text="Clear", font=('Arial', 18), command=self.clear)
        self.clearbtn.pack(padx=10, pady=10)

        #-------------------------------------------------------------------------------------
        #
        # Practice Tab End
        #
        #-------------------------------------------------------------------------------------

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
        


    def create_rig_json(self):
        rig_json = lf_rig_json.lf_create_rig_json(_file=self.lf_rig_file_entry_var.get(),
                               _lf_mgr=self.lf_mgr_entry_var.get(),
                               _lf_mgr_port=self.lf_mgr_port_entry_var.get(),
                               _lf_user=self.lf_user_entry_var.get(),
                               _lf_passwd=self.lf_passwd_entry_var.get(),
                               _test_rig=self.lf_test_rig_entry_var.get(),
                               _test_bed=self.lf_test_bed_entry_var.get(),
                               _test_server=self.lf_test_server_entry_var.get(),
                               _test_db=self.lf_test_db_entry_var.get(),
                               _upstream_port=self.lf_upstream_port_entry_var.get(),
                               _test_timeout=600,
                               _lf_atten_1_entry = self.lf_atten_1_entry.get(),
                               _lf_atten_2_entry = self.lf_atten_2_entry.get(),
                               _lf_atten_3_entry = self.lf_atten_3_entry.get(),
                               _lf_email_entry=self.lf_email_entry.get(),
                               _lf_email_production_entry=self.lf_email_production_entry.get())
        
        rig_json.create()
        tkinter.messagebox.showinfo(title="success", message= self.lf_rig_file_entry_var.get() + " created")  


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
                _use_radio_dict = self.use_radio_var_dict,
                _radio_dict = self.radio_dict,
                _radio_type_dict = self.radio_type_dict,
                _radio_max_sta_dict = self.radio_max_sta_dict,
                _use_radio_var_dict = self.use_radio_var_dict,
                _use_radio_2g_var_dict = self.use_radio_2g_var_dict,
                _use_radio_5g_var_dict = self.use_radio_5g_var_dict,
                _use_radio_6g_var_dict = self.use_radio_6g_var_dict,
                _suite_radios_2g = self.suite_radios_2g,
                _suite_radios_5g = self.suite_radios_5g,
                _suite_radios_6g = self.suite_radios_6g,
                _suite_test_name_2g_dict = self.suite_test_name_2g_dict,
                _suite_test_name_5g_dict = self.suite_test_name_5g_dict,
                _suite_test_name_6g_dict = self.suite_test_name_6g_dict,
                _radio_count = self.radio_count,
                _radio_batch_dict = self.radio_batch_dict,
                _lf_ap_auto_basic_client_connectivity = self.lf_ap_auto_basic_client_connectivity_var,
                _lf_ap_auto_multi_band_performance = self.lf_ap_auto_multi_band_performance_var,
                _lf_ap_auto_multi_station_throughput_vs_pkt_size = self.lf_ap_auto_multi_station_throughput_vs_pkt_size_var,
                _lf_ap_auto_stability = self.lf_ap_auto_stability_var,
                _lf_ap_auto_channel_switching_test = self.lf_ap_auto_channel_switching_test_var,
                _lf_ap_auto_throughput_vs_pkt_size = self.lf_ap_auto_throughput_vs_pkt_size_var,
                _lf_ap_auto_capacity = self.lf_ap_auto_capacity_var,
                _lf_ap_auto_band_steering = self.lf_ap_auto_band_steering_var,
                _lf_ap_auto_long_term = self.lf_ap_auto_long_term_var,
                _lf_ap_auto_use_qa_var = self.lf_ap_auto_use_qa_var,
                _lf_ap_auto_use_inspect_var = self.lf_ap_auto_use_inspect_var
        )

        if self.suite_radios_2g != "":
            ap_auto_json.test_suite_band = "2g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_2g_file_entry_var.set(ap_auto_json.get_file_2g())
        if self.suite_radios_5g  != "":
            ap_auto_json.test_suite_band = "5g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_5g_file_entry_var.set(ap_auto_json.get_file_5g())
        if self.suite_radios_6g != "":
            ap_auto_json.test_suite_band = "6g"
            ap_auto_json.create_suite()
            self.lf_ap_auto_6g_file_entry_var.set(ap_auto_json.get_file_6g())


        if self.suite_radios_2g == "" and self.suite_radios_5g == "" and self.suite_radios_6g == "":
            tkinter.messagebox.showinfo(title="message", message= "Please Read or Select LANforge Radios on LANforge tab" )  
        else:
            tkinter.messagebox.showinfo(title="success", message= "created \n" + self.lf_ap_auto_2g_file_entry_var.get() +"\n" + self.lf_ap_auto_5g_file_entry_var.get() + "\n" + self.lf_ap_auto_6g_file_entry.get() )  


    def wc_clear_information(self):
        self.lf_wc_2g_file_entry_var.set("")
        self.lf_wc_5g_file_entry_var.set("")
        self.lf_wc_6g_file_entry_var.set("")



    def create_wc_json(self):
        # use the auto generated name        
        self.wc_clear_information()


        wc_duration = self.lf_wc_duration_combobox.get()
        if wc_duration == "":
            self.lf_wc_duration_combobox.set("20000")

        self.lf_wc_use_qa_var.get()
        self.lf_wc_use_inspect_var.get()

        self.lf_radio_2g_combobox.get()
        self.lf_radio_5g_combobox.get()
        self.lf_radio_6g_combobox.get()
        self.lf_wc_number_dut_indexes_combobox.get()
        self.lf_wc_sta_profile_combobox.get()

        ul_rate = self.lf_wc_ul_rate_combobox.get()

        dl_rate = self.lf_wc_dl_rate_combobox.get()


        dictionary_length = len(self.radio_dict)
        logger.debug("radio_dict length = {length}".format(length=dictionary_length))
        wc_json = lf_create_wc_json.lf_create_wc_json(
                _file_2g=self.lf_wc_2g_file_entry_var.get(),
                _file_5g=self.lf_wc_5g_file_entry_var.get(),
                _file_6g=self.lf_wc_6g_file_entry_var.get(),
                _dir_2g=self.lf_wc_2g_dir_entry_var.get(),
                _dir_5g=self.lf_wc_5g_dir_entry_var.get(),
                _dir_6g=self.lf_wc_6g_dir_entry_var.get(),
                _wc_duration=self.lf_wc_duration_combobox.get(),
                _use_radio_dict = self.use_radio_var_dict,
                _radio_dict = self.radio_dict,
                _radio_type_dict = self.radio_type_dict,
                _radio_max_sta_dict = self.radio_max_sta_dict,
                _use_radio_var_dict = self.use_radio_var_dict,
                _use_radio_2g_var_dict = self.use_radio_2g_var_dict,
                _use_radio_5g_var_dict = self.use_radio_5g_var_dict,
                _use_radio_6g_var_dict = self.use_radio_6g_var_dict,
                _suite_radios_2g = self.suite_radios_2g,
                _suite_radios_5g = self.suite_radios_5g,
                _suite_radios_6g = self.suite_radios_6g,
                _suite_test_name_2g_dict = self.suite_test_name_2g_dict,
                _suite_test_name_5g_dict = self.suite_test_name_5g_dict,
                _suite_test_name_6g_dict = self.suite_test_name_6g_dict,
                _radio_count = self.radio_count,
                _radio_batch_dict = self.radio_batch_dict,
                _lf_wc_use_qa_var = self.lf_wc_use_qa_var,
                _lf_wc_use_inspect_var = self.lf_wc_use_inspect_var,
                _lf_radio_2g = self.lf_radio_2g_combobox.get(),
                _lf_radio_5g = self.lf_radio_5g_combobox.get(),
                _lf_radio_6g = self.lf_radio_6g_combobox.get(),
                _lf_wc_number_dut_indexes_combobox = self.lf_wc_number_dut_indexes_combobox,
                _lf_wc_sta_profile_combobox = self.lf_wc_sta_profile_combobox,
                _ul_rate = ul_rate,
                _dl_rate = dl_rate

        )

        if self.suite_radios_2g != "":
            wc_json.test_suite_band = "2g"
            wc_json.create_suite()
            self.lf_wc_2g_file_entry_var.set(wc_json.get_file_2g())
            self.lf_wc_2g_dir_entry_var.set(wc_json.get_dir_2g())
        if self.suite_radios_5g  != "":
            wc_json.test_suite_band = "5g"
            wc_json.create_suite()
            self.lf_wc_5g_file_entry_var.set(wc_json.get_file_5g())
            self.lf_wc_5g_dir_entry_var.set(wc_json.get_dir_5g())
        if self.suite_radios_6g != "":
            wc_json.test_suite_band = "6g"
            wc_json.create_suite()
            self.lf_wc_6g_file_entry_var.set(wc_json.get_file_6g())
            self.lf_wc_6g_dir_entry_var.set(wc_json.get_dir_6g())


        if self.suite_radios_2g == "" and self.suite_radios_5g == "" and self.suite_radios_6g == "":
            tkinter.messagebox.showinfo(title="message", message= "Please Read or Select LANforge Radios on LANforge tab" )  
        else:
            tkinter.messagebox.showinfo(title="success", message= "created \n" + 
                self.lf_wc_2g_dir_entry_var.get() + "/" + self.lf_wc_2g_file_entry_var.get() +"\n" + 
                self.lf_wc_5g_dir_entry_var.get() + "/" + self.lf_wc_5g_file_entry_var.get() + "\n" + 
                self.lf_wc_6g_dir_entry_var.get() + "/" + self.lf_wc_6g_file_entry.get() )  

    def dp_rvr_clear_information(self):
        self.lf_dp_rvr_2g_file_entry_var.set("")
        self.lf_dp_rvr_5g_file_entry_var.set("")
        self.lf_dp_rvr_6g_file_entry_var.set("")
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
        self.lf_dp_rvr_attenuator_combobox.get()
        self.lf_dp_rvr_attenuation_2g_combobox.get()
        self.lf_dp_rvr_attenuation_5g_combobox.get()
        self.lf_dp_rvr_attenuation_6g_combobox.get()

        dictionary_length = len(self.radio_dict)
        logger.debug("radio_dict length = {length}".format(length=dictionary_length))
        dp_rvr_json = lf_create_dp_rvr_json.lf_create_dp_rvr_json(
                _suite_type = self.dp_rvr_suite_type,
                _file_2g=self.lf_dp_rvr_2g_file_entry_var.get(),
                _file_5g=self.lf_dp_rvr_5g_file_entry_var.get(),
                _file_6g=self.lf_dp_rvr_6g_file_entry_var.get(),
                _use_radio_dict = self.use_radio_var_dict,
                _radio_dict = self.radio_dict,
                _radio_type_dict = self.radio_type_dict,
                _radio_max_sta_dict = self.radio_max_sta_dict,
                _use_radio_var_dict = self.use_radio_var_dict,
                _use_radio_2g_var_dict = self.use_radio_2g_var_dict,
                _use_radio_5g_var_dict = self.use_radio_5g_var_dict,
                _use_radio_6g_var_dict = self.use_radio_6g_var_dict,
                _suite_radios_2g = self.suite_radios_2g,
                _suite_radios_5g = self.suite_radios_5g,
                _suite_radios_6g = self.suite_radios_6g,
                _suite_test_name_2g_dict = self.suite_test_name_2g_dict,
                _suite_test_name_5g_dict = self.suite_test_name_5g_dict,
                _suite_test_name_6g_dict = self.suite_test_name_6g_dict,
                _radio_count = self.radio_count,
                _radio_batch_dict = self.radio_batch_dict,
                _lf_dp_rvr_use_qa_var = self.lf_dp_rvr_use_qa_var,
                _lf_dp_rvr_use_inspect_var = self.lf_dp_rvr_use_inspect_var,
                _lf_dp_rvr_duration_combobox=self.lf_dp_rvr_duration_combobox,
                _lf_dp_rvr_traffic_type_combobox = self.lf_dp_rvr_traffic_type_combobox,
                _lf_dp_rvr_dut_traffic_direction_combobox = self.lf_dp_rvr_dut_traffic_direction_combobox,
                _lf_dp_rvr_pkt_size_combobox = self.lf_dp_rvr_pkt_size_combobox,
                _lf_dp_rvr_pkt_size_custom_combobox = self.lf_dp_rvr_pkt_size_custom_combobox,
                _lf_dp_rvr_download_speed_combobox = self.lf_dp_rvr_download_speed_combobox,
                _lf_dp_rvr_upload_speed_combobox = self.lf_dp_rvr_upload_speed_combobox,
                _lf_dp_rvr_attenuator_combobox = self.lf_dp_rvr_attenuator_combobox,      
                _lf_dp_rvr_attenuation_2g_combobox = self.lf_dp_rvr_attenuation_2g_combobox,
                _lf_dp_rvr_attenuation_5g_combobox = self.lf_dp_rvr_attenuation_5g_combobox,
                _lf_dp_rvr_attenuation_6g_combobox = self.lf_dp_rvr_attenuation_6g_combobox,
                _lf_radio_2g = self.lf_radio_2g_combobox.get(),
                _lf_radio_5g = self.lf_radio_5g_combobox.get(),
                _lf_radio_6g = self.lf_radio_6g_combobox.get(),
                _lf_dp_rvr_number_dut_indexes_combobox=self.lf_dp_rvr_number_dut_indexes_combobox
        )

        if self.suite_radios_2g != "":
            dp_rvr_json.test_suite_band = "2g"
            dp_rvr_json.create_suite()
            self.lf_dp_rvr_2g_file_entry_var.set(dp_rvr_json.get_file_2g())
        else:
            self.lf_dp_rvr_2g_file_entry_var.set("")

        if self.suite_radios_5g  != "":
            dp_rvr_json.test_suite_band = "5g"
            dp_rvr_json.create_suite()
            self.lf_dp_rvr_5g_file_entry_var.set(dp_rvr_json.get_file_5g())
        else:
            self.lf_dp_rvr_5g_file_entry_var.set("")

        if self.suite_radios_6g != "":
            dp_rvr_json.test_suite_band = "6g"
            dp_rvr_json.create_suite()
            self.lf_dp_rvr_6g_file_entry_var.set(dp_rvr_json.get_file_6g())
        else:
            self.lf_dp_rvr_6g_file_entry_var.set("")


        if self.suite_radios_2g == "" and self.suite_radios_5g == "" and self.suite_radios_6g == "":
            tkinter.messagebox.showinfo(title="message", message= "Please Read or Select LANforge Radios on LANforge tab" )  
        else:
            tkinter.messagebox.showinfo(title="success", message= "created \n" + self.lf_dp_rvr_2g_file_entry_var.get() +"\n" + self.lf_dp_rvr_5g_file_entry_var.get() + "\n" + self.lf_dp_rvr_6g_file_entry.get() )  


    def create_dut_json(self):


        for idx in range(0,self.lf_idx_upper_range):

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
        tkinter.messagebox.showinfo(title="success", message= self.lf_dut_file_entry_var.get() + " created")  


    def get_lanforge_radio_information(self):

        # clear then re-read
        self.clear_lanforge_radio_information()

        # https://docs.python-requests.org/en/latest/
        # https://stackoverflow.com/questions/26000336/execute-curl-command-within-a-python-script - use requests
        # curl --user "lanforge:lanforge" -H 'Accept: application/json'
        # http://192.168.100.116:8080/radiostatus/all | json_pp  , where --user
        # "USERNAME:PASSWORD"

        # https://stackoverflow.com/questions/61236703/tkinter-how-to-access-a-stringvar-and-objects-from-a-different-class/61237289#61237289        
        # access data 
        request_command = 'http://{lfmgr}:{port}/radiostatus/all'.format(lfmgr=self.lf_mgr_entry_var.get(), 
                                                                         port=self.lf_mgr_port_entry_var.get())
        request = requests.get(request_command, auth=(self.lf_user_entry_var.get(), self.lf_passwd_entry_var.get()))
        logger.debug("radio request command: {request_command}".format(request_command=request_command))
        logger.debug("radio request status_code {status}".format(status=request.status_code))
        self.lanforge_radio_json = request.json()
        logger.debug("radio request.json: {json}".format(json=self.lanforge_radio_json))
        self.lanforge_radio_text = request.text
        logger.debug("radio request.test: {text}".format(text=self.lanforge_radio_text))


        radio = 0
        for key in self.lanforge_radio_json:
            if 'wiphy' in key:
                self.radio_dict[radio].set(self.lanforge_radio_json[key]['entity id'])
                self.radio_type_dict[radio].set(self.lanforge_radio_json[key]['capabilities'])
                radio_name_tmp = self.lanforge_radio_json[key]['driver'].split('Driver:', maxsplit=1)[-1].split('Bus:', maxsplit=1)[0]
                self.radio_max_sta_dict[radio].set(self.lanforge_radio_json[key]['max_sta'])

                # for now have batch size be 1
                self.radio_batch_dict[radio].set("1")

                radio_name_tmp = radio_name_tmp.strip()
                if "mt" in radio_name_tmp:
                    radio_name_tmp = radio_name_tmp.split(' ', maxsplit=1)[0]
                elif "ath10" in radio_name_tmp:
                    radio_name_tmp = radio_name_tmp.replace(' (','_').replace(')','')
                elif "AX2" in radio_name_tmp:
                    radio_name_tmp = radio_name_tmp.replace('iwlwifi (','').replace(')','')
                    radio_name_tmp = radio_name_tmp.replace('iwlwifi(','').replace(')','') # Older syntax
                elif "BE2" in radio_name_tmp:
                    radio_name_tmp = radio_name_tmp.replace('iwlwifi (','').replace(')','')
                    radio_name_tmp = radio_name_tmp.replace('iwlwifi(','').replace(')','') # Older syntax
                elif "ath9" in radio_name_tmp:
                    pass

                self.radio_model_dict[radio].set(radio_name_tmp)

                self.use_radio_var_dict[radio].set("Use")
                radio_type = self.lanforge_radio_json[key]['capabilities']
                if '802.11bgn' in radio_type or '802.11abgn' in radio_type:
                    self.use_radio_2g_var_dict[radio].set("Use")
                    self.suite_test_name_2g_dict[radio] = self.radio_model_dict[radio]
                else:
                    self.use_radio_2g_var_dict[radio].set("Do Not Use")

                if '802.11abgn' in radio_type or '802.11an' in radio_type:
                    self.use_radio_5g_var_dict[radio].set("Use")
                    self.suite_test_name_5g_dict[radio] = self.radio_model_dict[radio]
                else:
                    self.use_radio_5g_var_dict[radio].set("Do Not Use")
                
                if 'AX' in radio_type or 'BE' in radio_type:
                    if '7915' in radio_name_tmp:
                        self.use_radio_6g_var_dict[radio].set("Do Not Use")
                    else:
                        self.use_radio_6g_var_dict[radio].set("Use")
                        self.suite_test_name_6g_dict[radio] = self.radio_model_dict[radio]
                else:
                    self.use_radio_6g_var_dict[radio].set("Do Not Use")
                
                if "Use" == self.use_radio_2g_var_dict[radio].get():
                    self.suite_radios_2g += "_W{}".format(radio)

                if "Use" == self.use_radio_5g_var_dict[radio].get():
                    self.suite_radios_5g += "_W{}".format(radio)

                if "Use" == self.use_radio_6g_var_dict[radio].get():
                    self.suite_radios_6g += "_W{}".format(radio)

                radio += 1

    def apply_lanforge_radio_information(self):

        radio = 0
        self.suite_radios_2g = ""
        self.suite_radios_5g = ""
        self.suite_radios_6g = ""
        for radio in range(0,self.max_radios):
            if "Use" == self.use_radio_var_dict[radio].get():
                if "Use" == self.use_radio_2g_var_dict[radio].get():
                    self.suite_radios_2g += "_W{}".format(radio)

                if "Use" == self.use_radio_5g_var_dict[radio].get():
                    self.suite_radios_5g += "_W{}".format(radio)

                if "Use" == self.use_radio_6g_var_dict[radio].get():
                    self.suite_radios_6g += "_W{}".format(radio)

        radio_message = f"2g: {self.suite_radios_2g}\n5g: {self.suite_radios_5g}\n6g: {self.suite_radios_6g}"
        tkinter.messagebox.showinfo(title="Updated", message= radio_message)  

    def get_suite_radios_2g(self):
        return self.suite_radios_2g

    def get_suite_radios_5g(self):
        return self.suite_radios_5g

    def get_suite_radios_6g(self):
        return self.suite_radios_6g


    def clear_lanforge_radio_information(self):

        for radio in range(0,self.max_radios):

            self.use_radio_var_dict[radio].set("Do Not Use")
            self.radio_dict[radio].set("")
            self.radio_type_dict[radio].set("")
            self.radio_model_dict[radio].set("")
            self.radio_max_sta_dict[radio].set("")
            self.radio_batch_dict[radio].set("")
            self.radio_count += 1
            self.use_radio_2g_var_dict[radio].set("Do Not Use")
            self.use_radio_5g_var_dict[radio].set("Do Not Use")
            self.use_radio_6g_var_dict[radio].set("Do Not Use")
            self.suite_radios_2g = ""
            self.suite_radios_5g = ""
            self.suite_radios_6g = ""
            


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
    parser.add_argument('--radio_count', help='Number of radios to display on GUI', default='8')

    args = parser.parse_args()
    _radio_count = args.radio_count


    my_gui = json_gen_gui(radio_count=int(_radio_count))
    # TODO allow log level to be sets
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level='debug')


if __name__ == '__main__':
    main()
