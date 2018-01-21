#===========================================================================
#
# Command line utility to obtain information from thermostat
#
#===========================================================================

#from optparse import OptionParser
import argparse
import zmq
import sys

def get_main():
	parser = argparse.ArgumentParser(description='Obtain information from an RCS serial thermostat')
	parser.add_argument('-t', '--temp', action='store_true', dest='temp', help='Get the current temperature')
	parser.add_argument('-s', '--setpoint', action='store_true', dest='sp', help='Get the current setpoint')
	parser.add_argument('-b', '--basic', action='store_true', dest='basicinfo', help='Get the basic variables in a human readable format')
	parser.add_argument('--version', action='version', version='%(prog)s 1.0')
	if len(sys.argv)==1:
		parser.print_help()
		return
	options = parser.parse_args()
	# Begin main non-option code
	# Setup socket communication with mqttStat
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("ipc://@/mqttStat")
	# Get all the latest settings from mqttStat as a JSON string and store as a python dict
	socket.send_json({"function":"getStatus"})
	currentsettings=socket.recv_json()
	if options.temp:
		print (currentsettings['temp'])
	if options.sp:
		print (currentsettings['setPoint'])
	if options.basicinfo:
		print ("Temperature: " + currentsettings['temp'])
		print ("Set Point: " + currentsettings['setPoint'])
		print ("Mode: " + mode_to_english(currentsettings))
		print ("Fan Mode: " + fanMode_to_english(currentsettings))
		print ("Schedule Mode: "+ scheduleMode_to_english(currentsettings))
	#Close the socket interface and context
	context.destroy()

def mode_to_english(currentsettings):
	modes = {
		"H":	"heat",
		"O":	"off",
		"C":	"cool",
		"A":	"auto",
		"EH":	"emergency-heat"}
	return modes[currentsettings['mode']]

def fanMode_to_english(currentsettings):
	modes = {
		"0":	"auto",
		"1":	"on"}
	return modes[currentsettings['fanMode']]

def scheduleMode_to_english(currentsettings):
	modes = {
		"0":	"hold",
		"1":	"run"}
	return modes[currentsettings['scheduleControl']]
