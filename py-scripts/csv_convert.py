#!/usr/bin/env python3

import sys
import os

import argparse
import pandas as pd

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

class CSVParcer():
    def __init__(self,csv_infile=None,csv_outfile=None):

        # Grab the appropriate columns from Candela csv and place in the Comcast csv
        include_summary = ['Atten','Rotation','Rx-Bps']
        self.csv_infile = csv_infile
        self.csv_outfile = csv_outfile

        try: 
            #dataframe = pd.read_csv(self.csv_infile,header = 0, usecols = lambda column : any(substr in column for substr in include_summary ))
            dataframe = pd.read_csv(self.csv_infile,header = 0, usecols = lambda column : column in include_summary )
        except:
            print("Input file not accessible, please check for presence of input file")
            exit(1)

        dataframe.index.name = 'Step Index' 
        dataframe = dataframe.replace('Mbps','',regex=True) 
        dataframe = dataframe.rename(columns={'Atten':'Attenuation [dB]','Rotation':'Position [Deg]','Rx-Bps':'Traffic Pair 1 Throughtput [Mbps]'})

        #print('{}'.format(self.csv_infile))
        #print("dataframe {}".format(dataframe))
        if self.csv_outfile == None:
            csv_summary = self.csv_infile.replace('candela','comcast')
        else:
            csv_summary = self.csv_outfile
            csv_summary = os.path.splitext(csv_summary)[0] + '.csv'


        dataframe.to_csv(csv_summary, index = True, header=True)
        
        xlsx_summary = os.path.splitext(csv_summary)[0] + '.xlsx'

        dataframe.to_excel(xlsx_summary, index = True, header=True)


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
    parser.add_argument('-o','--outfile', help="output file of csv, xlsx data", default=None)


    args = parser.parse_args()
    csv_outfile_name = None

    if args.infile:
        csv_infile_name = args.infile
    if args.outfile:
        csv_outfile_name = args.outfile

    CSVParcer(csv_infile_name,csv_outfile_name)

if __name__ == "__main__":
    main()
