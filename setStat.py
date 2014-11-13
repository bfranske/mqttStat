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
        parser.add_option("-s", "--schedule-control",
                action="store", type="string", dest="control",
                metavar="CONTROL", help="Set system schedule CONTROL to run or hold")
        parser.add_option("-m", "--mode",
                action="store", type="string", dest="mode",
                metavar="MODE", help="Set system MODE to off, heat, cool, or auto")
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
        if options.control:
                if string.lower(options.control) == "hold" or string.lower(options.control) == "run":
                        t.setschedcontrol(string.lower(options.control))
        if options.mode:
                if string.lower(options.mode) == "off" or string.lower(options.mode) == "heat" or string.lower(options.mode) == "cool" or string.lower(options.mode) == "auto":
                        t.setmode(string.lower(options.mode))
	if options.setclock:
		t.setclocktopc()
	t.close()

if __name__ == "__main__":
    main()

