#!/usr/bin/env python3
from html.parser import HTMLParser
import urllib.request
from html.entities import name2codepoint
import re
import datetime
import argparse
import os
import time
import glob
import sys
import subprocess


#===========ARGUMENT PARSING==============
parser = argparse.ArgumentParser()
parser.add_argument("--versionNumber", type=str, help="Specify version number to search for")

args = parser.parse_args()
if args.versionNumber != None:
	ver = args.versionNumber
else:
	parser.print_help()
	parser.exit()

#=============HTML PARSING================
url = "http://jed-centos7/pld/"
with urllib.request.urlopen(url) as response:
	html = response.read()

webpage = html.decode('utf-8')
#print(webpage)

searchPattern = '(LANforgeGUI_(\d+\.\d+\.\d+)_Linux64.tar.bz2)<\/a><\/td><td align="right">(\d+\-\d+\-\d+\ \d+\:\d+)'
searchResults = re.findall(searchPattern, webpage)

webFiles = []

for file in searchResults:
	if ver == file[1]:
		webFiles.append({'filename':file[0], 'timestamp': datetime.datetime.strptime(file[2], "%Y-%m-%d %H:%M")})
if len(webFiles) == 0:
	print(f"Unable to find webfile with version number {ver}")
	sys.exit(1)


#=========CHECK DIR FOR FILES=============
filePath = f"/home/lanforge/Downloads/"
dir = glob.glob(filePath + f"LANforgeGUI_{ver}*")
dirFiles = []

for file in dir:
	if ver in file:
		fileTime = datetime.datetime.strptime(time.ctime(os.stat(file).st_ctime), "%a %B %d %H:%M:%S %Y") # Fri May  8 08:31:43 2020
		dirFiles.append({'filename':file[25:], 'timestamp':fileTime})

if len(dirFiles) == 0:
	print(f"Unable to find file in {filePath} with version {ver}")
	#sys.exit(1)

#============FIND NEWEST FILES============
def findNewestVersion(filesArray):
	newest = filesArray[0]
	if len(filesArray) > 0:
		for file in filesArray:
			if file['timestamp'] > newest['timestamp']:
				newest = file

	return newest

newestWebFile = findNewestVersion(webFiles)
if len(dirFiles) != 0:
	newestDirFile = findNewestVersion(dirFiles)
else:
	newestDirFile = {'filename':'placeholder', 'timestamp': datetime.datetime.strptime("0", "%H")}


#=======COMPARE WEB AND DIR FILES=========
if newestWebFile['timestamp'] > newestDirFile['timestamp']:
	try:
		if newestDirFile['filename'] != 'placeholder':
			subprocess.call(["rm", f"{filePath}{newestDirFile['filename']}"])
			print("No file found")
			print(f"Downloading newest {newestWebFile['filename']} from {url}")
		else:
			print("Found newer version of GUI")
			print(f"Downloading {newestWebFile['filename']} from {url}")
#=====ATTEMPT DOWNLOAD AND INSTALL=========
		subprocess.call(["curl", "-o", f"{filePath}{newestWebFile['filename']}", f"{url}{newestWebFile['filename']}"])
		time.sleep(5)
	except Exception as e:
		print(f"{e} Download failed. Please try again.")
		sys.exit(1)
	try:
		print("Attempting to extract files")
		subprocess.call(["tar", "-xf", f"{filePath}{newestWebFile['filename']}", "-C", "/home/lanforge/"])
	except Exception as e:
		print(f"{e}\nExtraction Failed. Please try again")
		sys.exit(1)

	#time.sleep(90)
	try:
		if "/home/lanforge/.config/autostart/LANforge-auto.desktop" not in glob.glob("/home/lanforge/.config/autostart/*"):
			print("Copying LANforge-auto.desktop to /home/lanforge/.config/autostart/")
			subprocess.call(["cp", f"/home/lanforge/{newestWebFile['filename'][:len(newestWebFile)-18]}/LANforge-auto.desktop", "/home/lanforge/.config/autostart/"])
	except Exception as e:
		print(e)


	try:
		print(f"Attempting to install {newestWebFile['filename']} at /home/lanforge")
		os.system(f"cd /home/lanforge/{newestWebFile['filename'][:len(newestWebFile)-18]}; sudo bash lfgui_install.bash")
	except Exception as e:
		print(f"{e}\nInstallation failed. Please Try again.")
		sys.exit(1)
#=========ATTEMPT TO RESTART GUI==========
	try:
		print("Killing current GUI process")
		os.system("pgrep java | xargs kill")
	except Exception as e:
		print(e)


else:
	print("Current GUI version up to date")
	sys.exit(0)

