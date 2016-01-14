#!python3
import os, sys, re, csv, sqlite3, string
from datetime import datetime, timedelta
from time import strptime, strftime
from itertools import chain
maxlinecount = 16000000
linecount = 0
filecount = 0

# Sample LIne
# 11.11.11.11 - - [14/Sep/2015:02:36:18 +0000] "GET /auth/password_reset/ HTTP/1.1" 503 14 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"

header = ["DATE","EMAIL","FILE_NAME","SRCIP","METHOD","URI","HTTPSTATUSCODE","BYTES","UNK","USERAGENTSTRING"]


def parsefile(fname,ofile):
	tmp_lcount = 0
	for line in open(fname,'r'):
		output_line = []
		# DATE
		if line.split("[")[1].split("]")[0].split("+")[1] != "0000":
			print("ERROR: Time format is not +0000")
			sys.exit(1)
		# RAWDATE: 14/Sep/2015:03:42:52
		rawdate = line.split("[")[1].split("]")[0].split("+")[0].strip()
		finaldate = datetime.strptime(rawdate,'%d/%b/%Y:%H:%M:%S')
		output_line.append(str(finaldate))

		#EMAIL
		EMAIL = line.split("[")[0].split(" ")[-2].strip()
		output_line.append(EMAIL)

		#FILENAME
		output_line.append(fname)


		#SRCIP
		srcip = line.split(" ")[0].strip()
		output_line.append(srcip)

		#METHOD
		METHOD = line.split("\"")[1].split(" ")[0].strip()
		output_line.append(METHOD)

		#URI
		URI = line.split("\"")[1].strip()
		output_line.append(URI)

		#HTTPSTATUSCODE
		HTTPSTATUSCODE = line.split("\"")[2].split(" ")[1].strip()
		output_line.append(HTTPSTATUSCODE)

		#BYTES
		BYTES = line.split("\"")[2].split(" ")[2].strip()
		output_line.append(BYTES)

		#UNK
		UNK = line.split("\"")[3].strip()
		output_line.append(UNK)

		#USERAGENTSTRING
		USERAGENTSTRING = line.split("\"")[5].strip()
		output_line.append(USERAGENTSTRING)

		ofile.write('\t'.join(output_line)+"\n")
		tmp_lcount += 1
		#print(tmp_lcount)
	return tmp_lcount

def getfilenames(fext):
	listoffiles = []
	for root, dirs, files in os.walk(os.curdir):
		for file in files:
			if file.endswith(fext):
				listoffiles.append(os.path.join(root, file))
	return listoffiles

def new_outfile(filecount):
	ofilename = "all_output_file_final_"+ str(filecount) +".log"
	print(ofilename)
	return open(ofilename,'w')



mofile = new_outfile(filecount)
mofile.write('\t'.join(header)+"\n")

lof = getfilenames("")

for fname in lof:
	linecount += parsefile(fname, mofile)
	if linecount > maxlinecount:
		mofile.close()
		filecount += 1
		mofile = new_outfile(filecount)
		mofile.write('\t'.join(header)+"\n")
		linecount = 0


mofile.close()