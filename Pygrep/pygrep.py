#! python3
import os, sys, re, string, argparse

pygrep_version = "beta"

# myencoder="iso2022_jp_2"
myencoder="utf-8"

def getfilenames(fext):
	listoffiles = []
	for root, dirs, files in os.walk(os.curdir):
		for file in files:
			if file.endswith(fext):
				listoffiles.append(os.path.join(root, file))
	return listoffiles

# def path_leaf(path):
#     head, tail = ntpath.split(path)
#     return tail or ntpath.basename(head)

# Parsing begins
parser = argparse.ArgumentParser(description='Python Grep.  This implements a simple regex search on file(s) provided at the command line.')
parser.add_argument('reg_search',nargs=1,help='Regex search string')
parser.add_argument('search_loc',nargs=1,help='file(s) to be searched. files that end with this are included from the current directory and sub-directories')
parser.add_argument('-i', action='store_true' , help='case insensitive')
parser.add_argument('-o', action='store_true' , help='Print just match')
parser.add_argument('-v', action='store_true' , help='inverts match')
parser.add_argument('--version', action='version', version=pygrep_version)

args=parser.parse_args()

if args:
	grep_pattern = re.compile(args.reg_search[0])
	grep_ignorecase_pattern = re.compile(args.reg_search[0],re.IGNORECASE)
	lof = getfilenames(args.search_loc[0])
	for fname in lof:
		for line in open(fname,'r',encoding=myencoder):
			if args.i:
				results = grep_ignorecase_pattern.search(line)
			else:
				results = grep_pattern.search(line)
			if results:
				if args.o:
					print(results.group())
				else:
					print(line)
			else:
				if args.v:
					print(line.rstrip('\n'))
