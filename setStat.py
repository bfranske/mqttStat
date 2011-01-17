#! /usr/bin/python

import pystat
import sys
import string
from optparse import OptionParser

def main():
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage, version="%prog 0.2")
	parser.add_option("-t", "--setpoint",
		action="store", type="int", dest="setpoint",
		metavar="TEMP",	help="Adjust thermostat setpoint to TEMP")
	parser.add_option("-f", "--fan",
		action="store", type="string", dest="fan",
		metavar="STATUS", help="Set fan STATUS to auto or on")
        parser.add_option("-c", "--clock",
                action="store_true", dest="setclock",
                help="Set the thermostat clock to match the PC")
	(options, args) = parser.parse_args()
	t = pystat.thermostat('/dev/ttyUSB0')
	if 39 < options.setpoint < 114:
		t.setpoint(options.setpoint)
	if options.fan:
		if string.lower(options.fan) == "auto":
			t.setfan(0)
		elif string.lower(options.fan) == "on":
			t.setfan(1)
	if options.setclock:
		t.setclocktopc()
	t.close()

if __name__ == "__main__":
    main()

