#!/usr/bin/env python3
'''
NAME: lf_rssi_process.py

PURPOSE: Module to Process the data that was measured during  lf_rssi_check.py , the process will take in a list of csv files
            extract the data and graph
            TODO this graphing protion may be moved to graph.py

EXAMPLE:

'''

import matplotlib.pyplot as plt
import numpy as np
import csv
import argparse
import os
import sys
import importlib
import logging


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

logger = logging.getLogger(__name__)

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")



# Exit Codes
# 0: Success
# 1: Python Error
# 2: CSV file not found
# 3: Radio disconnected before exit threshold expected RSSI; PNG will still be generated
# 4: Attempted Bandwidth HT80 used with Channel 6

class lf_rssi_process:
    def __init__(self,
                csv_file='NA',
                png_dir='NA',
                bandwidth='NA',
                channel='NA',
                antenna=0,
                path_loss_2g=26.74,  # These values are specific to RSSI testbed
                path_loss_5g=31.87,  # These values are specific to RSSI testbed

                ):
        self.CSV_FILE = csv_file  # TODO this needs to be a list for compatibility
        self.PNG_OUTPUT_DIR = png_dir
        # TODO the args are passed in as metavar so it may be looped 
        # for the module the looping takes place outside the loop so this 
        # hack will be used for now
        self.BANDWIDTH = bandwidth
        self.CHANNEL = channel
        self.ANTENNA = antenna
        self.path_loss_2g = path_loss_2g
        self.path_loss_5g = path_loss_5g
        self.BASE_PATH_LOSS = 36
        # TODO the tx_power needs to be configurable
        self.TX_POWER = 20
        # TODO make that the radios are passed in so that
        # the RSSI test may be run on any test setup
        self.CHECK_RADIOS = [0, 1, 2, 3, 4, 5, 6]  # radios to check during early exit
        self.EXIT_THRESHOLD = -85.  # expected-signal cutoff for radio-disconnect exit code

        self.set_channel_path_loss(self.CHANNEL)
        # self.csv_data not used in legacy mode
        self.csv_data = [[], [], [], [], [], [], []]

        self.atten_data = [[], [], [], [], [], [], []]
        self.signal_data = [[], [], [], [], [], [], []]

        self.ANTENNA_LEGEND = {
            0: 'Diversity (All)',
            1: 'Fixed-A (1x1)',
            4: 'AB (2x2)',
            7: 'ABC (3x3)',
            8: 'ABCD (4x4)'
        }

    # TODO this may need to be part of
    def set_channel_path_loss(self, channel):
        # TODO remove hard coded values
        # also capitalized variables
        # need to check for 2G channels
        self.CHANNEL = channel
        self.BASE_PATH_LOSS = 36
        if self.CHANNEL <= 11:
            self.BASE_PATH_LOSS = self.path_loss_2g
        elif self.CHANNEL >= 34 and self.CHANNEL <= 177:
            self.BASE_PATH_LOSS = self.path_loss_5g


    # helper functions
    def filt(self, lst):  # filter out all instances of nan
        return lst[~(np.isnan(lst))]

    def avg(self, lst):  # mean
        lst = self.filt(lst)
        return sum(lst) / len(lst) if len(lst) else np.nan

    def dev(self, lst):  # element-wise deviation from mean (not standard deviation)
        return np.abs(self.avg(lst) - lst)

    def expected_signal(self, attenuation):  # theoretical expected signal
        return self.TX_POWER - (self.BASE_PATH_LOSS + attenuation)

    # early exit for disconnected radio before threshold expected RSSI
    # TODO this should not be necessary as the data collection should skip
    # TODO
    
    def check_data(self, signal, signal_exp):
        if self.CHANNEL <= 11:
            self.CHECK_RADIOS.remove(1)  # TODO: Make generic
        elif self.CHANNEL >= 34 and self.CHANNEL <= 177:
            self.CHECK_RADIOS.remove(0)  # TODO: Make generic
        threshold_ind = np.where(signal_exp <= self.EXIT_THRESHOLD)[0][0]  # the first index where exit threshold is reached
        isnans = np.concatenate([np.isnan(e) for e in signal[0:threshold_ind, self.CHECK_RADIOS]])  # array of booleans
        if (any(isnans)):
            print(F'Warning: Radio disconnected before exit threshold expected RSSI; check {self.PNG_OUTPUT_DIR}/{self.CHANNEL}_{self.ANTENNA}_{self.BANDWIDTH}_*.png.')
            sys.exit(3)

    # TODO the original test should have taken care of skipping these tests
    # this is a check to see if lf_rssi_check.py is not functioning properly
    # check bandwidth compatibility
    def check_compatibility(self):
        if self.CHANNEL <= 11 and (self.BANDWIDTH == 80 or self.BANDWIDTH == 160):
            sys.exit(4)

    # Read in the data this probably should be generic
    def read_csv_file(self, csv_file,index):
        self.CSV_FILE = csv_file
        # read data from file
        #self.csv_data = 
        if not os.path.exists(self.CSV_FILE):
            logger.error("File not found {csv_file}".format(csv_file=self.CSV_FILE))
            sys.exit(2)
        # TODO There will be multiple lists.
        with open(self.CSV_FILE, 'r') as filename:
            reader = csv.reader(filename)
            for row in reader:
                self.csv_data[index].append(row)

    # TODO for python version there will be a list of csv file
    def populate_signal_and_attenuation_data(self,index):
        # populate signal and attenuation data
        # creating a list of lists
        # atten_data = [[], [], [], [], [], [], []]
        # signal_data = [[], [], [], [], [], [], []]
        # For our csv files only contain the data for a single station 
        
        for i in range(1, len(self.csv_data[index])):
            # for j in range(0, len(self.atten_data)):
            #    if int(self.data[i][5]) == j:
            # the numbers in the index is where the data is located in the csv file
            # attenuation data
            # attenuation is in 1/10 dBm
            self.atten_data[index].append(float(self.csv_data[index][i][11])/10)
            # signal data
            rssi = self.csv_data[index][i][17]

            rssi = rssi.replace(' dBm','')
            rssi = float(rssi)
            if rssi:            
                self.signal_data[index].append(rssi)
            else:
                self.signal_data[index].append(np.nan)
                
        logger.debug("atten_data {atten_data}".format(atten_data=self.atten_data))
        logger.debug("signal_data {signal_data}".format(signal_data=self.signal_data))

    def create_png_files(self,index):
        # remove empty list from lists
        self.atten_data = [ele for ele in self.atten_data if ele != []]
        self.signal_data = [ele for ele in self.signal_data if ele != []]
        self.csv_data = [ele for ele in self.csv_data if ele != []]

        atten = np.array(self.atten_data).T
        signal = np.array(self.signal_data).T
        signal_avg = np.array([self.avg(row) for row in signal])
        signal_exp = self.expected_signal(atten[:, 0])
        signal_dev = np.array([signal[i] - signal_exp[i] for i in range(0, len(signal))])
        signal_avg_dev = signal_exp - signal_avg

        COLORS = {
            'red': '#dc322f',
            'orange': '#cb4b16',
            'yellow': '#b58900',
            'green': '#859900',
            'blue': '#268bd2',
            'violet': '#6c71c4',
            'magenta': '#d33682',
            'cyan': '#2aa198',
            'black': '#002b36',
            'gray': '#839496',
            'dark_gray': '#073642'
        }

        color_index = {
            1 : 'red',
            2 : 'orange',
            3 : 'yellow',
            4 : 'green',
            5 : 'blue',
            6 : 'violet',
            7 : 'magenta',
            8 : 'cyan',
            9 : 'black',
            10 : 'gray',
            11 : 'dark_gray'
        }

        # TODO The legend needs to be dynamic.
        logger.debug("length of list of lists {length}".format(length=len(self.csv_data)))
        legend = {}
        # Use the number of lists to determing the legend
        # should only need to read a single sample to get the radios and not 
        # loop though all
        # TODO think of a more accurate way
        i = 1
        j = 0
        while j < index:
            #while  i <= len(self.atten_data):
            legend[self.csv_data[j][1][24]] = '{station} {radio}'.format(station=self.csv_data[j][1][24],radio=self.csv_data[j][1][25] )
            #    i += 1
            logger.debug("legend {legend}".format(legend=legend))
            j += 1
            

        plt.rc('font', family='Liberation Serif')
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(8, 8), dpi=100)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.plot(atten[:, 0], signal_exp, color=COLORS['gray'], alpha=1.0, label='Expected')
        #if self.CHANNEL <= 6:
        #    ax.plot(atten[:, 0], signal[:, 0], color=COLORS['red'], alpha=1.0, label=legend['sta0000'])  # TODO: Make generic
        #if self.CHANNEL >= 34 and self.CHANNEL <= 177:
        #  TODO Need to read the radio and creat the legend 
        # TODO needs to be dynamic Focus on 5g for now
        # TODO only capture data for radios that support the mode
        # TODO using the number of lists in self.atten_data to see how much to plot
        # TODO look for a better way 
        # The index for self.data is incremented due to column headers
        logger.debug("length of lists of lists {length}".format(length=len(self.atten_data)))
        i = 0
        j = 0
        while j < index:
            #while i < len(self.atten_data):    
            ax.plot(atten[:, j], signal[:, j], color=COLORS[color_index[j+1]], alpha=1.0, label=legend[self.csv_data[j][j+1][24]])  # TODO: Make generic
            #i += 1
            j += 1

        ax.set_title('Attenuation vs. Signal:\n'
                     + F'VAP={self.csv_data[0][1][19]}, '
                     + F'VAP Radio=TODO'
                     + F'Channel={self.CHANNEL}, '
                     + F'Bandwidth={self.BANDWIDTH}, '
                     + F'Antenna={self.ANTENNA_LEGEND[self.ANTENNA]}')
        ax.set_xlabel('Attenuation (dB)')
        ax.set_ylabel('RSSI (dBm)')
        ax.set_yticks(range(-30, -110, -5))
        ax.set_xticks(range(20, 100, 5))
        plt.grid(color=COLORS['dark_gray'], linestyle='-', linewidth=1)
        plt.legend()
        plt.savefig(F'{self.PNG_OUTPUT_DIR}/{self.CHANNEL}_{self.ANTENNA}_{self.BANDWIDTH}_signal_atten.png')

        plt.style.use('dark_background')
        fig = plt.figure(figsize=(8, 8), dpi=100)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        # if self.CHANNEL <= 11:
        #     ax.plot(atten[:, 0], signal_dev[:, 0], color=COLORS['red'], label=legend['sta0000'])
        # if self.CHANNEL >= 36 and self.CHANNEL <= 177:
        i = 0
        j = 0
        while j < index:
            # while i < len(self.atten_data):    
            ax.plot(atten[:, j], signal_dev[:, j], color=COLORS[color_index[j+1]], label=legend[self.csv_data[j][j+1][24]])            
            #i += 1
            j += 1

        ax.set_title('Atteunuation vs. Signal Deviation:\n'
                     + F'SSID={self.csv_data[0][1][19]}, '
                     + F'Channel={self.CHANNEL}, '
                     + F'Bandwidth={self.BANDWIDTH}, '
                     + F'Antenna={self.ANTENNA_LEGEND[self.ANTENNA]}')
        ax.set_xlabel('Attenuation (dB)')
        ax.set_ylabel('RSSI (dBm)')
        ax.set_yticks(range(-5, 30, 5))
        ax.set_xticks(range(20, 100, 5))
        plt.grid(color=COLORS['dark_gray'], linestyle='-', linewidth=1)
        plt.legend()
        plt.savefig(F'{self.PNG_OUTPUT_DIR}/{self.CHANNEL}_{self.ANTENNA}_{self.BANDWIDTH}_signal_deviation_atten.png')

        # TODO the chack_data will need to be modified
        # self.check_data(signal, signal_exp)
        sys.exit(0)


    # Leaving in the legacy parsing of the files 
    # generated by rssi validation
    def read_csv_file_legacy(self, csv_file):
        self.CSV_FILE = csv_file
        # read data from file
        self.data = []
        if not os.path.exists(self.CSV_FILE):
            sys.exit(2)
        # TODO There will be multiple lists.
        with open(self.CSV_FILE, 'r') as filename:
            reader = csv.reader(filename)
            for row in reader:
                self.data.append(row)

    # TODO for python version there will be a list of csv files
    # Leaving in the legacy parsing of the files 
    # generated by rssi validation

    def populate_signal_and_attenuation_data_legacy(self):
        # populate signal and attenuation data
        # creating a list of lists
        # atten_data = [[], [], [], [], [], [], []]
        # signal_data = [[], [], [], [], [], [], []]
        for i in range(1, len(self.data)):
            for j in range(0, len(self.atten_data)):
                if int(self.data[i][5]) == j:
                    # attenuation data
                    self.atten_data[j].append(float(self.data[i][0]))
                    # signal data
                    rssi = float(self.data[i][13])
                    if rssi:
                        self.signal_data[j].append(float(self.data[i][13]))
                    else:
                        self.signal_data[j].append(np.nan)

    # Leaving in the legacy parsing of the files 
    # generated by rssi validation
    def create_png_files_legacy(self):
        atten = np.array(self.atten_data).T
        signal = np.array(self.signal_data).T
        signal_avg = np.array([self.avg(row) for row in signal])
        signal_exp = self.expected_signal(atten[:, 0])
        signal_dev = np.array([signal[i] - signal_exp[i] for i in range(0, len(signal))])
        signal_avg_dev = signal_exp - signal_avg

        COLORS = {
            'red': '#dc322f',
            'orange': '#cb4b16',
            'yellow': '#b58900',
            'green': '#859900',
            'blue': '#268bd2',
            'violet': '#6c71c4',
            'magenta': '#d33682',
            'cyan': '#2aa198',
            'black': '#002b36',
            'gray': '#839496',
            'dark_gray': '#073642'
        }

        # TODO The legend needs to be dynamic.
        legend = {
            'sta0000': self.data[1][6],
            'sta0001': self.data[2][6],
            'sta0002': self.data[3][6],
            'sta0003': self.data[4][6],
            'sta0004': self.data[5][6],
            'sta0005': self.data[6][6],
            'sta0006': self.data[7][6]
        }

        plt.rc('font', family='Liberation Serif')
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(8, 8), dpi=100)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.plot(atten[:, 0], signal_exp, color=COLORS['gray'], alpha=1.0, label='Expected')
        if self.CHANNEL <= 6:
            ax.plot(atten[:, 0], signal[:, 0], color=COLORS['red'], alpha=1.0, label=legend['sta0000'])  # TODO: Make generic
        if self.CHANNEL >= 34 and self.CHANNEL <= 177:
            ax.plot(atten[:, 1], signal[:, 1], color=COLORS['orange'], alpha=1.0, label=legend['sta0001'])  # TODO: Make generic
        ax.plot(atten[:, 2], signal[:, 2], color=COLORS['yellow'], alpha=1.0, label=legend['sta0002'])
        ax.plot(atten[:, 3], signal[:, 3], color=COLORS['green'], alpha=1.0, label=legend['sta0003'])
        ax.plot(atten[:, 4], signal[:, 4], color=COLORS['cyan'], alpha=1.0, label=legend['sta0004'])
        ax.plot(atten[:, 5], signal[:, 5], color=COLORS['blue'], alpha=1.0, label=legend['sta0005'])
        ax.plot(atten[:, 6], signal[:, 6], color=COLORS['violet'], alpha=1.0, label=legend['sta0006'])
        ax.set_title('Attenuation vs. Signal:\n'
                     + F'SSID={self.data[7][14]}, '
                     + F'Channel={self.CHANNEL}, '
                     + F'Bandwidth={self.BANDWIDTH}, '
                     + F'Antenna={self.ANTENNA_LEGEND[self.ANTENNA]}')
        ax.set_xlabel('Attenuation (dB)')
        ax.set_ylabel('RSSI (dBm)')
        ax.set_yticks(range(-30, -110, -5))
        ax.set_xticks(range(20, 100, 5))
        plt.grid(color=COLORS['dark_gray'], linestyle='-', linewidth=1)
        plt.legend()
        plt.savefig(F'{self.PNG_OUTPUT_DIR}/{self.CHANNEL}_{self.ANTENNA}_{self.BANDWIDTH}_signal_atten.png')

        plt.style.use('dark_background')
        fig = plt.figure(figsize=(8, 8), dpi=100)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        if self.CHANNEL <= 11:
            ax.plot(atten[:, 0], signal_dev[:, 0], color=COLORS['red'], label=legend['sta0000'])
        if self.CHANNEL >= 36 and self.CHANNEL <= 177:
            ax.plot(atten[:, 1], signal_dev[:, 1], color=COLORS['orange'], label=legend['sta0001'])
        ax.plot(atten[:, 2], signal_dev[:, 2], color=COLORS['yellow'], label=legend['sta0002'])
        ax.plot(atten[:, 2], signal_dev[:, 3], color=COLORS['green'], label=legend['sta0003'])
        ax.plot(atten[:, 2], signal_dev[:, 4], color=COLORS['cyan'], label=legend['sta0004'])
        ax.plot(atten[:, 2], signal_dev[:, 5], color=COLORS['blue'], label=legend['sta0005'])
        ax.plot(atten[:, 2], signal_dev[:, 6], color=COLORS['violet'], label=legend['sta0006'])
        ax.set_title('Atteunuation vs. Signal Deviation:\n'
                     + F'SSID={self.data[7][14]}, '
                     + F'Channel={self.CHANNEL}, '
                     + F'Bandwidth={self.BANDWIDTH}, '
                     + F'Antenna={self.ANTENNA_LEGEND[self.ANTENNA]}')
        ax.set_xlabel('Attenuation (dB)')
        ax.set_ylabel('RSSI (dBm)')
        ax.set_yticks(range(-5, 30, 5))
        ax.set_xticks(range(20, 100, 5))
        plt.grid(color=COLORS['dark_gray'], linestyle='-', linewidth=1)
        plt.legend()
        plt.savefig(F'{self.PNG_OUTPUT_DIR}/{self.CHANNEL}_{self.ANTENNA}_{self.BANDWIDTH}_signal_deviation_atten.png')

        self.check_data(signal, signal_exp)
        sys.exit(0)

# Starting point for running this from cmd line.
# note: when adding command line delimiters : +,=@
# https://stackoverflow.com/questions/37304799/cross-platform-safe-to-use-command-line-string-separator


def main():
    parser = argparse.ArgumentParser(
        prog='lf_rssi_process.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            # Exit Codes
            # 0: Success
            # 1: Python Error
            # 2: CSV file not found
            # 3: Radio disconnected before exit threshold expected RSSI; PNG will still be generated
            # 4: Attempted Bandwidth HT80 used with Channel 6
        ''',
        description='''\
        lf_rssi_process.py:
        --------------------
        '''
    )
    #parser = argparse.ArgumentParser(description='Input and output files.')
    parser.add_argument('--csv', action="append",  help='../output.csv')
    parser.add_argument('--png_dir', metavar='o', type=str, help='../PNGs')
    # TODO read the bandwidth from the csv data
    parser.add_argument('--bandwidth', metavar='b', type=int, help='20, 40, 80')
    parser.add_argument('--channel', metavar='c', type=int, help='6, 36')
    parser.add_argument('--antenna', metavar='a', type=int, help='0, 1, 4, 7, 8')
    parser.add_argument('--path_loss_2', metavar='p', type=float, help='26.74')
    parser.add_argument('--path_loss_5', metavar='q', type=float, help='31.87')
    parser.add_argument('--legacy', help='--lagacy will enable legacy csv parsing', action="store_true")
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    # logging configuration
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")



    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    # CSV_FILE = args.csv
    # PNG_OUTPUT_DIR = args.png_dir
    # BANDWIDTH = args.bandwidth
    # CHANNEL = args.channel
    # ANTENNA = args.antenna

    rssi_process = lf_rssi_process(
                                    csv_file=args.csv,
                                    png_dir=args.png_dir,
                                    bandwidth = args.bandwidth,
                                    channel = args.channel,
                                    antenna = args.antenna,
                                    path_loss_2g=args.path_loss_2,
                                    path_loss_5g=args.path_loss_5,
                                    )

    if args.legacy:
        rssi_process.read_csv_file_legacy(args.csv)
        rssi_process.populate_signal_and_attenuation_data_legacy()
        rssi_process.create_png_files_legacy()                                   
    else:   
        csv_num = 0
        for csv in args.csv:
            
            # hard code the index will need to base it on a csv list
            rssi_process.read_csv_file(csv, index=csv_num)
            # TODO hard code the index while debugging
            # may have to use another method from the calling routine
            rssi_process.populate_signal_and_attenuation_data(index=csv_num)
            csv_num += 1                                 

        
        # TODO index should be the number of stations connected to the VAP
        rssi_process.create_png_files(index=csv_num)  

            


if __name__ == "__main__":
    main()
