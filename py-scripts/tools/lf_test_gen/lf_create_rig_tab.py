import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import importlib

lf_rig_json = importlib.import_module("lf_create_rig_json")

class lf_create_rig_tab():

   def __init__(self, rig_tab, window_tooltip, current_working_directory):
      self.rig_tab = rig_tab
      self.window_tooltip = window_tooltip
      self.current_working_directory = current_working_directory

      # -----------------------------------------------------------------------------------
      #
      #  Create Rig Json
      #
      # ------------------------------------------------------------------------------------
      self.lf_rig_tab_frame = tkinter.Frame(self.rig_tab)
      self.lf_rig_tab_frame.pack()

      # lanforge Information for json
      self.lf_rig_frame = tkinter.LabelFrame(self.lf_rig_tab_frame, text="LANforge Rig Information")
      self.lf_rig_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)

      self.lf_mgr = tkinter.Label(self.lf_rig_frame, text="IP")
      self.lf_mgr.grid(row=1, column=0)
      self.lf_mgr_entry_var = tkinter.StringVar()
      # self.lf_mgr_entry_var.set("192.168.100.116")
      self.lf_mgr_entry_var.set("")
      self.lf_mgr_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_mgr_entry_var)
      self.lf_mgr_entry.grid(row=1, column=1)
      self.window_tooltip.bind(self.lf_mgr_entry, 'Enter LANforge Manager IP')

      self.lf_mgr_port = tkinter.Label(self.lf_rig_frame, text='PORT')
      self.lf_mgr_port.grid(row=1, column=2)
      self.lf_mgr_port_entry_var = tkinter.StringVar()
      self.lf_mgr_port_entry_var.set("8080")
      self.lf_mgr_port_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_mgr_port_entry_var)
      self.lf_mgr_port_entry.grid(row=1, column=3)
      self.window_tooltip.bind(self.lf_mgr_port_entry, 'Enter LANforge Manager Port')

      self.lf_user = tkinter.Label(self.lf_rig_frame, text="USER")
      self.lf_user.grid(row=1, column=4)
      self.lf_user_entry_var = tkinter.StringVar()
      self.lf_user_entry_var.set("lanforge")
      self.lf_user_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_user_entry_var)
      self.lf_user_entry.grid(row=1, column=5)
      self.window_tooltip.bind(self.lf_user_entry, 'Enter Lanforge Username')

      self.lf_passwd = tkinter.Label(self.lf_rig_frame, text='PASSWORD')
      self.lf_passwd.grid(row=1, column=6)
      self.lf_passwd_entry_var = tkinter.StringVar()
      self.lf_passwd_entry_var.set("lanforge")
      self.lf_passwd_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_passwd_entry_var)
      self.lf_passwd_entry.grid(row=1, column=7)
      self.window_tooltip.bind(self.lf_passwd_entry, 'Enter Lanforge Password')

      # second row
      self.lf_test_rig = tkinter.Label(self.lf_rig_frame, text="TEST RIG")
      self.lf_test_rig.grid(row=2, column=0)
      self.lf_test_rig_entry_var = tkinter.StringVar()
      self.lf_test_rig_entry_var.set("LANforge")
      self.lf_test_rig_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_test_rig_entry_var)
      self.lf_test_rig_entry.grid(row=2, column=1)
      self.window_tooltip.bind(self.lf_test_rig_entry, 'Enter Test RIG NAME')

      self.lf_test_bed = tkinter.Label(self.lf_rig_frame, text='TEST BED')
      self.lf_test_bed.grid(row=2, column=2)
      self.lf_test_bed_entry_var = tkinter.StringVar()
      self.lf_test_bed_entry_var.set("TESTBED")
      self.lf_test_bed_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_test_bed_entry_var)
      self.lf_test_bed_entry.grid(row=2, column=3)
      self.window_tooltip.bind(self.lf_test_bed_entry, 'Enter Test Bed Name')

      self.lf_test_server = tkinter.Label(self.lf_rig_frame, text="TEST SERVER")
      self.lf_test_server.grid(row=2, column=4)
      self.lf_test_server_entry_var = tkinter.StringVar()
      self.lf_test_server_entry_var.set("localhost")
      self.lf_test_server_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_test_server_entry_var)
      self.lf_test_server_entry.grid(row=2, column=5)
      self.window_tooltip.bind(self.lf_test_server_entry, 'Enter ip of test reports server can be lanforge ip, default set to lanforge ip input')

      # third row
      self.lf_test_db = tkinter.Label(self.lf_rig_frame, text="SQLite Database")
      self.lf_test_db.grid(row=3, column=0)
      self.lf_test_db_entry_var = tkinter.StringVar()
      self.lf_test_db_entry_var.set("LANforge")
      self.lf_test_db_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_test_db_entry_var)
      self.lf_test_db_entry.grid(row=3, column=1)
      self.window_tooltip.bind(self.lf_test_db_entry, 'Enter SQLite Database')

      self.lf_upstream_port = tkinter.Label(self.lf_rig_frame, text='UPSTREAM PORT')
      self.lf_upstream_port.grid(row=3, column=2)
      self.lf_upstream_port_entry_var = tkinter.StringVar()
      self.lf_upstream_port_entry_var.set("1.1.eth2")
      self.lf_upstream_port_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_upstream_port_entry_var)
      self.lf_upstream_port_entry.grid(row=3, column=3)
      self.window_tooltip.bind(self.lf_upstream_port_entry, 'Enter Upstream Port')

      self.lf_test_timeout = tkinter.Label(self.lf_rig_frame, text="TEST TIMEOUT")
      self.lf_test_timeout.grid(row=3, column=4)
      self.lf_test_timeout_entry_var = tkinter.StringVar()
      self.lf_test_timeout_entry_var.set("600")
      self.lf_test_timeout_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_test_timeout_entry_var)
      self.lf_test_timeout_entry.grid(row=3, column=5)
      self.window_tooltip.bind(self.lf_test_timeout_entry, 'Enter test timeout in seconds')

      self.lf_file = tkinter.Label(self.lf_rig_frame, text='json file')
      self.lf_file.grid(row=3, column=6)
      self.lf_rig_file_entry_var = tkinter.StringVar()
      self.lf_rig_file_entry_var.set("ct_auto_gen_rig.json")
      self.lf_file_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_rig_file_entry_var)
      self.lf_file_entry.grid(row=3, column=7)
      self.window_tooltip.bind(self.lf_file_entry, 'Enter rig json file name and/or path and rig json file name  /home/user/ct_auto_gen_rig.json')

      # forth row #TODO can the ATTEN values be read
      self.lf_atten_1 = tkinter.Label(self.lf_rig_frame, text="Atten 1")
      self.lf_atten_1.grid(row=4, column=0)
      self.lf_atten_1_entry_var = tkinter.StringVar()
      self.lf_atten_1_entry_var.set("1.1.3360")
      self.lf_atten_1_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_atten_1_entry_var)
      self.lf_atten_1_entry.grid(row=4, column=1)
      self.window_tooltip.bind(self.lf_atten_1_entry, 'LANforge Atten 1 example 1.1.3360, for test rig uses ATTENUATOR_1')

      self.lf_atten_2 = tkinter.Label(self.lf_rig_frame, text="Atten 2")
      self.lf_atten_2.grid(row=4, column=2)
      self.lf_atten_2_entry_var = tkinter.StringVar()
      self.lf_atten_2_entry_var.set("")
      self.lf_atten_2_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_atten_2_entry_var)
      self.lf_atten_2_entry.grid(row=4, column=3)
      self.window_tooltip.bind(self.lf_atten_2_entry, 'LANforge Atten 2 example 1.1.3360, for the test rig json uses ATTENUATOR_2')

      self.lf_atten_3 = tkinter.Label(self.lf_rig_frame, text="Atten 3")
      self.lf_atten_3.grid(row=4, column=4)
      self.lf_atten_3_entry_var = tkinter.StringVar()
      self.lf_atten_3_entry_var.set("")
      self.lf_atten_3_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_atten_3_entry_var)
      self.lf_atten_3_entry.grid(row=4, column=5)
      self.window_tooltip.bind(self.lf_atten_3_entry, 'LANforge Atten 3 example 1.1.3360, for the test rig json uses ATTENUATOR_3')

      self.lf_email = tkinter.Label(self.lf_rig_frame, text='Email Results:')
      self.lf_email.grid(row=5, column=0)
      self.lf_email_entry_var = tkinter.StringVar()
      self.lf_email_entry_var.set("")
      self.lf_email_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_email_entry_var, width=80)
      self.lf_email_entry.grid(row=5, column=1, columnspan=4)
      self.window_tooltip.bind(self.lf_email_entry, '''Enter emails to receive notification of test results and completion. Comma separated list''')

      self.lf_email_production = tkinter.Label(self.lf_rig_frame, text='Email Results Production:')
      self.lf_email_production.grid(row=6, column=0)
      self.lf_email_production_entry_var = tkinter.StringVar()
      self.lf_email_production_entry_var.set("")
      self.lf_email_production_entry = tkinter.Entry(self.lf_rig_frame, textvariable=self.lf_email_production_entry_var, width=80)
      self.lf_email_production_entry.grid(row=6, column=1, columnspan=4)
      self.window_tooltip.bind(self.lf_email_production_entry, '''Enter emails for Production results. Comma separated list''')

      # Max Stations
      for widget in self.lf_rig_frame.winfo_children():
         widget.grid_configure(padx=10, pady=5)

      # save = ttk.Button(self.lf_rig_frame, text = 'Create Test Rig Json', command = lambda : messagebox.askyesno('Confirm', 'Do you want to save?'))
      self.lf_rig_save = ttk.Button(self.lf_rig_frame, text='Create Test Rig Json', command=self.create_rig_json)
      self.lf_rig_save.grid(row=7, column=0, sticky="news", padx=20, pady=10)
      rig_tool_tip_text = "Create Rig Json, In Current Working Directory: {}".format(self.current_working_directory)
      self.window_tooltip.bind(self.lf_rig_save, rig_tool_tip_text)

   # -----------------------------------------------------------------------------------
   #
   #  End of Create Rig Json
   #
   # ------------------------------------------------------------------------------------

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
                                                _lf_atten_1_entry=self.lf_atten_1_entry.get(),
                                                _lf_atten_2_entry=self.lf_atten_2_entry.get(),
                                                _lf_atten_3_entry=self.lf_atten_3_entry.get(),
                                                _lf_email_entry=self.lf_email_entry.get(),
                                                _lf_email_production_entry=self.lf_email_production_entry.get())

      rig_json.create()
      tkinter.messagebox.showinfo(title="success", message=self.lf_rig_file_entry_var.get() + " created")


