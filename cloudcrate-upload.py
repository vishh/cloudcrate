#!/usr/bin/python

# https://docs.python.org/2/library/os.html#os.listdir
# Getting Started with AWS - https://aws.amazon.com/articles/3998
# Introduction to boto - http://boto.cloudhackers.com/en/latest/
# How to Install boto  - http://stackoverflow.com/questions/2481287/how-do-i-install-boto
# https://ariejan.net/2010/12/24/public-readable-amazon-s3-bucket-policy/
# http://aws.amazon.com/code/Amazon-S3/1713

print """
   ____ _                 _      ____           _       
  / ___| | ___  _   _  __| |    / ___|_ __ __ _| |_ ___ 
 | |   | |/ _ \| | | |/ _` |   | |   | '__/ _` | __/ _ 
 | |___| | (_) | |_| | (_| |   | |___| | | (_| | ||  __/
  \____|_|\___/ \__,_|\__,_|    \____|_|  \__,_|\__\___|

  Usage : python cloudcrate-upload.py
  ===================================
  Available tasks:

	setup      ................ Run 'cloudcrate-upload setup' first to setup AWS keys. 
                                      Example: python cloudcrate-upload.py setup 
	sync       ................ Run Sync from the desired folder to sync to the cloud 
                                      Example: python cloudcrate-upload.py sync 
	schedule   ................ Run schedule to cron sync and download every 90 mins
	
  """

import sys
import os
from datetime import datetime
from collections import defaultdict



try:
	task = str(sys.argv[1])

	#args = str(sys.argv[2])
except IndexError:
	print "Enter one of the above command line arguments "
	sys.exit(1)

if task == 'setup' :
	try:
		import boto
		print "===================================================================="
		print "All required libraries have already been installed , proceed to sync"
		print "===================================================================="

	except ImportError,e:
		print "============================================================="
		raw_input("Missing Libraries - Press Hit Enter to Install them")

		print "============================================================="
		print "Installing boto - python interface to Amazon S3"
		print "============================================================="
		os.system("tar -zxvf boto.0.tar.gz")
		os.chdir("boto-2.34.0")
		os.system("sudo python setup.py install ")
		print "============================================================="
		print "All required libraries have been installed, proceed to sync "
		print "Example sync command : python cloudcrate-upload.py sync"
		print "For list of all commands : python cloudcrate-upload.py  "
		print "============================================================="



if task == 'sync' :


	from boto.s3.connection import S3Connection
	from boto.s3.key import Key
	import json
	import time
	from time import mktime
	from datetime import datetime

	conn = S3Connection('AKIAJ332D5S6IQ7WITSQ', 'G2WNp8xGxQPSxEcurBOTI32okS/izRmz2KPAJO24')
	print "Established connection to AWS S3"

	bucket = conn.create_bucket('cloudcrate.hari')
	print "======================================"

	print "====== Syncing Current Directory ====="
	path = os.path.dirname(os.path.realpath('cloudcrate-upload.py')) + '/'
	
	list_of_files = {}

	for (path,dirs,list_of_files) in os.walk(path):
		#print list_of_files
		break

	print "======================================"
	print "===== LIST OF FILES IN DIRECTORY======"
	print "======================================"

	print type(list_of_files)

	try:
		print "in try block - this would handle a resyn operation"
		print os.path.exists("last_modified.txt")
		last_modified_dict = json.load(open("last_modified.txt"))

		for files in list_of_files:
			if not files.startswith('.'):
				#print 'Working on file ' ,files

				if (files not in last_modified_dict):
					last_modified_dict[files] = os.path.getmtime(files)
					#print "Missing file Added to dictionary is ", files
					print "uploading ..from try block if" , files
					k = Key(bucket)
					k.key = files
					k.set_contents_from_filename(path+files)
					json.dump(last_modified_dict, open("last_modified.txt",'w'))

				elif (files in last_modified_dict) & (os.path.getmtime(files) > last_modified_dict[files]) :
					last_modified_dict[files] = os.path.getmtime(files)
					print "uploading ..from try block elif" , files
					k = Key(bucket)
					k.key = files
					k.set_contents_from_filename(path+files)
					json.dump(last_modified_dict, open("last_modified.txt",'w'))
				
				else :
					print "skipping file from try block else ",files


		bucket.set_acl('public-read')


	except IOError: 

		print "in exception block"
		last_modified_dict = defaultdict()
		for files in list_of_files:
			last_modified_dict[files]= os.path.getmtime(files)
		print last_modified_dict
		json.dump(last_modified_dict, open("last_modified.txt",'w'))

		for files in list_of_files:
		   	if not files.startswith('.'):
				print 'uploading file from IOError Exception code block' ,files
				k = Key(bucket)
				k.key = files
				k.set_contents_from_filename(path+files)

	bucket.set_acl('public-read')

	print "========================================================================================"
	print "visit http://cloudcrate.hari.s3.amazonaws.com/list.html to take a look at the bucket & uploaded files"
	print "========================================================================================"