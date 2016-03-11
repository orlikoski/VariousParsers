#!python3
import os, sys, re, csv, sqlite3, string
from datetime import datetime, timedelta
from time import strptime, strftime
from itertools import chain

maxlinecount = 16000000
linecount = 0
filecount = 0

# Sample LIne
# 192.168.117.1 - - [20/Jun/2013:01:38:40 -0400] "GET /Dkrh8Ycb.htm HTTP/1.0" 404 210 "-" "Mozilla/5.00"

header = ["DATE_TIME","SRC_FILE","SRC_IP","REQ_TYPE","URI","HTTP_STATUS_CODE","BYTES","REFFER","USER_AGENT_STRING","RAW_LINE"]


def parsefile(fname,ofile):
	# REGEX Patterns
	http_bytes_useragentstring_pattern = re.compile("\"([A-Z]{1,10}|[a-z]{1,10}) (.{1,10000})\" (\d{1,1000}) (\d{1,1000}|-) \"(-|.{1,500})\" \"(.{1,500})\"")
	ip_address_pattern = re.compile('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
	datetime_pattern = re.compile('\[([0-9]{2}\/[A-Z][a-z]{2}\/[0-9]{4}\:[0-9]{2}\:[0-9]{2}:[0-9]{2}) ([\+,\-][0-9]{4})\]')

	tmp_lcount = 0
	for line in open(fname,'r'):
		if line[0] <> "#":
			output_line = []
			# Prefill the value of each field before starting loop
			finaldate = "-"
			srcip = "-"
			URL = "-"
			HTTPSTATUSCODE = "-"
			BYTES1 = "-"
			BYTES2 = "-"
			REFFER = "-"
			port = "-"
			useragentstring = "-"


			# # Check for NULL line
			# if line == " ":
			# 	continue

			# DATE
			rawdate = datetime_pattern.search(line)
			if rawdate:
				datetime2 = rawdate.group(1)
				offset = rawdate.group(2)
				finaldate = normalize_datetime(datetime2,offset)
			output_line.append(str(finaldate))

			#FILENAME
			try:
				output_line.append(fname)
			except:
				print("ERROR: Parsing FILENAME error on line")
				#print(line)
				error_file.write(line)
				continue

			#SRCIP and SRC_PORT
			srcip_atmp = ip_address_pattern.search(line)
			#srcinfo = status_type_url_port_pattern.search(line)


			if srcip_atmp:
				srcip = srcip_atmp.group().split(":")[0]
			output_line.append(srcip)

			#HTTPSTATUSCODE and BYTES
			bytesinfo = http_bytes_useragentstring_pattern.search(line)
			if bytesinfo:
				REQ_TYPE = bytesinfo.group(1)
				URL = bytesinfo.group(2)
				BYTES1 = bytesinfo.group(4)
				HTTPSTATUSCODE = bytesinfo.group(3)
				REFFER = bytesinfo.group(5)
				useragentstring = bytesinfo.group(6)

			output_line.append(REQ_TYPE)
			output_line.append(URL)
			output_line.append(HTTPSTATUSCODE)
			output_line.append(BYTES1)
			output_line.append(REFFER)
			output_line.append(useragentstring)

			# RAW_LINE
			output_line.append(line.strip())

			ofile.write('\t'.join(output_line)+"\n")
			tmp_lcount += 1
			#print(tmp_lcount)
	return tmp_lcount

def normalize_datetime(rawdate,offset):
	# RAW Date: 28/Feb/2015:00:05:03
	# RAW Offset: -0800
	tmpdate = datetime.strptime(rawdate,'%d/%b/%Y:%H:%M:%S')
	if offset[0:1] == "-":
		finaldate = tmpdate + timedelta(hours=int(offset[1:3]),minutes=int(offset[3:5]))
	if offset[0:1] == "+":
		finaldate = tmpdate - timedelta(hours=int(offset[1:3]),minutes=int(offset[3:5]))
	return finaldate

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

# Start the error file
error_file = open("unparsed_lines.log",'w')

# Start the first file and write the header
mofile = new_outfile(filecount)
mofile.write('\t'.join(header)+"\n")

# Get the list of filenames from the directory ending with the string provided to the function
lof = getfilenames(sys.argv[1])

# Cycle through list of filenames and parse the data
for fname in lof:
	linecount += parsefile(fname, mofile)
	if linecount > maxlinecount:
		mofile.close()
		filecount += 1
		mofile = new_outfile(filecount)
		mofile.write('\t'.join(header)+"\n")
		print('\t'.join(header))
		linecount = 0

# Close the final file
mofile.close()

# Close the error file
error_file.close()