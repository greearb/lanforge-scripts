#!/usr/bin/env python3

import tkinter
from tkinter import messagebox
from tkinter import ttk
import importlib
import sys
import os
import logging
import argparse
import traceback


try:
    import Pmw
except Exception as x:
    traceback.print_exception(
        Exception, x, x.__traceback__, chain=True)
    print("Pmw module needed, Please do: pip install Pmw ")
    exit(1)


if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

lf_rig_tab = importlib.import_module("lf_create_rig_tab")
lf_radio_frame = importlib.import_module("lf_create_radio_frame")
lf_dut_tab = importlib.import_module("lf_create_dut_tab")
lf_wc_tab = importlib.import_module("lf_create_wc_tab")
lf_ap_auto_tab = importlib.import_module("lf_create_ap_auto_tab")
lf_dp_rvr_tab = importlib.import_module("lf_create_dp_rvr_tab")
lf_create_wc_json = importlib.import_module("lf_create_wc_json")
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
        self.tabControl.add(self.ap_auto_tab, text='AP Auto Beta')
        # self.tabControl.add(self.functional_tab, text = 'Functional Tests')
        # self.tabControl.add(self.creation_tab, text = 'Creation Tests')
        # self.tabControl.add(self.interop_tab, text = 'Interop Tests')

        # self.tabControl.add(self.practice_tab, text = 'Pratice Tests')
        # self.tabControl.add(self.practice_tab, text = 'Practice') # Please Do not Delete.
        self.tabControl.pack(expand=1, fill="both")

        self.file_2g = ""
        self.file_5g = ""
        self.file_6g = ""

        # -----------------------------------------------------------------------------------
        #
        #  Create Rig Json
        #
        # ------------------------------------------------------------------------------------
        self.lf_rig_frame = lf_rig_tab.lf_create_rig_tab(self.rig_tab, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #
        #  End of Create Rig Json
        #
        # ------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------
        #
        #  Create DUT json
        #
        # ------------------------------------------------------------------------------------
        self.lf_dut_tab = lf_dut_tab.lf_create_dut_tab(self.dut_tab, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #
        #  END Create DUT json
        #
        # ------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------
        #
        #  Create Radios
        #
        # ------------------------------------------------------------------------------------
        self.lf_radio_frame = lf_radio_frame.lf_create_radio_frame(self.rig_tab, self.lf_rig_frame, self.max_radios, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #
        #  End of Create Radios
        #
        # ------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------
        #
        #  Create Wifi Capacity
        #
        # ------------------------------------------------------------------------------------
        lf_wc_tab.lf_create_wc_tab(self.wc_tab, self.lf_dut_tab, self.lf_radio_frame, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #
        #  End Wifi Capacity
        #
        # ------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------
        #
        #  Create Data Plane or RvR
        #
        # ------------------------------------------------------------------------------------
        lf_dp_rvr_tab.lf_create_dp_rvr_tab(self.dp_rvr_tab, self.lf_dut_tab, self.lf_radio_frame, self.window_tooltip, self.current_working_directory)

        # -----------------------------------------------------------------------------------
        #
        #  Create AP Auto Tests
        #
        # ------------------------------------------------------------------------------------
        lf_ap_auto_tab.lf_create_ap_auto_tab(self.ap_auto_tab, self.lf_dut_tab, self.lf_radio_frame, self.window_tooltip, self.current_working_directory)

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
    ./lf_check_json_gen.py --radio_count 12 --log_level debug



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
    parser.add_argument('--log_level', help='Set logging level: debug | info | warning | error | critical')

    args = parser.parse_args()
    logger_config = lf_logger_config.lf_logger_config()
    if args.log_level:
        logger_config.set_level(level=args.log_level)
    else:
        # for now default to debug
        logger_config.set_level(level='debug')

    _radio_count = args.radio_count

    # my_gui = json_gen_gui(radio_count=int(_radio_count))
    json_gen_gui(radio_count=int(_radio_count))
    # TODO allow log level to be sets


if __name__ == '__main__':
    main()
