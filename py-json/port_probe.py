#!/usr/bin/env python3
import importlib
from time import sleep
import pandas as pd
import sys
import os
from pprint import pprint


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase


# Probe data can change frequently. It is recommended to update

class ProbePort(LFCliBase):
    def __init__(self,
                 lfhost=None,
                 lfport='8080',
                 debug=False,
                 eid_str=None):
        super().__init__(_lfjson_host=lfhost,
                         _lfjson_port=lfport,
                         _debug=debug)
        hunks = eid_str.split(".")
        self.eid_str = eid_str
        self.probepath = "/probe/1/%s/%s" % (hunks[-2], hunks[-1])
        self.response = None
        self.signals = None
        self.he = None

        self.tx_bitrate = None
        self.tx_mcs = None
        self.tx_nss = None
        self.tx_mbit = None
        self.tx_mhz = None
        self.tx_ns = None
        self.tx_duration = None
        self.tx_data_rate_gi_short_Mbps = None
        self.tx_data_rate_gi_long_Mbps = None

        self.rx_bitrate = None
        self.rx_actual_mcs = None
        self.rx_mcs = None
        self.rx_nss = None
        self.rx_mbit = None
        self.rx_mhz = None
        self.rx_ns = None
        self.rx_duration = None
        self.rx_data_rate_gi_short_Mbps = None
        self.rx_data_rate_gi_long_Mbps = None

        self.data_rate = None
        folder = os.path.dirname(__file__)

    def refreshProbe(self):
        self.json_post(self.probepath, {})
        sleep(0.2)
        response = self.json_get(self.probepath)
        self.response = response
        if self.debug:
            print("probepath (eid): {probepath}".format(probepath=self.probepath))
            pprint("Probe response: {response}".format(response=self.response))
        text = self.response['probe-results'][0][self.eid_str]['probe results'].split('\n')
        signals = [x.strip('\t').split('\t') for x in text if 'signal' in x]
        keys = [x[0].strip(' ').strip(':') for x in signals]
        values = [x[1].strip('dBm').strip(' ') for x in signals]
        self.signals = dict(zip(keys, values))

        tx_bitrate = [x for x in text if 'tx bitrate' in x][0].replace('\t', ' ')
        print("tx_bitrate {tx_bitrate}".format(tx_bitrate=tx_bitrate))
        self.tx_bitrate = tx_bitrate.split(':')[-1].strip(' ')
        self.tx_nss = [x.strip('\t') for x in text if 'tx bitrate' in x][0].split('NSS')[1].strip(' ')
        print("tx_nss {tx_nss}".format(tx_nss=self.tx_nss))
        self.tx_mhz  = [x.strip('\t') for x in text if 'tx bitrate' in x][0].split('MHz')[0].rsplit(' ')[-1].strip(' ')
        print("tx_mhz {tx_mhz}".format(tx_mhz=self.tx_mhz))
        rx_bitrate = [x for x in text if 'rx bitrate' in x][0].replace('\t', ' ')
        print("rx_bitrate {rx_bitrate}".format(rx_bitrate=rx_bitrate))
        self.rx_bitrate = rx_bitrate.split(':')[-1].strip(' ')

        try:
            tx_mcs = [x.strip('\t') for x in text if 'tx bitrate' in x][0].split(':')[1].strip('\t')
            self.tx_mcs = int(tx_mcs.split('MCS')[1].strip(' ').split(' ')[0])
            print("self.tx_mcs {tx_mcs}".format(tx_mcs=self.tx_mcs))
            self.tx_mbit = float(self.tx_bitrate.split(' ')[0])
            self.calculated_data_rate_tx_HT()

        except IndexError as error:
            print(error)

        try:
            rx_mcs = [x.strip('\t') for x in text if 'rx bitrate' in x][0].split(':')[1].strip('\t')
            self.rx_mcs = int(rx_mcs.split('MCS')[1].strip(' ').split(' ')[0])
            self.rx_actual_mcs = self.rx_mcs & 8
            self.rx_mbit = self.rx_bitrate.split(' ')[0]
            if 'HE not supported' in [x.strip('\t') for x in text if 'HE' in x]:
                self.he = False
            else:
                self.he = True
        except IndexError as error:
            print(error)

    def getSignalAvgCombined(self):
        return self.signals['signal avg'].split(' ')[0]

    def getSignalAvgPerChain(self):
        return ' '.join(self.signals['signal avg'].split(' ')[1:])

    def getSignalCombined(self):
        return self.signals['signal'].split(' ')[0]

    def getSignalPerChain(self):
        return ' '.join(self.signals['signal'].split(' ')[1:])

    def getBeaconSignalAvg(self):
        return ' '.join(self.signals['beacon signal avg']).replace(' ', '')

    def calculated_data_rate_tx_HT(self):
        # TODO compare with standard for 40 MHz if values change
        N_sd = 0 # Number of Data Subcarriers based on modulation and bandwith 
        N_bpscs = 0# Number of coded bits per Subcarrier(Determined by the modulation, MCS) 
        R = 0 # coding ,  (Determined by the modulation, MCS )
        N_ss = 0 # Number of Spatial Streams
        T_dft = 3.2 * 10**-6  # Constant for HT
        T_gi_short = .4 * 10**-6 # Guard index.
        T_gi_long = .8 * 10**-6 # Guard index.
        # Note the T_gi is not exactly know so need to calculate bothh with .4 and .8
        # the nubmer of Data Subcarriers is based on modulation and bandwith
        try:
            bw = int(self.tx_mhz)
        except BaseException:
            print("port_probe.py:  {} WARNING unable to parse tx MHz (BW) , check probe output will use ")

        print("Mhz {Mhz}".format(Mhz=self.tx_mhz))
        if bw == 20:
            N_sd = 52
        elif bw == 40:
            N_sd = 108
        elif bw == 80:
            N_sd = 234
        elif bw == 160:
            N_sd = 468
        else:
            print("bw needs to be know")
            exit(1)

        # NSS 
        N_ss = self.tx_nss
        # MCS (Modulation Coding Scheme) determines the constands
        # MCS 0 == Modulation BPSK R = 1/2 ,  N_bpscs = 1, 
        # Only for HT configuration 
        if self.tx_mcs == 0:
            R = 1/2
            N_bpscs = 1
        # MCS 1 == Modulation QPSK R = 1/2 , N_bpscs = 2
        elif self.tx_mcs == 1:
            R = 1/2
            N_bpscs = 2
        # MCS 2 == Modulation QPSK R = 3/4 , N_bpscs = 2
        elif self.tx_mcs == 2:
            R = 3/4
            N_bpscs = 2
        # MCS 3 == Modulation 16-QAM R = 1/2 , N_bpscs = 4
        elif self.tx_mcs == 3:
            R = 1/2
            N_bpscs = 4
        # MCS 4 == Modulation 16-QAM R = 3/4 , N_bpscs = 4
        elif self.tx_mcs == 4:
            R = 3/4
            N_bpscs = 4
        # MCS 5 == Modulation 64-QAM R = 2/3 , N_bpscs = 6
        elif self.tx_mcs == 5:
            R = 2/3
            N_bpscs = 6
        # MCS 6 == Modulation 64-QAM R = 3/4 , N_bpscs = 6
        elif self.tx_mcs == 6:
            R = 3/4
            N_bpscs = 6
        # MCS 7 == Modulation 64-QAM R = 5/6 , N_bpscs = 6
        elif self.tx_mcs == 7:
            R = 5/6
            N_bpscs = 6

        print("mcs {mcs} N_sd {N_sd} N_bpscs {N_bpscs} R {R} N_ss {N_ss}  T_dft {T_dft} T_gi_short {T_gi_short}".format(
            mcs=self.tx_mcs,N_sd=N_sd,N_bpscs=N_bpscs,R=R,N_ss=N_ss,T_dft=T_dft,T_gi_short=T_gi_short))

        self.tx_data_rate_gi_short_Mbps = ((N_sd * N_bpscs * R * float(N_ss)) / (T_dft + T_gi_short))/1000000
        print("data_rate gi_short {data_rate} Mbit/s".format(data_rate=self.tx_data_rate_gi_short_Mbps))

        print("mcs {mcs} N_sd {N_sd} N_bpscs {N_bpscs} R {R} N_ss {N_ss}  T_dft {T_dft} T_gi_long {T_gi_long}".format(
            mcs=self.tx_mcs,N_sd=N_sd,N_bpscs=N_bpscs,R=R,N_ss=N_ss,T_dft=T_dft,T_gi_long=T_gi_long))

        self.tx_data_rate_gi_long_Mbps = ((N_sd * N_bpscs * R * float(N_ss)) / (T_dft + T_gi_long))/1000000
        print("data_rate gi_long {data_rate} Mbps".format(data_rate=self.tx_data_rate_gi_long_Mbps))