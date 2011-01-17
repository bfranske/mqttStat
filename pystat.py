# pyStat Python module

#Copyright 2010-2011 Ben Franske (ben@franske.com http://www.benfranske.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import serial
from time import localtime, strftime, strptime
global tstat_address
global local_address

# Thermostat address is 1 by default
tstat_address=1

# Local address is 0 by default
local_address=0

# pyStat is a Python module for sending and receiving information from
# the Residential Control Systems (RCS) TR-60 (and possibly other RCS)
# thermostats.
#
# Example usage:
#
# Create a thermostat object that can send and receive information from
# the thermostat
# 	t = pystat.thermostat('/dev/ttyUSB0')
# Adjust the thermostat setpoint to 72 degrees)
# 	t.setpoint(72)
# Close the thermostat object and release the serial port
# 	t.close()
#

class thermostat:

	commands = {
		'setpoint' :		'SP',
		'setpointheat' :	'SPH',
		'setpointcool' :	'SPC',
		'setmode' :		'M',
		'setfan' :		'F',
		'tempformat' :		'CFM',
		'textmsg' :		'TM',
		'settime' :		'TIME',
		'setdate' :		'DATE',
		'setdayofweek' :	'DOW',
		'schedulecontrol' :	'SC',
		'scheduleentry' :	'SE',
		'returnstatus' :	'R'}

	def sendBasicSet(self,tstat_address,local_address,cmd,value):
		# Sends a standard command to the thermostat
		if tstat_address is None: return "Invalid thermostat address"
		if local_address is None: return "Invalid local address"
		tstat_address = str(tstat_address)
		local_address = str(local_address)
		value = str(value)
		msg = "A=" + tstat_address + " O=" + local_address + " " + cmd + "=" + value + "\r"
		self.send_msg(msg,0)
		return

	def getLine(self,tstat_address,local_address,cmd,value):
		# Send a status request message and return one line
		if tstat_address is None: return "Invalid thermostat address"
                if local_address is None: return "Invalid local address"
                tstat_address = str(tstat_address)
                local_address = str(local_address)
                value = str(value)
                msg = "A=" + tstat_address + " O=" + local_address + " " + cmd + "=" + value + "\r"
		line = ''
                line = self.send_msg(msg,1)
                return line

	def send_msg(self,message,expectdata=0):
		# This method is responsible for handling all outgoing serial messages.
		try:
			if not self.ser.isOpen():
				self.ser.open()
		except serial.SerialException:
			raise
			return "Could not open serial port"
		self.ser.write(message)
		line = ''
		# Only some of the commands return data
		if expectdata is 1:
			while True:
			        char = self.ser.read(1)
			        line += char
			        if char == '\r':
			                break
		return line

	def __init__(self, serPort=None, verbose=False):

		# Serial port initialization
		try:
			if serPort is None:
				raise Exception('Serial port not selected')
			else:
				if type(serPort) is str:
					port = serPort
				else:
					raise Exception('User specified serial port is not a string.')
				self.ser = serial.Serial(port,9600,8,'N',1,timeout=1)
		except serial.SerialException:
			raise
		except NameError:
			self.ser = None
			raise

# --- Low-level/internal methods ---
			
	def close(self):
		# Use close to release the serial port and socket interface.
		try:
			self.ser.close()
		except:
			pass

# --- High-level methods ---

	def setpoint(self, setpoint):
		# Adjust the thermostat setpoint for the currently selected mode (heating or cooling)
		status = self.sendBasicSet(tstat_address,local_address,self.commands['setpoint'],setpoint)
		return
	def setfan(self, setfan):
		# Put the fan in auto mode (FALSE) or manual on mode (TRUE)
		if setfan:
			status = self.sendBasicSet(tstat_address,local_address,self.commands['setfan'],1)
		elif not setfan:
			status = self.sendBasicSet(tstat_address,local_address,self.commands['setfan'],0)
		return
	def setclocktopc(self):
		# Set the time, date and day of week on the thermostat to match the local system time on the computer
		status = self.sendBasicSet(tstat_address,local_address,self.commands['settime'],strftime("%H:%M:%S",localtime()))
		status = self.sendBasicSet(tstat_address,local_address,self.commands['setdate'],strftime("%m/%d/%y",localtime()))
		status = self.sendBasicSet(tstat_address,local_address,self.commands['setdayofweek'],str(int(strftime("%w",localtime())) + 1))
		return
	def currentsettings(self):
		# Return an array with the current settings of the thermostat
		settings = self.getLine(tstat_address,local_address,self.commands['returnstatus'],1)
		data = settings.split()
		parsedData = {}
		for i in data:
		        subdata = i.split("=")
		        if subdata[0] == "A":
		                parsedData['address']=subdata[1]
		        elif subdata[0] == "O":
		                parsedData['originator']=subdata[1]
		        elif subdata[0] == "Z":
		                parsedData['zone']=subdata[1]
		        elif subdata[0] == "T":
		                parsedData['temperature']=subdata[1]
		        elif subdata[0] == "SP":
		                parsedData['setpoint']=subdata[1]
		        elif subdata[0] == "SPH":
		                parsedData['setpointHeating']=subdata[1]
		        elif subdata[0] == "SPC":
		                parsedData['setpointCooling']=subdata[1]
		        elif subdata[0] == "M":
		                parsedData['mode']=subdata[1]
		        elif subdata[0] == "FM":
		                parsedData['fanMode']=subdata[1]
		        elif subdata[0] == "SC":
		                parsedData['scheduleControl']=subdata[1]
		return parsedData
	def getperiodsched(self, day, period):
		# Return an array with the schedule entries for a given day and period (day and period given numerically in RCS format)
		# Sun=1, Sat=7
		# Note that schedTime is returned in the python struct_time format (with only hour, minute and weekday set)
		settings = self.getLine(tstat_address,local_address,self.commands['scheduleentry'] + str(day) + '/' + str(period),'?')
                data = settings.split()
                parsedData = {}
		pythonDOW = str(day-1)
		for i in data:
			subdata = i.split("=")
		#	if subdata[0] == "A":
		#		parsedData['address']=subdata[1]
		#	elif subdata[0] == "O":
		#		parsedData['originator']=subdata[1]
			if subdata[0] == self.commands['scheduleentry'] + str(day) + '/' + str(period):
				parsedData['schedTime']=strptime(pythonDOW + subdata[1][0:4],"%w%H%M")
				parsedData['setpointHeating']=subdata[1][4:6]
				parsedData['setpointCooling']=subdata[1][6:8]
		parsedData['period']=period
                return parsedData
	def getdaysched(self, day):
		# Return an array with the daily schedule for the given day (given numerically where Sun=1, Sat=7)
		daysched = {}
		for i in range(1,5):
			daysched[i]=self.getperiodsched(day, i)
		return daysched
	def getweeksched(self):
                # Return an array with the complete weekly schedule (where Sun=1, Sat=7)
                weeksched = {}
                for i in range(1,8):
                        weeksched[i]=self.getdaysched(i)
                return weeksched
        def setperiodsched(self, schedule):
                # Accepts an array with the entries for a given day and period in the same format as getperiodsched returns
                # Note that schedTime is in the python struct_time format (with only hour, minute and weekday used)
		day=int(strftime("%w",schedule['schedTime']))+1
		time=strftime("%H%M",schedule['schedTime'])
		status = self.sendBasicSet(tstat_address,local_address,self.commands['scheduleentry'] + str (day) + '/' + str(schedule['period']),time + schedule['setpointHeating'] + schedule['setpointCooling'])
                return
	def setdaysched(self, schedule):
		# Accepts a multi-dimensional array with the entries for all periods of a given day in the same format as getdaysched returns
		# Note that schedTime is in the python struct_time format (with only hour, minute and weekday used)
		daysched = {}
                for i in range(1,5):
			self.setperiodsched(schedule[i])
                return
        def setweeksched(self, schedule):
                # Accepts a multi-dimensional array with the entries for all periods of all days in the same format as getweeksched returns
                # Note that schedTime is in the python struct_time format (with only hour, minute and weekday used)
                daysched = {}
                for i in range(1,5):
                        self.setdaysched(schedule[i])
                return
