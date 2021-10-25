#!/usr/bin/env python3
import importlib
from time import sleep
import pandas as pd
import sys
import os

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

        self.rx_bitrate = None
        self.rx_actual_mcs = None
        self.rx_mcs = None
        self.rx_nss = None
        self.rx_mbit = None
        self.rx_mhz = None
        self.rx_ns = None
        self.rx_duration = None
        self.data_rate = None
        folder = os.path.dirname(__file__)
        self.df = pd.read_csv(os.path.join(folder, "mcs_snr_rssi.csv"))

    def refreshProbe(self):
        self.json_post(self.probepath, {})
        sleep(0.2)
        response = self.json_get(self.probepath)
        self.response = response
        if self.debug:
            print(self.probepath)
            print(response)
        text = self.response['probe-results'][0][self.eid_str]['probe results'].split('\n')
        signals = [x.strip('\t').split('\t') for x in text if 'signal' in x]
        keys = [x[0].strip(' ').strip(':') for x in signals]
        values = [x[1].strip('dBm').strip(' ') for x in signals]
        self.signals = dict(zip(keys, values))
        tx_bitrate = [x for x in text if 'tx bitrate' in x][0].replace('\t', ' ')
        self.tx_bitrate = tx_bitrate.split(':')[-1].strip(' ')
        rx_bitrate = [x for x in text if 'rx bitrate' in x][0].replace('\t', ' ')
        self.rx_bitrate = rx_bitrate.split(':')[-1].strip(' ')

        try:
            tx_mcs = [x.strip('\t') for x in text if 'tx bitrate' in x][0].split(':')[1].strip('\t')
            self.tx_mcs = int(tx_mcs.split('MCS')[1].strip(' ').split(' ')[0])
            self.tx_mbit = float(self.tx_bitrate.split(' ')[0])
            if 'VHT' in self.tx_bitrate:
                tx_mhz_ns = self.vht_calculator(self.tx_mbit, self.tx_mcs)
                try:
                    self.tx_mhz = tx_mhz_ns['MHz']
                    self.tx_nss = [x.strip('\t') for x in text if 'tx bitrate' in x][0].split('VHT-NSS')[1].strip(' ')
                    self.tx_ns = tx_mhz_ns['ns']
                    self.tx_duration = float([x for x in text if 'tx duration' in x][0].split('\t')[1].split(' ')[0])
                except TypeError as error:
                    print('%s, %s' % (error, tx_mhz_ns))
            else:
                tx_mhz_ns = self.ht_calculator(self.tx_mbit, self.tx_mcs)
                self.df.index = self.df['HT']
                nbpscs = self.df['Modulation'][self.tx_mcs]
                coding = self.df['Coding'][self.tx_mcs]
                tdft = 168.35
                if 'short GI' in self.tx_bitrate:
                    tgi = 0.4
                else:
                    tgi = 0.8
                self.data_rate = (self.tx_mbit * nbpscs * coding * self.tx_nss) / (tdft + tgi)
                try:
                    self.tx_mhz = tx_mhz_ns['MHz']
                    self.tx_nss = int(self.tx_mcs / 8) + 1
                    self.tx_ns = tx_mhz_ns['ns']
                except TypeError:
                    print('tx_mhz_ns is None')
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
            if 'VHT' in self.rx_bitrate:
                rx_mhz_ns = self.vht_calculator(self.rx_mbit, self.rx_mcs)
                try:
                    self.rx_mhz = rx_mhz_ns['MHz']
                    self.rx_nss = [x.strip('\t') for x in text if 'rx bitrate' in x][0].split('VHT-NSS')[1].strip(' ')
                    self.rx_ns = rx_mhz_ns['ns']
                    self.rx_duration = float([x for x in text if 'rx duration' in x][0].split('\t')[1].split(' ')[0])
                except TypeError as error:
                    print('%s, %s' % (error, rx_mhz_ns))
            else:
                rx_mhz_ns = self.ht_calculator(self.rx_mbit, self.rx_mcs)
                self.df.index = self.df['HT']
                nbpscs = self.df['Modulation'][self.rx_mcs]
                coding = self.df['Coding'][self.rx_mcs]
                tdft = 168.35
                if 'short GI' in self.rx_bitrate:
                    tgi = 0.4
                else:
                    tgi = 0.8
                self.data_rate = (self.rx_mbit * nbpscs * coding * self.rx_nss) / (tdft + tgi)
                try:
                    self.rx_mhz = rx_mhz_ns['MHz']
                    self.rx_nss = int(self.rx_mcs / 8) + 1
                    self.rx_ns = rx_mhz_ns['ns']
                except TypeError:
                    print('rx_mhz_nz not found')
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

    def ht_calculator(self, mbit, mcs):
        df1 = self.df[self.df['HT'] == mcs]
        df1.index = df1['HT']
        values = df1.transpose().to_dict()[mcs]
        result = {k: v for (k, v) in values.items() if v == str(mbit)}.keys()
        results = list(result)[0].split(',')
        response = dict()
        try:
            for value in results:
                if 'MHz' in value:
                    response['MHz'] = value.strip('MHz')
                if 'µs GI' in value:
                    response['ns'] = value.strip('µs GI')
            return response
        except KeyError:
            self.vht_calculator(mbit, mcs)

    def vht_calculator(self, mbit, mcs):
        df = self.df[self.df['VHT'] == mcs]
        results = pd.concat([pd.DataFrame(x.items()) for x in df.transpose().to_dict().values()]).dropna()
        result = list(results[results[1] == str(mbit)][0])[0]
        response = dict()
        try:
            for value in result.split(','):
                if 'MHz' in value:
                    response['MHz'] = value.strip('MHz')
                if 'µs GI' in value:
                    response['ns'] = value.strip('µs GI')
            return response
        except KeyError as error:
            print(error)
            print('mbit: %s, mcs: %s' % (mbit, mcs))

    def ofdma_calculator(self, mbit, mcs):
        df = self.df[self.df['VHT'] == mcs]
        data_rate = (mbit * nbpscs * cding * nss) / (tdft + tgi)
        return data_rate
