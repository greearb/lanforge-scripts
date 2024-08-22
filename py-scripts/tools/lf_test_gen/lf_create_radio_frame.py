import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import StringVar
import importlib
import requests
import logging


logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


class lf_create_radio_frame():
   def __init__(self, rig_tab, rig_frame, max_radios, window_tooltip, current_working_directory):
      self.rig_tab = rig_tab
      self.rig_frame = rig_frame
      self.max_radios = max_radios
      self.window_tooltip = window_tooltip
      self.current_working_directory = current_working_directory

      # -----------------------------------------------------------------------------------
      #
      #  Create Radios
      #
      # ------------------------------------------------------------------------------------

      # create then either pack, place, grid
      self.radio_frame = tkinter.Frame(self.rig_tab)
      self.radio_frame.pack()

      # lanforge Radio Information
      self.lf_radio_frame = tkinter.LabelFrame(self.radio_frame, text="Radio Information")
      self.lf_radio_frame.grid(row=1, column=0, sticky="news", padx=20, pady=10)

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
      self.radio_type_list = ["", "AX200_abgn_AX", "AX210_abgn_AX", "MTK7915_abgn_AX", "MTK7921_abgn_AX", "ATH9K_abgn", "ATH10K_bgn_AC", "ATH10K_an_AC"]

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

      for radio in range(0, self.max_radios):

         use_radio_var = tkinter.StringVar(value="Do Not Use")
         self.use_radio_var_dict[radio] = use_radio_var
         use_radio_check = tkinter.Checkbutton(self.lf_radio_frame, text="Use Radio", variable=self.use_radio_var_dict[radio],
                                                onvalue="Use", offvalue="Do Not Use")
         use_radio_check.grid(row=radio + 2, column=0)

         radio_entry_var = tkinter.StringVar()
         self.radio_dict[radio] = radio_entry_var
         radio_entry_var.set("")
         radio_entry = tkinter.Entry(self.lf_radio_frame, textvariable=self.radio_dict[radio])
         radio_entry.grid(row=radio + 2, column=1)
         self.window_tooltip.bind(radio_entry, 'Enter LANforge radio shelf.resource.radio, example: 1.1.wiphy0')

         radio_type_entry_var = tkinter.StringVar()
         self.radio_type_dict[radio] = radio_type_entry_var
         radio_type_entry_var.set("")
         radio_type_entry = tkinter.Entry(self.lf_radio_frame, textvariable=self.radio_type_dict[radio])
         radio_type_entry.grid(row=radio + 2, column=2)
         self.window_tooltip.bind(radio_type_entry, 'Enter Radio Type, example: 802.11abgn-AX')

         radio_model_entry_var = tkinter.StringVar()
         self.radio_model_dict[radio] = radio_model_entry_var
         radio_model_entry_var.set("")
         radio_model_entry = tkinter.Entry(self.lf_radio_frame, textvariable=self.radio_model_dict[radio])
         radio_model_entry.grid(row=radio + 2, column=3)
         self.window_tooltip.bind(radio_model_entry, 'Enter Radio Model Type, example: AX210')

         radio_max_sta_entry_var = tkinter.StringVar()
         self.radio_max_sta_dict[radio] = radio_max_sta_entry_var
         radio_max_sta_entry_var.set("")
         radio_max_sta_entry = tkinter.Entry(self.lf_radio_frame, textvariable=self.radio_max_sta_dict[radio])
         radio_max_sta_entry.grid(row=radio + 2, column=4)
         self.window_tooltip.bind(radio_max_sta_entry, 'Enter Radio Maximum Stations supported')

         radio_batch_entry_var = tkinter.StringVar()
         self.radio_batch_dict[radio] = radio_batch_entry_var
         radio_batch_entry_var.set("")
         radio_batch_entry = tkinter.Entry(self.lf_radio_frame, textvariable=self.radio_batch_dict[radio])
         radio_batch_entry.grid(row=radio + 2, column=5)

         use_radio_2g_var = tkinter.StringVar(value="Do Not Use")
         self.use_radio_2g_var_dict[radio] = use_radio_2g_var
         use_radio_2g_check = tkinter.Checkbutton(self.lf_radio_frame, text="2g", variable=self.use_radio_2g_var_dict[radio],
                                                   onvalue="Use", offvalue="Do Not Use")
         use_radio_2g_check.grid(row=radio + 2, column=6)
         self.window_tooltip.bind(use_radio_2g_check, '''Read Radio info will select 2g band as capability if applicable
The check box may be selected to allow the band to be included in the test json
or deselect to remove from the test json''')

         use_radio_5g_var = tkinter.StringVar(value="Do Not Use")
         self.use_radio_5g_var_dict[radio] = use_radio_5g_var
         use_radio_5g_check = tkinter.Checkbutton(self.lf_radio_frame, text="5g", variable=self.use_radio_5g_var_dict[radio],
                                                   onvalue="Use", offvalue="Do Not Use")
         use_radio_5g_check.grid(row=radio + 2, column=7)
         self.window_tooltip.bind(use_radio_5g_check, '''Read Radio info will select 5g band as capability if applicable
The check box may be selected to allow the band to be included in the test json
or deselect to remove from the test json''')

         use_radio_6g_var = tkinter.StringVar(value="Do Not Use")
         self.use_radio_6g_var_dict[radio] = use_radio_6g_var
         use_radio_6g_check = tkinter.Checkbutton(self.lf_radio_frame, text="6g", variable=self.use_radio_6g_var_dict[radio],
                                                   onvalue="Use", offvalue="Do Not Use")
         use_radio_6g_check.grid(row=radio + 2, column=8)
         self.window_tooltip.bind(use_radio_6g_check, '''Read Radio info will select 6g band as capability if applicable
The check box may be selected to allow the band to be included in the test json
or deselect to remove from the test json''')

      self.lf_read_radio = ttk.Button(self.lf_radio_frame, text='Read Radio Info', command=self.get_lanforge_radio_information)
      self.lf_read_radio.grid(row=radio + 3, column=0, sticky="news", padx=20, pady=10)
      self.window_tooltip.bind(self.lf_read_radio, 'Read LANforge Radio Information')

      self.lf_apply_radio = ttk.Button(self.lf_radio_frame, text='Apply Radio Info', command=self.apply_lanforge_radio_information)
      self.lf_apply_radio.grid(row=radio + 3, column=1, sticky="news", padx=20, pady=10)
      self.window_tooltip.bind(self.lf_apply_radio, 'Apply Radio Information based on updates')

      self.lf_clear_radio = ttk.Button(self.lf_radio_frame, text='Clear Radio Info', command=self.clear_lanforge_radio_information)
      self.lf_clear_radio.grid(row=radio + 3, column=2, sticky="news", padx=20, pady=10)
      self.window_tooltip.bind(self.lf_clear_radio, 'Clear Radio Information')

      # Max Stations
      for widget in self.lf_radio_frame.winfo_children():
         widget.grid_configure(padx=5, pady=5)

      # -----------------------------------------------------------------------------------
      #
      #  End of Create Radios
      #
      # ------------------------------------------------------------------------------------

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
      request_command = 'http://{lfmgr}:{port}/radiostatus/all'.format(lfmgr=self.rig_frame.lf_mgr_entry_var.get(),
                                                                        port=self.rig_frame.lf_mgr_port_entry_var.get())
      request = requests.get(request_command, auth=(self.rig_frame.lf_user_entry_var.get(), self.rig_frame.lf_passwd_entry_var.get()))
      logger.debug("radio request command: {request_command}".format(request_command=request_command))
      logger.debug("radio request status_code {status}".format(status=request.status_code))
      self.lanforge_radio_json = request.json()
      logger.debug("radio request.json: {json}".format(json=self.lanforge_radio_json))
      self.lanforge_radio_text = request.text
      logger.debug("radio request.test: {text}".format(text=self.lanforge_radio_text))

      radio = 0
      self.lanforge_radio_json.pop("handler")
      self.lanforge_radio_json.pop("uri")
      self.lanforge_radio_json.pop("warnings")
      self.sorted_lanforge_radio_json = {}
      for key in sorted(self.lanforge_radio_json, key= lambda key: (key.split('y')[0],int(key.split('y')[1]))):
         self.sorted_lanforge_radio_json[key] = self.lanforge_radio_json[key]
      self.lanforge_radio_json = self.sorted_lanforge_radio_json
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
                  radio_name_tmp = radio_name_tmp.replace(' (', '_').replace(')', '')
               elif "AX2" in radio_name_tmp:
                  radio_name_tmp = radio_name_tmp.replace('iwlwifi (', '').replace(')', '')
                  radio_name_tmp = radio_name_tmp.replace('iwlwifi(', '').replace(')', '')  # Older syntax
               elif "BE2" in radio_name_tmp:
                  radio_name_tmp = radio_name_tmp.replace('iwlwifi (', '').replace(')', '')
                  radio_name_tmp = radio_name_tmp.replace('iwlwifi(', '').replace(')', '')  # Older syntax
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
      for radio in range(0, self.max_radios):
         if "Use" == self.use_radio_var_dict[radio].get():
               # the radio location may not match the radio number
               radio_number = self.radio_dict[radio].get()
               radio_number = radio_number.split('wiphy')[-1]
               if "Use" == self.use_radio_2g_var_dict[radio].get():
                  self.suite_radios_2g += "_W{}".format(radio_number)

               if "Use" == self.use_radio_5g_var_dict[radio].get():
                  self.suite_radios_5g += "_W{}".format(radio_number)

               if "Use" == self.use_radio_6g_var_dict[radio].get():
                  self.suite_radios_6g += "_W{}".format(radio_number)

      radio_message = f"2g: {self.suite_radios_2g}\n5g: {self.suite_radios_5g}\n6g: {self.suite_radios_6g}"
      tkinter.messagebox.showinfo(title="Updated", message=radio_message)

   def get_suite_radios_2g(self):
      return self.suite_radios_2g

   def get_suite_radios_5g(self):
      return self.suite_radios_5g

   def get_suite_radios_6g(self):
      return self.suite_radios_6g

   def clear_lanforge_radio_information(self):

      for radio in range(0, self.max_radios):

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






