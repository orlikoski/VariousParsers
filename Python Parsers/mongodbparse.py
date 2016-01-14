#!python3
import os, sys, re, csv, sqlite3, string
from datetime import datetime, timedelta
from time import strptime, strftime
from itertools import chain

maxlinecount = 16000000
linecount = 0
filecount = 0
file_base_name = sys.argv[1]
# Sample LIne
# 2015-12-10T23:06:47.603+0000 [initandlisten] connection accepted from 11.11.1.11:47923 #2 (1 connection now open)

header = ["DATE_TIME","SRC_FILE","SRC_IP","SRC_PORT","CONN","ACTION","DB_NAME","TABLE_NAME","QUERY","RAW_LINE"]
dtime_format = '%Y-%m-%dT%H:%M:%S.%f'

def parsefile(fname,ofile):
	# REGEX Patterns
	ip_address_pattern = re.compile('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\:([0-9]{1,5})')
	datetime_pattern = re.compile('([0-9]{4}\-[0-9]{2}\-[0-9]{2}\T[0-9]{2}\:[0-9]{2}:[0-9]{2}\.[0-9]{3})([\-\+][0-9]{4})')
	conn_action_pattern = re.compile('\[(.{1,13})\] (\w{1,15})')
	initandlisten_pattern = re.compile(' \#.{1,10} \(')
	dbname_tablename_pattern = re.compile('(spedse|calstrs)\.(\w{1,20}) ')
	query_pattern = re.compile(': (\{.{1,10000}\}) ')
	#action_pattern = re.compile('\] \w{1,15}')

	#details_pattern = re.compile('\].{1,}')

	tmp_lcount = 0
	for line in open(fname,'r',encoding='utf-8'):
		output_line = []
		# Prefill the value of each field before starting loop
		finaldate = "-"
		srcip = "-"
		port = "-"
		CONN = "-"
		details = '-'
		action = '-'
		dbname = '-'
		tablename = '-'
		queryname = '-'

		# # Check for NULL line
		# if line == " ":
		# 	continue

		# DATE
		rawdate = datetime_pattern.search(line)
		if rawdate:
			datetime2 = rawdate.group(1)
			offset = rawdate.group(2)
			finaldate = normalize_datetime(datetime2,offset)
		else:
			error_file.write(line)
			continue
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
		if srcip_atmp:
			srcip = srcip_atmp.group().split(":")[0]
			port = srcip_atmp.group(5)
		output_line.append(srcip)
		output_line.append(port)

		# CONN and Action
		conn_action_search = conn_action_pattern.search(line)
		if conn_action_search:
			CONN = conn_action_search.group(1)
			action = conn_action_search.group(2)

			if CONN == 'initandlisten':
				tsearch2 = initandlisten_pattern.search(line)
				if tsearch2:
					CONN = "conn"+tsearch2.group()[2:-2]
		output_line.append(CONN)
		output_line.append(action)

		# DB_NAME and TABLE_NAME
		dbname_tablename_name = dbname_tablename_pattern.search(line)
		if dbname_tablename_name:
			dbname = dbname_tablename_name.group(1)
			tablename = dbname_tablename_name.group(2)
		output_line.append(dbname)
		output_line.append(tablename)

		# QUERY_NAME
		query_search = query_pattern.search(line)
		if query_search:
			queryname = query_search.group(1)
		output_line.append(queryname)

		# RAW_LINE
		output_line.append(line.strip())

		ofile.write('\t'.join(output_line)+"\n")
		tmp_lcount += 1
		#print(tmp_lcount)
	return tmp_lcount

def normalize_datetime(rawdate,offset):
	# RAW Date: 28/Feb/2015:00:05:03
	# RAW Offset: -0800
	tmpdate = datetime.strptime(rawdate,dtime_format)
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
	ofilename = file_base_name[0:-4]+"_"+ str(filecount) +".log"
	print(ofilename)
	return open(ofilename,'w',encoding='utf-8')

# Start the error file
error_file = open("unparsed_lines.log",'w')

# Start the first file and write the header
mofile = new_outfile(filecount)
mofile.write('\t'.join(header)+"\n")

# Get the list of filenames from the directory ending with the string provided to the function
#lof = getfilenames(sys.argv[1])

tmp = parsefile(sys.argv[1],mofile)

# Cycle through list of filenames and parse the data
# for fname in lof:
# 	linecount += parsefile(fname, mofile)
# 	if linecount > maxlinecount:
# 		mofile.close()
# 		filecount += 1
# 		mofile = new_outfile(filecount)
# 		mofile.write('\t'.join(header)+"\n")
# 		print('\t'.join(header))
# 		linecount = 0

# Close the final file
mofile.close()

# Close the error file
error_file.close()