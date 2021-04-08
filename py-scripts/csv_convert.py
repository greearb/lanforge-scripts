#!/usr/bin/env python3

# This program is used to read in a LANforge Dataplane CSV file and output
# a csv file that works with a customer's RvRvO visualization tool.
#
# Example use case:
#
# Read in ~/text-csv-0-candela.csv, output is stored at outfile.csv
# ./py-scripts/csv_convert.py -i ~/text-csv-0-candela.csv

import sys
import os

import argparse

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

class CSVParcer():
    def __init__(self,csv_infile=None,csv_outfile=None,ddb=False):

        idx = 0
        i_atten = -1
        i_rotation = -1
        i_rxbps = -1
        fpo = open(csv_outfile, "w")
        with open(csv_infile) as fp:
            line = fp.readline()
            if not line:
                exit(1)
            # Read in initial line, this is the CSV headers.  Parse it to find the column indices for
            # the columns we care about.
            x = line.split(",")
            cni = 0
            for cn in x:
                if (cn == "Atten"):
                    i_atten = cni
                if (cn == "Rotation"):
                    i_rotation = cni
                if (cn == "Rx-Bps"):
                    i_rxbps = cni
                cni += 1

            # Write out out header for the new file.
            fpo.write("Step Index,Attenuation [dB],Position [Deg],Traffic Pair 1 Throughput [Mbps]\n")

            # Read rest of the input lines, processing one at a time.  Covert the columns as
            # needed, and write out new data to the output file.
            line = fp.readline()

            step_i = 0
            while line:
                x = line.split(",")
                mbps_data = x[i_rxbps]
                mbps_array = mbps_data.split(" ")
                mbps_val = float(mbps_array[0])
                if (mbps_array[1] == "Gbps"):
                    mbps_val *= 1000
                if (mbps_array[1] == "Kbps"):
                    mbps_val /= 1000
                if (mbps_array[1] == "bps"):
                    mbps_val /= 1000000

                attenv = int(x[i_atten])
                if ddb:
                    attenv /= 10
                    
                fpo.write("%s,%s,%s,%s\n" % (step_i, attenv, x[i_rotation], mbps_val))
                line = fp.readline()
                step_i += 1

def main():

    #debug_on = False
    parser = argparse.ArgumentParser(
        prog='csv_convert.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
 Useful Information:
            ''',
        
        description='''
csv_convert.py:  
    converts the candela csv into the comcast csv and xlsx, 
    renames input file from candela to comcast if not outfile given
        ''')

    # for testing parser.add_argument('-i','--infile', help="input file of csv data", default='text-csv-0-candela.csv')
    parser.add_argument('-i','--infile', help="input file of csv data", required=True)
    parser.add_argument('-d','--ddb', help="Specify attenuation units are in ddb in source file",
                        action='store_true', default=False)
    parser.add_argument('-o','--outfile', help="output file in .csv format", default='outfile.csv')


    args = parser.parse_args()
    csv_outfile_name = None

    if args.infile:
        csv_infile_name = args.infile
    if args.outfile:
        csv_outfile_name = args.outfile

    CSVParcer(csv_infile_name, csv_outfile_name, args.ddb)

if __name__ == "__main__":
    main()
