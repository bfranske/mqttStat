#===========================================================================
#
# Command line utility to set variables on thermostat
#
#===========================================================================

import argparse
import sys
import zmq

def set_main():
	parser = argparse.ArgumentParser(description='Change settings on an RCS serial thermostat')
	parser.add_argument('-t', '--setpoint', action='store', type=int, dest='setpoint', metavar='TEMP', help='Adjust thermostat setpoint to TEMP')
	parser.add_argument('-f', '--fan', action='store', dest='fan', metavar='MODE', help='Set fan MODE to auto or on')
	parser.add_argument('-s', '--schedule-control', action='store', dest='control', metavar='MODE', help='Set system schedule MODE to run or hold')
	parser.add_argument('-m', '--mode', action='store', dest='mode', metavar='MODE', help='Set system MODE to off, heat, cool, or auto')
	parser.add_argument('-c', '--clock', action='store_true', dest='setclock', help='Set the thermostat clock to match the PC')
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
	settings= {}
	changes = {}
	if options.setpoint:
		settings.update({"function":"setBasic"})
		changes.update({"setPoint":options.setpoint})
	if options.fan:
		if options.fan.lower() == "auto":
			settings.update({"function":"setBasic"})
			changes.update({"fanMode":0})
		elif options.fan.lower() == "on":
			settings.update({"function":"setBasic"})
			changes.update({"fanMode":1})
	if options.control:
		if options.control.lower() == "hold":
			settings.update({"function":"setBasic"})
			changes.update({"scheduleControl":0})
		elif options.control.lower() == "run":
			settings.update({"function":"setBasic"})
			changes.update({"scheduleControl":1})
	if options.mode:
		if options.mode.lower() == "off":
			settings.update({"function":"setBasic"})
			changes.update({"mode":"O"})
		elif options.mode.lower() == "heat":
			settings.update({"function":"setBasic"})
			changes.update({"mode":"H"})
		elif options.mode.lower() == "cool":
			settings.update({"function":"setBasic"})
			changes.update({"mode":"C"})
		elif options.mode.lower() == "auto":
			settings.update({"function":"setBasic"})
			changes.update({"mode":"A"})
	if options.setclock:
		settings.update({"function":"setBasic"})
		changes.update({"updateClock":1})
	# If there are some settings to change send the changes to the socket
	if settings:
		settings.update({"changes":changes})
		socket.send_json(settings)
		response=socket.recv_json()
	#Close the socket interface and context
	context.destroy()
