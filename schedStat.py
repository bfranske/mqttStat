#! /usr/bin/python

import pystat
import sys
import string
import json
from optparse import OptionParser
from lxml import etree
from time import localtime, strftime, strptime

def convertWeekToJSON(weekSched):
	# Returns a JSON string version of the weekSched array
	jsonWeekSched = {}
	for period in weekSched:
		jsonWeekSched[period] = {}
		for item in weekSched[period]:
			jsonWeekSched[period][item] = {}
			if item=='schedTime':
				jsonWeekSched[period][item]=strftime("%H%M",weekSched[period]['schedTime'])
			else:
				jsonWeekSched[period][item]=weekSched[period][item]
	return jsonWeekSched

def convertJsonToSched(jsonSched):
	# Returns a schedule style python array of the JSON data
	schedule = {}
	for period in jsonSched:
		schedule[period] = {}
		for item in jsonSched[period]:
			schedule[period][item] = {}
			if item=='schedTime':
				schedule[period][item]=strptime(str(int(jsonSched[period]['rcs_day_number'])-1) + jsonSched[period]['schedTime'],"%w%H%M")
			else:
				schedule[period][item]=int(jsonSched[period][item])
	return schedule

def saveSched(weeksched,fileName):
	with open(fileName, 'w') as outfile:
		json.dump(convertWeekToJSON(weeksched),outfile,indent=4,sort_keys=True)
	outfile.close()
	return

def loadSched(fileName):
	with open(fileName, 'r') as infile:
		schedule=convertJsonToSched(json.load(infile))
	infile.close()
	return schedule

def getSched():
	t = pystat.thermostat('/dev/ttyUSB0')
	weeksched=t.getweeksched()
	t.close()
	return weeksched

def setSched(schedule):
	t = pystat.thermostat('/dev/ttyUSB0')
	t.setsched(schedule)
	t.close()
	return

def stinSched():
	schedule=convertJsonToSched(json.loads(sys.stdin.read()))
	return schedule

def stoutSched(weeksched):
	print json.dumps(convertWeekToJSON(weeksched),indent=4,sort_keys=True)
	return

def main():
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage, version="%prog 0.2")
	parser.add_option("-s", "--save",
		action="store", type="string", dest="saveFile",
		metavar="FILE",	help="Save the current weekly schedule to FILE")
	parser.add_option("-l", "--load",
		action="store", type="string", dest="loadFile",
		metavar="FILE", help="Load one or more periods from FILE")
        parser.add_option("-o", "--stout",
                action="store_true", dest="stout",
                help="Send the current weekly schedule to standard output")
        parser.add_option("-i", "--stin",
                action="store_true", dest="stin",
                help="Load one or more periods from standard input")
	(options, args) = parser.parse_args()
	if options.saveFile or options.stout:
		weeksched=getSched()
		if options.saveFile:
			saveSched(weeksched,options.saveFile)
		if options.stout:
			stoutSched(weeksched)
	elif options.loadFile:
		setSched(loadSched(options.loadFile))
	elif options.stin:
		setSched(stinSched())
if __name__ == "__main__":
    main()

