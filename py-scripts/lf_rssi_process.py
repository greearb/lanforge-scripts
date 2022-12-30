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
                csv_file_list='NA',
                png_dir='NA',
                bandwidths_list='NA',
                channel_list='NA',
                antenna_list=0,
                pathloss_list='NA'
                ):
        self.csv_file_list = csv_file_list
        self.num_station_csv = len(self.csv_file_list)
        self.CSV_FILE = csv_file_list  # TODO this needs to be a list for compatibility
        self.PNG_OUTPUT_DIR = png_dir
        # TODO the args are passed in as metavar so it may be looped 
        # for the module the looping takes place outside the loop so this 
        # hack will be used for now
        self.bandwidths_list = bandwidths_list
        self.BANDWIDTH = 'NA'
        self.channel_list= channel_list
        self.CHANNEL = 'NA'
        self.antenna_list = antenna_list
        self.ANTENNA = 'NA'
        self.pathloss_list = pathloss_list
        self.BASE_PATH_LOSS = 36
        # TODO the tx_power needs to be configurable
        self.TX_POWER = 20
        # TODO make that the radios are passed in so that
        # the RSSI test may be run on any test setup
        self.CHECK_RADIOS = [0, 1, 2, 3, 4, 5, 6]  # radios to check during early exit
        self.EXIT_THRESHOLD = -85.  # expected-signal cutoff for radio-disconnect exit code

        # self.csv_data not used in legacy mode
        self.csv_data = [[], [], [], [], [], [], []]

        self.atten_data = [[], [], [], [], [], [], []]
        self.signal_data = [[], [], [], [], [], [], []]

        self.ANTENNA_LEGEND = {
            '0': 'Diversity (All)',
            '1': 'Fixed-A (1x1)',
            '4': 'AB (2x2)',
            '7': 'ABC (3x3)',
            '8': 'ABCD (4x4)'
        }

    # TODO this may need to be part of
    def set_channel_path_loss(self):
        # TODO remove hard coded values
        # also capitalized variables
        # need to check for 2G channels
    
        self.BASE_PATH_LOSS = 36
        if int(self.CHANNEL) <= 11:
            self.BASE_PATH_LOSS = float(self.pathloss_list[0])
        elif int(self.CHANNEL) >= 34 and int(self.CHANNEL) <= 177:
            self.BASE_PATH_LOSS = float(self.pathloss_list[1])


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

    # Read in all csv file data
    def read_all_csv_files(self):
        csv_file_index = 0
        for csv_file in self.csv_file_list:
        #self.csv_data = 
            if not os.path.exists(csv_file):
                logger.error("File not found {csv_file}".format(csv_file=csv_file))
                sys.exit(2)
            # TODO There will be multiple lists.
            with open(csv_file, 'r') as filename:
                reader = csv.reader(filename)
                for row in reader:
                    self.csv_data[csv_file_index].append(row)

            csv_file_index += 1                    


    # Read in the data this probably should be generic
    # TODO remove not used
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

    def populate_signal_and_attenuation_data_create_png(self):
        # Each station has its own csv file 
        data_index  = (len(self.csv_file_list) - 1)

        for channel in self.channel_list:
            self.CHANNEL = channel
            self.set_channel_path_loss()


            for bandwidth in self.bandwidths_list:
                # used for title
                self.BANDWIDTH = bandwidth

                for antenna in self.antenna_list:
                    self.ANTENNA = antenna

                    self.atten_data = [[], [], [], [], [], [], []]
                    self.signal_data = [[], [], [], [], [], [], []]
                    
                    # csv_index is the all the csv data for an individual station
                    for csv_index in range (0, len(self.csv_file_list)  ):
                        # run index is the data collected for a specific run
                        for run_index in range(1, len(self.csv_data[csv_index])):

                            # attenuation data
                            # attenuation is in 1/10 dBm
                            # position 11 in csv is the attenuation location counting from zero
                            logger.debug("bandwidth {bw} csv bandwidth {csv_bw}".format(bw=bandwidth,csv_bw=self.csv_data[csv_index][run_index][29]))
                            if self.csv_data[csv_index][run_index][29] == bandwidth:
                                self.atten_data[csv_index].append(float(self.csv_data[csv_index][run_index][11])/10)
                                # signal data is position 17
                                rssi = self.csv_data[csv_index][run_index][17]

                                rssi = rssi.replace(' dBm','')
                                rssi = float(rssi)
                                if rssi:            
                                    self.signal_data[csv_index].append(rssi)
                                else:
                                    self.signal_data[csv_index].append(np.nan)

                                logger.debug("csv_index: {csv} run_index: {run}".format(csv=csv_index,run=run_index))
                                
                        logger.debug("channel: {channel} bandwidth: {bandwidth} antenna: {antenna} atten_data: {atten_data}".format(channel=self.CHANNEL,bandwidth=self.BANDWIDTH,antenna=self.ANTENNA,atten_data=self.atten_data))
                        logger.debug("channel: {channel} bandwidth: {bandwidth} antenna: {antenna} signal_data: {signal_data}".format(channel=self.CHANNEL,bandwidth=self.BANDWIDTH,antenna=self.ANTENNA,signal_data=self.signal_data))

                    # all the data is now ready to create png for specific bandwidth
                    self.create_png_files(index=data_index)
            
    # TODO the index is actually the total number of stations that 
    # the csv data was gathered from
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
        j = 0 # csv data index starting a zero
        while j <= index:
            # we are reading the station and radio from the csv ,
            # this should be fixed in the csv so o.k. to read from the same spot
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

        logger.info("plotting Attenuation vs. Signal ")
        j = 0 # csv data index starting a zero, this is the number of csv files each csv file corresponds to one station
        while j <= index:
            ax.plot(atten[:, j], signal[:, j], color=COLORS[color_index[j+1]], alpha=1.0, label=legend[self.csv_data[j][j+1][24]])  # TODO: Make generic
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
        plt.savefig(F'{self.PNG_OUTPUT_DIR}/{self.CHANNEL}_{self.BANDWIDTH}_{self.ANTENNA}_signal_atten.png')

        plt.style.use('dark_background')
        fig = plt.figure(figsize=(8, 8), dpi=100)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        # if self.CHANNEL <= 11:
        #     ax.plot(atten[:, 0], signal_dev[:, 0], color=COLORS['red'], label=legend['sta0000'])
        # if self.CHANNEL >= 36 and self.CHANNEL <= 177:
        i = 0
        j = 0
        while j <= index:
            ax.plot(atten[:, j], signal_dev[:, j], color=COLORS[color_index[j+1]], label=legend[self.csv_data[j][j+1][24]])            
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

        logger.debug(F'{self.PNG_OUTPUT_DIR}/{self.CHANNEL}_{self.ANTENNA}_{self.BANDWIDTH}_signal_deviation_atten.png')
        # TODO the chack_data will need to be modified
        # self.check_data(signal, signal_exp)
        # sys.exit(0)



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
    parser.add_argument('--bandwidths', help='--bandwidths  list of bandwidths "20 40 80 160" space separated, default : "20" ', default='20')
    parser.add_argument('--channels', help='--channels  list of channels "6 36" space separated, default: "36" ', default='36')
    parser.add_argument('--antennas', help='''
                        --antennas list of antennas "0, 1, 4, 7, 8"  default: 
                                self.ANTENNA_LEGEND = {
                                    0: 'Diversity (All)',
                                    1: 'Fixed-A (1x1)',
                                    4: 'AB (2x2)',
                                    7: 'ABC (3x3)',
                                    8: 'ABCD (4x4)'
                                }
                                default is 0
                        ''', default= 0)
    parser.add_argument('--pathloss_list', help='list of path loss for 2g, 5g, 6g default: 26.74 31.87 0',default='26.74 31.87 0')
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

    bandwidths_list = args.bandwidths.split()        
    channel_list = args.channels.split()        
    antenna_list = args.antennas.split()  
    pathloss_list = args.pathloss_list.split() 


    # CSV_FILE = args.csv
    # PNG_OUTPUT_DIR = args.png_dir
    # BANDWIDTH = args.bandwidth
    # CHANNEL = args.channel
    # ANTENNA = args.antenna

    rssi_process = lf_rssi_process(
                                    csv_file_list=args.csv,
                                    png_dir=args.png_dir,
                                    bandwidths_list = bandwidths_list,
                                    channel_list = channel_list,
                                    antenna_list = antenna_list,
                                    pathloss_list = pathloss_list,
                                    )



    rssi_process.read_all_csv_files()
    # using the csv as a count 
    # process the collected csv data
    rssi_process.populate_signal_and_attenuation_data_create_png()

            

if __name__ == "__main__":
    main()
