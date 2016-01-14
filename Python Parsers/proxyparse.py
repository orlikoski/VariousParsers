#!python3
import os, sys, re, csv, sqlite3, string
from datetime import datetime, timedelta
from time import strptime, strftime
from itertools import chain

maxlinecount = 16000000
linecount = 0
filecount = 0

# Sample LIne
# 3616 0 27256 - 10.12.244.1 - - [28/Feb/2015:00:05:14 -0800] "GET /" 302 783 "BALANCEID=balancer.lb1; path=/; domain=.company.com"

header = ["DATE_TIME","SRC_FILE","SRC_IP","URI","HTTP_STATUS_CODE","BYTES","COOKIES", "RAW_LINE"]


def parsefile(fname,ofile):
	# REGEX Patterns
	http_bytes_pattern = re.compile(' [1-5][0-9][0-9] [0-9]{1,10000000} | [1-5][0-9][0-9] - ')
	datetime_pattern = re.compile('\[([0-9]{2}\/[A-Z][a-z]{2}\/[0-9]{4}\:[0-9]{2}\:[0-9]{2}:[0-9]{2}) (\-[0-9]{4})\]')

	tmp_lcount = 0
	for line in open(fname,'r'):
		output_line = []
		# Prefill the value of each field before starting loop
		finaldate = "-"
		srcip = "-"
		URI = "-"
		HTTPSTATUSCODE = "-"
		BYTES = "-"
		COOKIES = "-"


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

		#SRCIP
		try:
			srcip = line.split(" ")[4].strip()
			output_line.append(srcip)
		except:
			print("ERROR: Parsing SRCIP error on line")
			#print(line)
			error_file.write(line)
			continue

		#URI 
		Str1 = re.split(datetime_pattern,line)[3]
		URI = re.split(http_bytes_pattern,Str1)[0].strip().strip("\"")
		output_line.append(URI)
		#print(URI)

		#HTTPSTATUSCODE and BYTES
		http_bytes = http_bytes_pattern.search(line.split("] ",1)[1])
		if http_bytes:
			BYTES = http_bytes.group().strip().split(" ")[1]
			HTTPSTATUSCODE = http_bytes.group().strip().split(" ")[0]
		output_line.append(HTTPSTATUSCODE)
		output_line.append(BYTES)

		#COOKIES
		COOKIES = re.split(http_bytes_pattern,Str1)[1].strip().strip("\"")
		output_line.append(COOKIES)
		#print(COOKIES)

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