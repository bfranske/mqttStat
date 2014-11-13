#! /usr/bin/python

import pystat
import sys
import string
import json
from optparse import OptionParser
from lxml import etree
from time import localtime, strftime, strptime

def convertWeekToXML(weekSched):
	# Returns an XML etree version of the weekSched array
	root = etree.Element("schedule")
	day = {}
	day_number = {}
	day_name = {}
	
	for i in sorted(weekSched):
		day[i] = etree.SubElement(root, "day")
		# Get the current day number from the time_struct of the first period
		day_number[i] = etree.SubElement(day[i], "day_number").text = str(int(strftime("%w",weekSched[i]['period1']['schedTime']))+1)
		# Save the current day name to make the XML more human-readable but this is NOT used anythere, only the day_number is!
		day_name[i] = etree.SubElement(day[i], "day_name").text = strftime("%A",weekSched[i]['period1']['schedTime'])
		
		period = {}
		period_number = {}
		period_setpointHeating = {}
		period_setpointCooling = {}
		period_schedTime = {}
		
		for k in sorted(weekSched[i]):
			period[k] = etree.SubElement(day[i], "period")
			period_number[k] = etree.SubElement(period[k], "period_number").text = str(weekSched[i][k]['rcs_period_number'])
			period_schedTime[k] = etree.SubElement(period[k], "schedTime").text = strftime("%H%M",weekSched[i][k]['schedTime'])
			period_setpointHeating[k] = etree.SubElement(period[k], "setpointHeating").text = str(weekSched[i][k]['setpointHeating'])
			period_setpointCooling[k] = etree.SubElement(period[k], "setpointCooling").text = str(weekSched[i][k]['setpointCooling'])
	
	return root

def convertWeekToJSON(weekSched):
	# Returns a JSON string version of the weekSched array
	jsonWeekSched = {}
	for day in weekSched:
		jsonWeekSched[day] = {}
		for period in weekSched[day]:
			jsonWeekSched[day][period] = {}
			for item in weekSched[day][period]:
				jsonWeekSched[day][period][item] = {}
				if item=='schedTime':
					jsonWeekSched[day][period][item]=strftime("%H%M",weekSched[day][period]['schedTime'])
				else:
					jsonWeekSched[day][period][item]=weekSched[day][period][item]
	return jsonWeekSched

def convertXMLToWeek(weekXML):
	# Returns a week-style array of the XML data
	weekSched = {}
	i = 1
	for day in weekXML:
		k = 1
		daySched = {}
		for period in day:
			periodSched = {}
			# Day number is here
			if period.tag == 'day_number':
				day_number = int(period.text)
			for element in period:
				# Period number, time and setpoints are here
				if element.tag == 'period_number':
					periodSched['period'] = int(element.text)
				if element.tag == 'setpointCooling':
					periodSched['setpointCooling'] = element.text
				if element.tag == 'setpointHeating':
					periodSched['setpointHeating'] = element.text
				if element.tag == 'schedTime':
					schedTime = element.text
					pythonDOW = str(day_number-1)
					periodSched['schedTime'] = strptime(pythonDOW + schedTime,"%w%H%M")
			if period.tag == 'period':
				daySched[k] = periodSched
				k += 1
		weekSched[i] = daySched
		i += 1
	return weekSched

def saveSched(fileName,format):
#	t = pystat.thermostat('/dev/ttyUSB0')
#	weeksched=t.getweeksched()
#	t.close()
	weeksched=getSched()
	if format=="xml":
		etree.ElementTree(convertWeekToXML(weeksched)).write(fileName, pretty_print=True)
	return

def loadSched(fileName,format):
	weekXML = etree.parse(fileName).getroot()
	t = pystat.thermostat('/dev/ttyUSB0')
	if format=="xml":
		t.setweeksched(convertXMLToWeek(weekXML))
	t.close()
	return

def getSched():
	t = pystat.thermostat('/dev/ttyUSB0')
	weeksched=t.getweeksched()
	t.close()
	return weeksched

def stoutSched(format):
	weeksched=getSched()
	if format=="xml":
		etree.ElementTree(convertWeekToXML(weeksched)).write(sys.stdout, pretty_print=True)
	if format=="json":
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
		metavar="FILE", help="Load the weekly schedule from FILE")
        parser.add_option("-o", "--stout",
                action="store_true", dest="stout",
                help="Send the current weekly schedule to standard output")
	parser.add_option("-j", "--json",
		action="store_true", dest="json", default=False,
		help="Use JSON format input/output")
	parser.add_option("-x", "--xml",
                action="store_true", dest="xml", default=True,
                help="Use XML format input/output")
	(options, args) = parser.parse_args()
	if options.json:
		format="json"
	elif options.xml:
		format="xml"
	if options.saveFile:
		saveSched(options.saveFile,format)
	elif options.loadFile:
		loadSched(options.loadFile,format)
	if options.stout:
		stoutSched(format)

if __name__ == "__main__":
    main()

