#!python3
import os, sys, re, csv, sqlite3, string
from datetime import datetime, timedelta
from time import strptime, strftime
from itertools import chain

for line in open(sys.argv[1],'r'):
	#keyword = line.split("\\")[-1].strip().rstrip('\"')
	keyword = line.split("C$")[-1].strip().rstrip('\"')
	print(keyword)