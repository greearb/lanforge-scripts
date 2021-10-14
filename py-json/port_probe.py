#!/usr/bin/env python3
import importlib
from time import sleep
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

    def getSignalAvgCombined(self):
        return self.signals['signal avg'].split(' ')[0]

    def getSignalAvgPerChain(self):
        return ' '.join(self.signals['signal avg'].split(' ')[1:])

    def getSignalCombined(self):
        return self.signals['signal'].split(' ')[0]

    def getSignalPerChain(self):
        return ' '.join(self.signals['signal'].split(' ')[1:])

    def getBeaconSignalAvg(self):
        return ' '.join(self.signals['beacon signal avg'])
