import matplotlib.pyplot as plt
import numpy as np
import csv
from functools import reduce
import operator
import argparse
import os
import sys

# Exit Codes
# 0: Success
# 1: Python Error
# 2: CSV file not found
# 3: Radio disconnected before -80 expected RSSI; PNG will still be generated

parser = argparse.ArgumentParser(description='Input and output files.')
parser.add_argument('--csv', metavar='i', type=str, help='../output.csv')
parser.add_argument('--png_dir', metavar='o', type=str, help='../PNGs')
parser.add_argument('--bandwidth', metavar='b', type=int, help='20, 40, 80')
parser.add_argument('--channel', metavar='c', type=int, help='6, 36')
parser.add_argument('--antenna', metavar='a', type=int, help='0, 1, 4, 7, 8')

args = parser.parse_args()
CSV_FILE=args.csv
PNG_OUTPUT_DIR=args.png_dir
bandwidth = args.bandwidth
channel = args.channel
antenna = args.antenna
BASE_PATH_LOSS=36
TX_POWER=20
CHECK_RADIOS=[0,1,2,3,4,5,6]
EXIT_THRESHOLD=-85.

# helper functions
def filt(lst):
    return lst[~(np.isnan(lst))]

def avg(lst):
    lst = filt(lst)
    return sum(lst)/len(lst) if len(lst) else np.nan

def dev(lst):
    return np.abs(avg(lst) - lst)

def expected_signal(attenuation):
    return TX_POWER - (BASE_PATH_LOSS + attenuation)

def check_data(signal, signal_exp):
    if channel==6:
        CHECK_RADIOS.remove(1)
    if channel==36:
        CHECK_RADIOS.remove(0)
    threshold_ind = np.where(signal_exp==EXIT_THRESHOLD)[0][0]
    isnans = np.concatenate([np.isnan(e) for e in signal[0:threshold_ind, CHECK_RADIOS]])
    if (any(isnans)):
        sys.exit(3)

# read data from file
data=[]
if not os.path.exists(CSV_FILE):
    sys.exit(2)
with open(CSV_FILE, 'r') as filename:
    reader=csv.reader(filename)
    for row in reader:
        data.append(row)

# populate signal and attenuation data
atten_data = [[],[],[],[],[],[],[]]
signal_data = [[],[],[],[],[],[],[]]
for i in range(1, len(data)):
    for j in range(0, len(atten_data)):
        if int(data[i][5])==j:
            # attenuation data
            atten_data[j].append(float(data[i][0]))
            # signal data
            rssi = float(data[i][13])
            if rssi: signal_data[j].append(float(data[i][13]))
            else: signal_data[j].append(np.nan)

atten = np.array(atten_data).T            
signal = np.array(signal_data).T
signal_avg = np.array([avg(row) for row in signal])
signal_exp = expected_signal(atten[:,0])
signal_dev = np.array([signal[i] - signal_exp[i] for i in range(0,len(signal))])
signal_avg_dev = signal_exp - signal_avg

COLORS = {
    'red': '#dc322f',
    'orange': '#cb4b16',
    'yellow': '#b58900',
    'green': '#859900',
    'blue': '#268bd2',
    'violet':'#6c71c4',
    'magenta': '#d33682',
    'cyan': '#2aa198',
    'black': '#002b36',
    'gray': '#839496',
    'dark_gray': '#073642'
}

legend = {
    'sta0000' : data[1][6],
    'sta0001' : data[2][6],
    'sta0002' : data[3][6],
    'sta0003' : data[4][6],
    'sta0004' : data[5][6],
    'sta0005' : data[6][6],
    'sta0006' : data[7][6]
}

plt.rc('font',family='Liberation Serif')
plt.style.use('dark_background')
fig = plt.figure(figsize=(8,8),dpi=100)
ax = fig.add_axes([0.1,0.1,0.8,0.8])
ax.plot(atten[:,0],signal_exp,  color=COLORS['gray'],  alpha=1.0, label='Expected')
if channel==6:
    ax.plot(atten[:,0],signal[:,0], color=COLORS['red'],    alpha=1.0, label=legend['sta0000'])
if channel==36:
    ax.plot(atten[:,1],signal[:,1], color=COLORS['orange'], alpha=1.0, label=legend['sta0001'])
ax.plot(atten[:,2],signal[:,2], color=COLORS['yellow'], alpha=1.0, label=legend['sta0002'])
ax.plot(atten[:,3],signal[:,3], color=COLORS['green'],  alpha=1.0, label=legend['sta0003'])
ax.plot(atten[:,4],signal[:,4], color=COLORS['cyan'],   alpha=1.0, label=legend['sta0004'])
ax.plot(atten[:,5],signal[:,5], color=COLORS['blue'],   alpha=1.0, label=legend['sta0005'])
ax.plot(atten[:,6],signal[:,6], color=COLORS['violet'], alpha=1.0, label=legend['sta0006'])
ax.set_title(F'Attenuation vs. Signal:\n'
             + F'SSID={data[1][14]}, '
             + F'Channel={channel}, '
             + F'Mode={data[1][11]}')
ax.set_xlabel('Attenuation (dB)')
ax.set_ylabel('RSSI (dBm)')
ax.set_yticks(range(-30, -110, -5))
ax.set_xticks(range(20, 100, 5))
plt.grid(color=COLORS['dark_gray'], linestyle='-', linewidth=1)
plt.legend()
plt.savefig(F'{PNG_OUTPUT_DIR}/{channel}_{antenna}_{bandwidth}_signal_atten.png')

plt.style.use('dark_background')
fig = plt.figure(figsize=(8,8),dpi=100)
ax = fig.add_axes([0.1,0.1,0.8,0.8])
if channel==6:
    ax.plot(atten[:,0],signal_dev[:,0], color=COLORS['red'],     label=legend['sta0000'])
if channel==36:
    ax.plot(atten[:,1],signal_dev[:,1], color=COLORS['orange'],  label=legend['sta0001'])
ax.plot(atten[:,2],signal_dev[:,2], color=COLORS['yellow'],  label=legend['sta0002'])
ax.plot(atten[:,2],signal_dev[:,3], color=COLORS['green'],   label=legend['sta0003'])
ax.plot(atten[:,2],signal_dev[:,4], color=COLORS['cyan'],    label=legend['sta0004'])
ax.plot(atten[:,2],signal_dev[:,5], color=COLORS['blue'],    label=legend['sta0005'])
ax.plot(atten[:,2],signal_dev[:,6], color=COLORS['violet'],  label=legend['sta0006'])
ax.set_title(F'Atteunuation vs. Signal Deviation:\n'
             + F'SSID={data[1][14]}, '
             + F'Channel={channel}, '
             + F'Mode={data[1][11]}')
ax.set_xlabel('Attenuation (dB)')
ax.set_ylabel('RSSI (dBm)')
ax.set_yticks(range(-5, 30, 5))
ax.set_xticks(range(20, 100, 5))
plt.grid(color=COLORS['dark_gray'], linestyle='-', linewidth=1)
plt.legend()
plt.savefig(F'{PNG_OUTPUT_DIR}/{channel}_{antenna}_{bandwidth}_signal_deviation_atten.png')

check_data(signal, signal_exp)
sys.exit(0)
