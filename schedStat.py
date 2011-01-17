#! /usr/bin/python

import pystat
import sys
import string
from optparse import OptionParser
from lxml import etree
from time import localtime, strftime, strptime

def convertWeekToXML(weekSched):
	# Returns an XML etree version of the weekSched array
	root = etree.Element("schedule")
	day = {}
	day_number = {}
	day_name = {}
	
	for i in weekSched:
		day[i] = etree.SubElement(root, "day")
		# Get the current day number from the time_struct of the first period
		day_number[i] = etree.SubElement(day[i], "day_number").text = str(int(strftime("%w",weekSched[i][1]['schedTime']))+1)
		# Save the current day name to make the XML more human-readable but this is NOT used anythere, only the day_number is!
		day_name[i] = etree.SubElement(day[i], "day_name").text = strftime("%A",weekSched[i][1]['schedTime'])
		
		period = {}
		period_number = {}
		period_setpointHeating = {}
		period_setpointCooling = {}
		period_schedTime = {}
		
		for k in weekSched[i]:
			period[k] = etree.SubElement(day[i], "period")
			period_number[k] = etree.SubElement(period[k], "period_number").text = str(weekSched[i][k]['period'])
			period_schedTime[k] = etree.SubElement(period[k], "schedTime").text = strftime("%H%M",weekSched[i][k]['schedTime'])
			period_setpointHeating[k] = etree.SubElement(period[k], "setpointHeating").text = str(weekSched[i][k]['setpointHeating'])
			period_setpointCooling[k] = etree.SubElement(period[k], "setpointCooling").text = str(weekSched[i][k]['setpointCooling'])
	
	return root

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

def saveSched(fileName):
	t = pystat.thermostat('/dev/ttyUSB0')
	weeksched=t.getweeksched()
	t.close()
	etree.ElementTree(convertWeekToXML(weeksched)).write(fileName, pretty_print=True)
	return

def loadSched(fileName):
	weekXML = etree.parse(fileName).getroot()
	t = pystat.thermostat('/dev/ttyUSB0')
	t.setweeksched(convertXMLToWeek(weekXML))
	t.close()
	return

def main():
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage, version="%prog 0.1")
	parser.add_option("-s", "--save",
		action="store", type="string", dest="saveFile",
		metavar="FILE",	help="Save the current weekly schedule to FILE")
	parser.add_option("-l", "--load",
		action="store", type="string", dest="loadFile",
		metavar="FILE", help="Load the weekly schedule from FILE")
	(options, args) = parser.parse_args()
	if options.saveFile:
		saveSched(options.saveFile)
	elif options.loadFile:
		loadSched(options.loadFile)

if __name__ == "__main__":
    main()

