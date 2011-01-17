#! /usr/bin/python

import pystat
import sys
import string
from optparse import OptionParser

def main():
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage, version="%prog 0.1")
	parser.add_option("-t", "--temp",
		action="store_true", dest="temp",
		help="Get the current temperature")
	parser.add_option("-s", "--setpoint",
		action="store_true", dest="sp",
		help="Get the current setpoint")
        parser.add_option("-b", "--basic",
                action="store_true", dest="basicinfo",
                help="Get the basic statistics")
	(options, args) = parser.parse_args()
	t = pystat.thermostat('/dev/ttyUSB0')
	if options.temp:
		print (t.currentsettings()['temperature'])
	if options.sp:
		print (t.currentsettings()['setpoint'])
	if options.basicinfo:
		info = t.currentsettings()
		print ("Temperature: " + info['temperature'])
		print ("Set Point: " + info['setpoint'])
		print ("Mode: " + info['mode'])
		print ("Fan Mode: " + info['fanMode'])
	t.close()

if __name__ == "__main__":
    main()

