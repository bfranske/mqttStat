#===========================================================================
#
# Command line utility to get and set schedule information from/on thermostat
#
#===========================================================================

import argparse
import zmq
import json
import sys
from time import localtime, strftime, strptime

def saveSched(weeksched,fileName):
	with open(fileName, 'w') as outfile:
		json.dump(weeksched,outfile,indent=4,sort_keys=True)
	outfile.close()
	return

def loadSched(fileName):
	with open(fileName, 'r') as infile:
		schedule=json.load(infile)
	infile.close()
	return schedule

def getSched():
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("ipc://@/mqttStat")
	socket.send_json({"function":"getSchedule"})
	weeksched=socket.recv_json()
	context.destroy()
	return weeksched

def setSched(schedule):
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("ipc://@/mqttStat")
	socket.send_json({"function":"setSchedule","scheduleData":schedule})
	response=socket.recv_json()
	context.destroy()
	return

def stdinSched():
	schedule=json.loads(sys.stdin.read())
	return schedule

def sched_main():
	parser = argparse.ArgumentParser(description='Get and change the schedule on an RCS serial thermostat')
	parser.add_argument('-s', '--save', action='store', dest='saveFile', metavar='FILE', help='Save the current weekly schedule to FILE')
	parser.add_argument('-l', '--load', action='store', dest='loadFile', metavar='FILE', help='Load one or more periods from FILE')
	parser.add_argument('-o', '--stdout', action='store_true', dest='stdout', help='Send the current weekly schedule to standard output')
	parser.add_argument('-i', '--stdin', action='store_true', dest='stdin', help='Load one or more periods from standard input')
	parser.add_argument('--version', action='version', version='%(prog)s 1.0')
	if len(sys.argv)==1:
		parser.print_help()
		return
	options = parser.parse_args()
	if options.saveFile or options.stdout:
		weeksched=getSched()
		if options.saveFile:
			saveSched(weeksched,options.saveFile)
		if options.stdout:
			print (json.dumps(weeksched,indent=4,sort_keys=True))
	elif options.loadFile:
		setSched(loadSched(options.loadFile))
	elif options.stdin:
		setSched(stdinSched())
