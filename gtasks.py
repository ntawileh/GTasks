#!/usr/bin/env python

import argparse
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from os.path import expanduser

import sys
import parsedatetime.parsedatetime as pdt
import datetime
import os
from math import floor

from os.path import expanduser
from dateutil.relativedelta import *

def ensure_dir(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

def gtasks_init():
	storage = file.Storage(homedir + 'tokens.dat')
	credentials = storage.get()
	if credentials is None or credentials.invalid:
		credentials = tools.run_flow(FLOW, storage, flags)

	http = httplib2.Http()
	http = credentials.authorize(http)

	service = discovery.build('tasks', 'v1', http=http)
	return service

def display_task(task):
	t = { 'due': "No Date", 'title': "Untitled", 'notes': "" }
	t.update(task)
	print "%s\t%s\t%s" % (t["due"], t["title"], t["notes"])

def list_tasks():
	service = gtasks_init()
  	tasks = service.tasks().list(tasklist='@default').execute()
	for task in tasks['items']:
		display_task(task)
	  
def make_googletask(name="Unknown Task", notes="", due=""):
	try:
		service = gtasks_init()
	except client.AccessTokenRefreshError:
   		return ("The credentials have been revoked or expired, please re-run"
 			    "the application to re-authorize")

	task = {
		'title': name,
		'notes': notes,
		'due': due
	}

	try:
		result = service.tasks().insert(tasklist='@default', body=task).execute()
		return "+ Created Task " + result['title']
	except:
		return "*** FAILED to create task"
 
def build_rfc3339_phrase(datetime_obj):
	datetime_phrase = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')
	us = datetime_obj.strftime('%f')

	seconds = None
	try:
		seconds = datetime_obj.utcoffset().total_seconds()
	except:
		pass

	if seconds is None:
		datetime_phrase += 'Z'
	else:
		datetime_phrase += ('.%.6s%s%02d:%02d' % (
				us,
				('-' if seconds < 0 else '+'),
				abs(int(floor(seconds / 3600))),
				abs(seconds % 3600)
				))

	return datetime_phrase

def extract_due_date(task_string):
	reverse_list = task_string[:]
	reverse_list.reverse()
	
	main_list = task_string[:]
	
	word = ""
	date_string = ""
	
	# We iterate over the reversed list looking for the word 'by'. When we find it
	# we will have assembled the correct date string and we will also have popped
	# those words off the actual master string so we'll be left with a clean task
	# string to parse
	for word in reverse_list:
		main_list.pop()
		if word == "by":
			break
		
		date_string = word+" "+date_string
		
	# Check if we actually found the word by at all	and if not we just
	# return the original parameters
	if word!="by":
		return None, task_string
		
	try:
		the_date = datetimeFromString(date_string)
		
		return the_date, main_list
	except:
		return None, task_string
		

def make_task(task_string):
	due_date, remainder_string = extract_due_date(task_string)
	
	# If we dont have a date, the date is today
	if due_date==None:
		due_date=datetimeFromString("today")
	
	# Pull out any urls to stick in the description
	urls = []
	task_name_array = []
	for word in remainder_string:
		if "http://" in word:
			urls.append(word)
		elif "https://" in word:
			urls.append(word)
		else:
			task_name_array.append(word)
		
	task_name = " ".join(task_name_array)
	task_name = task_name.capitalize()
	
	task_notes = "\n".join(urls)
	
	# Here is a hack to fix tasks added straight from gmail
	try:
		if ((len(urls)==1) and "mail.google.com/mail" in urls[0]):
			name_split = task_name.rsplit("-", 2)
			# Double check that this is a add from gmail
#if name_split[-2].strip() == asana_user['email']:
				# OK this is definitely it
#				task_name = "Email: "+name_split[0].strip()
	except:
		# It's a hack so best efforts anyway. So PASS.
		pass

	try:
		print make_googletask(name=task_name, 
			notes=task_notes,
			due=build_rfc3339_phrase(due_date)
			)
	except:
		print "FAILED task add: '%s'" % (task_name)

def datetimeFromString(s):
	c = pdt.Calendar()
	result, what = c.parse( s )
	
	dt = None

	# what was returned (see http://code-bear.com/code/parsedatetime/docs/)
	# 0 = failed to parse
	# 1 = date (with current time, as a struct_time)
	# 2 = time (with current date, as a struct_time)
	# 3 = datetime

	if what in (1,2):
		# result is struct_time
		dt = datetime.datetime( *result[:6] )
	elif what == 3:
		# result is a datetime
		dt = result

	if dt is None:
		# Failed to parse
		raise ValueError, ("Don't understand date '"+s+"'")

	return dt	

def main():	
	global homedir, flags, CLIENT_SECRETS, FLOW
	homedir = expanduser("~") + "/.gtasks/" 
	ensure_dir(homedir)
	# Parser for command-line arguments.
 	parser = argparse.ArgumentParser(
			description=__doc__,
			formatter_class=argparse.RawDescriptionHelpFormatter,
			parents=[tools.argparser])
	flags = parser.parse_args("")
	CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), homedir+'client_secrets.json')
	FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
		scope=[
		'https://www.googleapis.com/auth/tasks',
		'https://www.googleapis.com/auth/tasks.readonly',
		],
		message=tools.message_if_missing(CLIENT_SECRETS))


	if(sys.argv[1] == "list"):
		list_tasks()
	else:
		make_task(sys.argv[1:])

######## START ##########
if len(sys.argv)==1:
	print "Usage: gtasks {task_description} [by {task_date}]"
	sys.exit(1)
main()

