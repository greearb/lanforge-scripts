"""
-----------------------------------------------------------------------------
Name : WIFI Diag
Author : Sushant Bawiskar
Date : 20 September 2020
------------------------------------------------------------------------------
"""

""" 
    Example:    python PcaplibFiles.py --input "11ax.pcapng","sta1.pcap" 

"""

import datetime
import pyshark
import pandas as pd
from bokeh.plotting import figure, output_file, show, save
from bokeh.io.export import get_screenshot_as_png, export_png, export_svgs, export_svg
import matplotlib.pyplot as plt
from plotly.offline import iplot, init_notebook_mode
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt
import base64
from io import BytesIO
from htmlText import *
from Dataplot import Plot
import shutil
import argparse
import logging
import numpy as np



import os


def PacketHistogram(subtype_list, Managementls, Controlls, Data_framels, count):
    # Created a Dictonary of Management Frame : {Subtype} , Control Frame : {Subtype} , Data Frame : {Subtype}
    Type_Subtype = {"Management Frame": [Managementls], "Control Frame": [Controlls], "Data Frame": [Data_framels]}

    Type_list = []
    Sub_list = []
    pack_list = []
    per_list = []

    # To calculate Total number of Subtype of packets in Type
    # Ex. To calculate how many packets have a subtype which are in Management/Control/Data Frame Type
    for Type, Subtype in Type_Subtype.items():

        liskeys = []
        for key in subtype_list.values():
            if (key in liskeys):
                continue

            val = Subtype[0].count(key)
            liskeys.append(key)
            # liskeys.append(key)
            if (val != 0):
                # Type_list = [Type,key,val,(val*100)/count]
                Type_list.append(str(Type))
                Sub_list.append(key)
                pack_list.append(val)
                per_list.append((round((val * 100) / count, 2)))


    # Type_list.append("")
    Sub = Sub_list
    NewSubList = Sub_list
    # NewSubList.append("Sum: ")
    #
    # pack_list.append(sum(pack_list))

    NewPerList = per_list
    # NewPerList.append(sum(NewPerList))

    print(len(subtype_list),len(NewSubList),len(pack_list),print(NewPerList))
    df_Type = pd.DataFrame(({"Type": Type_list, "Subtype": NewSubList, "Packet to packet": pack_list, "Percentage": NewPerList}))


    # print("df_Type",df_Type)

    df_Type = df_Type.to_html()
    # NewPerList.pop()
    # NewSubList.pop()
    plot = Plot()
    path = plot.bar(datax=NewSubList,datay=NewPerList,title="Type/SubType plot",xaxis="Subtype",yaxis="Percentage",figname="Type")

    htmltable(" Packet Type histogram", df_Type, str(path), "0", "0")



def RateHistogram(DataRate, PhyType, SignalStrength, count):

    countUniqueData = []
    perUniqueData = []

    countUniquePhy = []
    perUniquePhy = []

    countUniqueSignal = []
    perUniqueSignal = []

    # This is for Data Table Histogram
    uniqueData = np.unique(DataRate)

    for i in uniqueData:
        countUniqueData.append(DataRate.count(i))

    uniqueData = [i for i in uniqueData]

    # uniqueData.append("Sum: ")
    # countUniqueData.append(sum(countUniqueData))

    dictRate = (dict(zip(uniqueData, countUniqueData, )))

    for c in countUniqueData:
        perUniqueData.append(round((c * 100) / count, 2))



    df_Rate = pd.DataFrame({"Rate MBPS": [i for i in dictRate.keys()], "Packet to packet": [j for j in dictRate.values()], "Percentage": [k for k in perUniqueData]})

    df_Rate = df_Rate.T
    df_Rate.columns = df_Rate.iloc[0]
    df_Rate = df_Rate.drop(df_Rate.iloc[0].index.name)
    df_Rate = df_Rate.to_html()




    # uniqueData.pop()
    # perUniqueData.pop()

    plot1 = Plot()
    path = plot1.bar(datax=uniqueData, datay=perUniqueData, title="Rate plot", xaxis="Rate MBPS", yaxis="Percentage",
                    figname="rate")


    htmltable(" Encoding rate histogram.", df_Rate, str(path), "0", "0")


    # This is for Phy Histogram
    uniquePhy = np.unique(PhyType)
    for j in uniquePhy:
        countUniquePhy.append(PhyType.count(j))

    uniquePhy = [i for i in uniquePhy]
    # uniquePhy.append("Sum: ")
    # countUniquePhy.append(sum(countUniquePhy))

    dictPhy = (dict(zip(uniquePhy, countUniquePhy)))

    for d in countUniquePhy:
        perUniquePhy.append(round((d * 100) / count, 2))

    df_Phy = pd.DataFrame({"Phy": [i for i in dictPhy.keys()], "Packet to Packet": [j for j in dictPhy.values()],"Percentage": [k for k in perUniquePhy]})

    # print("df_Phy",df_Phy)

    # df_Phy = df_Phy.to_html()

    df_Phy = df_Phy.T
    df_Phy.columns = df_Phy.iloc[0]
    df_Phy = df_Phy.drop(df_Phy.iloc[0].index.name)
    df_Phy = df_Phy.to_html()

    dictphys = [i for i in dictPhy.keys()]

    # dictphys.pop()
    # perUniquePhy.pop()

    plot2 = Plot()
    path = plot2.bar(datax=dictphys, datay=perUniquePhy, title="Phy plot", xaxis="Subtype", yaxis="Percentage",
                    figname="Phy")

    htmltable(" Phy Histogram.",df_Phy,str(path),"0","0")

    # This is for Signal Histogram
    uniqueSignal = np.unique(SignalStrength)

    for k in uniqueSignal:
        countUniqueSignal.append(SignalStrength.count(k))

    uniqueSignal = [i for i in uniqueSignal]
    # uniqueSignal.append("Sum: ")
    # countUniqueSignal.append(sum(countUniqueSignal))

    dictSig = (dict(zip(uniqueSignal, countUniqueSignal)))

    for e in countUniqueSignal:
        perUniqueSignal.append(round((e * 100) / count, 2))

    # perUniqueSignal.append(sum(perUniqueSignal))
    # pd.DataFrame.reset_index(drop=True,inplace=True)
    # df_Sig = pd.DataFrame({"Signal": [i for i in dictSig.keys()], "Packet to Packet": [j for j in dictSig.values()],
    #                        "Percentage": [k for k in perUniqueSignal]})

    # pd.DataFrame.reset_index(drop=True,inplace=True)
    print([k for k in dictSig.keys()])
    print([i for i in dictSig.values()])
    print("perUniqueSignal",perUniqueSignal)

    # pd.DataFrame
    df_Sig = pd.DataFrame({"Signal":[k for k in dictSig.keys()],"Packet":[i for i in dictSig.values()],"Percentage":[j for j in perUniqueSignal]})

    df_Sig = df_Sig.T
    df_Sig.columns = df_Sig.iloc[0]
    df_Sig = df_Sig.drop(df_Sig.iloc[0].index.name)
    # df_Sig.columns.name = None
    # df_Sig.index.name = "Signal"
    print("df_Sig",df_Sig)
    # print("df_Sig",df_Sig)

    # df_Sig = df_Sig.to_html()

    # df_Sig = df_Sig.transpose()
    df_Sig = df_Sig.to_html()

    # perUniqueSignal.pop()
    dictSigs = [i for i in dictSig.keys()]
    # dictSigs.pop()

    plot3 = Plot()
    path = plot2.bar(datax=dictSigs, datay=perUniqueSignal, title="Signal plot", xaxis="Signal", yaxis="Percentage",
                     figname="Signal")
    htmltable(" Signal Histogram.", df_Sig, str(path), "0", "0")

    # print(dictSigs,perUniqueSignal)




class shark:
    def __init__(self):
        # FilePath having pcap file
        # self.FilePath = "wifi_diag.pcap"
        # self.FilePath = "C:\Candela\Scripts\Lanforge scripts\lanforge-scripts-master\wifi_diag\wifi_diag.pcapng"
        # self.FilePath = "wifi_diag.pcap"
        # self.FilePath = "C:\candela\pcap\wifi.pcapng"
        self.FilePath = "C:\candela\pcap\\ac1_28Sept.pcapng"
        # self.FilePath = "C:\Candela\My_Scripts\WIFI_diag11ax\wifi.pcapng"
        # self.FilePath = "wifi_diag.pcap"

        self.cap = pyshark.FileCapture(self.FilePath)
        print("Strt time stamp :",datetime.datetime.now())

    def Extract(self):

        type_list = {"0": "Management frame", "1": "Control Frame", "2": "Data frame"}
        subtype_list = {"80": "Beacon frame", "d0": "Action", "b4": "Request-to-send", "d4": "Acknowledgement", \
                        "88": "QoS Data", "84": "Block Ack Req", "94": "Block Ack Req", "08": "Data", \
                        "40": "Probe Request", "50": "Probe Response", "b0": "Authentication",
                        "a2": "Disassociate", "a8": "QoS Data + CF-Poll", "c8":"QoS Null function", \
                        "10": "Association Response", "00": "Association Request", "c4": "Clear-to-send", \
                        "98": "QoS Data + CF-Acknowledgment", "24": "Trigger", "28": "Data + CF-Poll" ,\
                        "d8": "Unknown", "54": "VHT/HE NDP Announcement", "e8": "QoS CF-Poll", \
                        "b8" : "QoS Data + CF-Ack + CF-Poll", "18": "Data + CF-Ack", "48" : "Null function", \
                        "69" : "CF-Poll"
                        }


        Managementls = []
        Controlls = []
        Data_framels = []
        PhyType = []
        DataRate = []
        SignalStrength = []


        MCSIndex = []
        uniqueMCSIndex = []
        countUniqueMCSIndex = []
        MCSIndex

        Bandwidth = []
        countUniqueBandwidth = []

        PHY = []
        countUniquePHY = []

        Spatial_Stream = []
        countUniqueSpatial_stream = []

        count = 0
        vWLAN_RADIO = 0
        vsignalstrength = 0
        vPhy = 0
        vdatarate = 0
        vWLAN = 0

        """ Comment   
        """






        # print(wlan_radio_Fields_keys,wlan_radio_Fields_values)

        # if "wlan_radio.phy" and "wlan_radio.11ac.bandwidth" and "wlan_radio.11ac.mcs" and "wlan_radio.11ac.nss" in wlan_radio_Fields_keys:
        #     # print(dir(packet.wlan_radio._all_fields["wlan_radio.phy"]))
        #     # print(packet.wlan_radio._all_fields["wlan_radio.phy"].showname_value) #for PHY
        #     # print(packet.wlan_radio._all_fields["wlan_radio.11ac.bandwidth"].showname_value) #for BW
        #     # print(packet.wlan_radio._all_fields["wlan_radio.11ac.mcs"].showname_value) #for MCS
        #     # print(packet.wlan_radio._all_fields["wlan_radio.11ac.nss"].showname_value) #for Spatial streams
        #     PHY.append(packet.wlan_radio._all_fields["wlan_radio.phy"].showname_value)
        #     Bandwidth.append(packet.wlan_radio._all_fields["wlan_radio.11ac.bandwidth"].showname_value)
        #     MCSIndex.append(packet.wlan_radio._all_fields["wlan_radio.11ac.mcs"].showname_value)
        #     Spatial_Stream.append(packet.wlan_radio._all_fields["wlan_radio.11ac.nss"].showname_value)

        # _data = (packet.wlan_radio._all_fields)
        # print(type(_data))
        # phy, _11ac_short_gi, _11ac_bandwidth, _11ac_user, _11ac_mcs, _11ac_nss, _11ac_fec, _data_rate = (packet.wlan_radio._all_fields)
        # print(phy.get_field_value)


        """
        comment
        """


        for packet in self.cap:
            count += 1

            # print(count)


            try:
                WLAN_RADIO = packet.wlan_radio
                vWLAN_RADIO = 1
                try:
                    signalstrength = WLAN_RADIO.signal_dbm
                    vsignalstrength = 1
                except:
                    pass

                try:
                    phy = WLAN_RADIO.phy.showname_value
                    vPhy = 1
                except:
                    pass

                try:
                    datarate = WLAN_RADIO.data_rate
                    vdatarate = 1
                except:
                    pass

            except:
                pass
                # print("WLAN RADIO NOT FOUND")

            try:
                RADIOTAP = packet.radiotap
            except:
                # print("RADIOTAP NOT FOUND")
                pass

            try:
                WLAN = packet.wlan
                vWLAN = 1
            except:
                pass
                # print("WLAN NOT FOUND")


            PacketCount = (packet.number)
            # print("PacketCount: ", PacketCount)


            if vWLAN == 1:
                # print("WLAN found")
                # Type/Subtype raw value
                type_raw = (str(packet.wlan.fc_type.raw_value))
                subtype_raw = ((packet.wlan.fc_type_subtype.raw_value))

                # Name of values Types/Subtype
                type = (str(packet.wlan.fc_type.showname_value))
                subtype = (str(packet.wlan.fc_type_subtype.showname_value))

                # Sorting Subtypes by Types as a refrence
                if (type_raw == "0"):
                    try:
                        Managementls.append(subtype_list[subtype_raw])
                    except:
                        pass

                elif (type_raw == "1"):
                    try:
                        Controlls.append(subtype_list[subtype_raw])
                    except:
                        print("Control Frame", subtype, subtype_raw)

                elif (type_raw == "2"):
                    try:
                        Data_framels.append(subtype_list[subtype_raw])

                    except:
                        print("Data frame", subtype, subtype_raw)

                else:
                    print("\nMissing Type in table : ", type_raw, subtype, subtype_raw, "\n")
            else:
                print("Packet Number :",count,":"," WLAN NOT FOUND")

            vWLAN = 0
            if vWLAN_RADIO == 1:
                # print("vWLAN Found")

                wlan_radio_Fields_keys = []
                wlan_radio_Fields_values = []

                for keys, values in packet.wlan_radio._all_fields.items():
                    # print(keys, ":", values)
                    wlan_radio_Fields_keys.append(keys)
                    wlan_radio_Fields_values.append(values)


                if vdatarate == 1:
                    DataRate.append(datarate)

                if vPhy == 1:
                    PhyType.append(phy)

                if vsignalstrength == 1:
                    SignalStrength.append(signalstrength)

                vWLAN_RADIO = 0
            else:
                print("Packet Number :",count," WLAN RADIO NOT FOUND")

            try:
                vMCS = 0
                {"MCSIndex":['0 (BPSK 1/2)','1 (QPSK 1/2)','2 (QPSK 3/4)','4 (16-QAM 3/4)','5 (64-QAM 2/3)']}
                {"Spatial_stream":["2"]}
                {}
                if "wlan_radio.11ac.bandwidth" and "wlan_radio.11ac.bandwidth" and "wlan_radio.phy" and \
                        "wlan_radio.11ac.mcs" and "wlan_radio.11ac.nss" in wlan_radio_Fields_keys:
                    # print(dir(packet.wlan_radio._all_fields["wlan_radio.phy"]))
                    # print(packet.wlan_radio._all_fields["wlan_radio.phy"].showname_value) #for PHY
                    # print(packet.wlan_radio._all_fields["wlan_radio.11ac.bandwidth"].showname_value) #for BW
                    # print(packet.wlan_radio._all_fields["wlan_radio.11ac.mcs"].showname_value) #for MCS
                    # print(packet.wlan_radio._all_fields["wlan_radio.11ac.nss"].showname_value) #for Spatial streams
                    PHY.append(packet.wlan_radio._all_fields["wlan_radio.phy"].showname_value)
                    Bandwidth.append(packet.wlan_radio._all_fields["wlan_radio.11ac.bandwidth"].showname_value)
                    MCSIndex.append(packet.wlan_radio._all_fields["wlan_radio.11ac.mcs"].showname_value)
                    Spatial_Stream.append(packet.wlan_radio._all_fields["wlan_radio.11ac.nss"].showname_value)
                    vMCS = 1
            except:
                pass

        # print("MCSIndex",len(MCSIndex),MCSIndex)
        # print("Bandwidth",len(Bandwidth),Bandwidth)
        # print("PHY",len(PHY),PHY)
        # print("Spatial_Stream",len(Spatial_Stream),Spatial_Stream)

        uniqueMCSIndex = np.unique(MCSIndex)
        uniqueBandwidth = ((np.unique(Bandwidth)))
        uniquePHY = ((np.unique(PHY)))
        uniqueSpatial_stream = ((np.unique(Spatial_Stream)))
        exit()

        print("After appending time stamp :", datetime.datetime.now())
        # print(count)
        RateHistogram(DataRate, PhyType, SignalStrength, count)
        print("After RateHist time stamp :", datetime.datetime.now())
        PacketHistogram(subtype_list, Managementls, Controlls, Data_framels, count)
        print("After PacketHist time stamp :", datetime.datetime.now())



if __name__ == "__main__":


    # parser = argparse.ArgumentParser(description="To create a single pcap file combining multiple pcap files")
    # # parser.add_argument("-o", "--output", type=str, help="Enter the output pcap file name")
    # parser.add_argument("-i", "--input", type=str,
    #                     help="Enter the Name of the pcap files which needs to be combined")
    #
    # args = None
    #
    # try:
    #     args = parser.parse_args()
    #     output = "wifi_diag.pcap"
    #
    #     if (args.input is not None):
    #         input = args.input  # 'C:\candela\pcap\\11ax.pcapng','C:\candela\pcap\sta1.pcap'
    #         input = input.split(",")
    #         print(input)
    #
    #     # if (args.input is None):
    #     #     input = "11ax.pcapng", "sta1.pcap"
    #
    # except Exception as e:
    #     logging.exception(e)
    #     exit(2)
    #
    # with open(output, 'wb') as wfd:
    #     print("input", input)
    #     for f in (input):
    #         with open(f, 'rb') as fd:
    #             shutil.copyfileobj(fd, wfd)

    htmlstart()
    downloadBtn()
    htmlobj("This is HTML objective")

    htmlpointview()
    htmlTableSummary("This is html table summary")
    myUL()


    Extract = shark()
    Extract.Extract()
    # htmltable()

    closemyUl()
    htmlclose()


