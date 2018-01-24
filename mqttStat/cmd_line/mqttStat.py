#===========================================================================
#
# Main setup and looping code for background daemon.
#
#===========================================================================
from . import pystat
import signal
import sys
import re
import paho.mqtt.client as mqtt
import zmq
from time import localtime, strftime
import json
import logging

previous_normalData_raw = ''
previous_normalData_dict = {}
previous_schedControl_raw = ''
last_full_status = {}
commands_to_send = []
blocking_functions_to_run = []

# Catch a signal interrupt (eg. CTRL-C) and disconnect from the serial port
def exit_signal(signal, frame):
	logger.debug('Received Exit Signal')
	global t, mqttc, context
	# Close the tstat object serial connection
	t.close()
	logger.debug('Closed Thermostat Serial Interface Connection')
	# Stop the MQTT thread
	mqttc.loop_stop(force=False)
	mqttc.disconnect()
	logger.debug('Closed MQTT Connection')
	#Close the socket interface and context
	context.destroy()
	logger.debug('Closed Socket Connection')
	#End logging
	logging.shutdown()
	sys.exit(0)
	return

# This function returns all new or changed keys in the fresh dictionary when compared with the stale dictionary
def dict_changes(fresh, stale):
	fresh_keys = set(fresh.keys())
	stale_keys = set(stale.keys())
	intersect_keys = fresh_keys.intersection(stale_keys)
	modified = {o : (fresh[o]) for o in intersect_keys if fresh[o] != stale[o]}
	added = {o : (fresh[o]) for o in (fresh_keys - stale_keys)}
	modified.update(added)
	return modified

def publish_status(changes):
	# Changes is a dict of new or changed values which need to be published
	# The dict keys will be used as the last part of the MQTT topic
	pubMsgs = []
	for o in set(changes.keys()):
		(rc, mid) = mqttc.publish("tstat/get/"+o, changes[o], qos=0, retain=True)
	return

# Return dict of any normal status variable changes which need publishing to MQTT
def check_normal_status():
	global previous_normalData_raw
	global previous_normalData_dict
	global last_full_status
	changes = {}
	# Get the raw output from the thermostat's status command
	fresh_data_raw = t.getLine(1,0,t.commands['returnstatus'],1)
	# Check to see if the status of anything has changed compared to the previous query
	if fresh_data_raw != previous_normalData_raw:
		# If there has been a change then parse the data using a regular expression
		pattern = r'^A=0 O=1(?=.* T=(?P<temp>[0-9\-][0-9][0-9]?))(?=.* SP=(?P<setPoint>[0-9][0-9][0-9]?))(?=.* SPH=(?P<setPointHeat>[0-9][0-9][0-9]?))(?=.* SPC=(?P<setPointCool>[0-9][0-9][0-9]?))(?=.* M=(?P<mode>[OHCA(EH)I]))(?=.* FM=(?P<fanMode>[01]))'
		m=re.match(pattern, fresh_data_raw)
		# If there are any matches (there should be unless something nonsensical is returned by the thermostat) from the regular expression process them
		if m:
			# Store the matches in a dictionary
			fresh_data_dict = m.groupdict()
			# Get a dictionary comprised of new or changed values only
			changes=dict_changes(fresh_data_dict,previous_normalData_dict)
			# Store the current data in dictionary form so we can run future comparisons against it with new data and find the specific changes
			previous_normalData_dict = fresh_data_dict
			# Update the current status to reflect the new values
			last_full_status.update(fresh_data_dict)
		# Store the current data string in raw format so we can run future comparisons against it with new data and find if there have been any changes
		previous_normalData_raw=fresh_data_raw
	if changes:
		return changes
	return None

# Return dict of schedule control changes which need publishing to MQTT
def check_schedule_control():
	global previous_schedControl_raw
	global last_full_status
	changes = {}
	# Get the raw output from the thermostat's schedule control status command
	fresh_data_raw = t.getLine(1,0,t.commands['schedulecontrol'],"?")
	# Check to see if the status of anything has changed compared to the previous query
	if fresh_data_raw != previous_schedControl_raw:
		# If there has been a change then parse the data using a regular expression
		pattern = r'^A=0 O=1(?=.* SC=(?P<scheduleControl>[01]))'
		m=re.match(pattern, fresh_data_raw)
		# If there are any matches (there should be unless something nonsensical is returned by the thermostat) from the regular expression process them
		if m:
			# Store the matches in a dictionary, any match is a change because we are only checking one variable and we have already determined the raw data has changed
			changes = m.groupdict()
			# Update the current status to reflect the new schedule control values
			last_full_status.update(changes)
		# Store the current data string in raw format so we can run future comparisons against it with new data and find if there have been any changes
		previous_schedControl_raw=fresh_data_raw
	if changes:
		return changes
	return None

# Handle Incoming MQTT adjustment events
def mqtt_adjustment(client, userdata, message):
	value=message.payload.decode('ascii')
	#get the adjustment from the last part of the MQTT topic
	pattern = r'^tstat/set/(.*)'
	m=re.match(pattern, message.topic)
	build_commands(m.group(1),value)
	return

# Validate adjustments, build commends, add to command queue
def build_commands(adjustment,value):
	global commands_to_send
	global t
	# Check to see which adjustment is required and if the input value is valid
	# Need to convert value from string to float then to int if it's a number.
	# Python won't convert straight from float in a string to an int in one step.
	if adjustment == 'setPoint' and (39 < int(float(value)) < 114):
		cmd = t.buildBasicSet(1,0,t.commands['setpoint'],int(float(value)))
		commands_to_send.append(cmd)
		return
	elif adjustment == 'setPointHeat' and (39 < int(float(value)) < 110):
		cmd = t.buildBasicSet(1,0,t.commands['setpointheat'],int(float(value)))
		commands_to_send.append(cmd)
		return
	elif adjustment == 'setPointCool' and (43 < int(float(value)) < 114):
		cmd = t.buildBasicSet(1,0,t.commands['setpointcool'],int(float(value)))
		commands_to_send.append(cmd)
		return
	elif adjustment == 'fanMode' and (int(float(value)) is 0 or 1):
		cmd = t.buildBasicSet(1,0,t.commands['setfan'],int(float(value)))
		commands_to_send.append(cmd)
		return
	elif adjustment == 'scheduleControl' and (int(float(value)) is 0 or 1):
		cmd = t.buildBasicSet(1,0,t.commands['schedulecontrol'],int(float(value)))
		commands_to_send.append(cmd)
		return
	elif adjustment == 'mode' and re.search(r'[OHCA(EH)I]', value):
		cmd = t.buildBasicSet(1,0,t.commands['setmode'],value)
		commands_to_send.append(cmd)
		return
	elif adjustment == 'updateClock' and (int(float(value)) is 1):
		cmd = t.buildBasicSet(1,0,t.commands['settime'],strftime("%H:%M:%S",localtime()))
		commands_to_send.append(cmd)
		cmd = t.buildBasicSet(1,0,t.commands['setdate'],strftime("%m/%d/%y",localtime()))
		commands_to_send.append(cmd)
		cmd = t.buildBasicSet(1,0,t.commands['setdayofweek'],str(int(strftime("%w",localtime())) + 1))
		commands_to_send.append(cmd)
		return
	return

# Setup MQTT subscriptions and callbacks
def mqtt_subscription_setup():
	mqttc.message_callback_add("tstat/set/setPoint", mqtt_adjustment)
	mqttc.message_callback_add("tstat/set/setPointHeat", mqtt_adjustment)
	mqttc.message_callback_add("tstat/set/setPointCool", mqtt_adjustment)
	mqttc.message_callback_add("tstat/set/fanMode", mqtt_adjustment)
	mqttc.message_callback_add("tstat/set/scheduleControl", mqtt_adjustment)
	mqttc.message_callback_add("tstat/set/mode", mqtt_adjustment)
	mqttc.subscribe("tstat/set/#", 0)
	return

# Handle incoming socket messages
def socket_message_handler(msg):
	global last_full_status
	global socket
	global blocking_functions_to_run
	# We always need to send back some data on a ZMQ Req-Rep socket so let's set some default data to return
	response = {'done':1}
	if msg['function'] == 'setBasic':
		#do some setting based on the included nested dict (foreach k,v run an adjustment)
		for key, value in msg['changes'].items():
			build_commands(key,value)
	elif msg['function'] == 'getStatus':
		#send back the latest normal status
		response = last_full_status
	elif msg['function'] == 'getSchedule':
		# Query the tstat and send back a schedule object
		# Add a get_week_schedule blocking function to the queue
		blocking_functions_to_run.append('get_week_schedule(t,socket)')
		# We do not want to send a socket response yet, that will be handled by the blocking function
		return
	elif msg['function'] == 'setSchedule':
		#get the schedule object from the nested dict and update the tstat accordingly
		schedule=json.dumps(msg['scheduleData'])
		blocking_functions_to_run.append('set_week_schedule(t,socket,'+schedule+')')
		# We do not want to send a socket response yet, that will be handled by the blocking function
		return
	else:
		response = {'done':0}
	socket.send_json(response)
	return

# Blocking function to get the weekly schedule and return it to the socket as JSON data
def get_week_schedule(t, socket):
	weeksched=t.getweeksched()
	socket.send_json(weeksched)
	return

# Blocking function to set the weekly schedule
def set_week_schedule(t, socket, schedule):
	t.setsched(schedule)
	socket.send_json({'done':1})
	return

# Main Setup
def setup():
	# Setup logging (at the debug level for now)
	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',level=logging.DEBUG)
	global logger
	logger = logging.getLogger('mqttStat')
	global t
	logger.debug('Connecting to Thermostat Serial Interface')
	t = pystat.thermostat('/dev/tty-tstat0')
	signal.signal(signal.SIGINT, exit_signal)
	signal.signal(signal.SIGTERM, exit_signal)
	global mqttc
	logger.debug('Connecting to MQTT Broker')
	mqttc = mqtt.Client()
	mqttc.on_connect = lambda client,userdata,flags,rc: logger.debug('Connected to MQTT Broker: '+mqtt.connack_string(rc))
	mqttc.on_disconnect = lambda client,userdata,rc: logger.debug('Disconnected from MQTT Broker: '+rc)
	mqttc.connect("localhost", 1883, 60)
	# Start the MQTT thread
	mqttc.loop_start()
	# Setup the MQTT subscriptions
	mqtt_subscription_setup()
	# Setup the local socket for IPC
	global context, socket
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	logger.debug('Opening Socket Connection')
	socket.bind("ipc://@/mqttStat")
	return

# Main Loop
def loop():
	global commands_to_send, blocking_functions_to_run
	global t
	global socket
	# Check to see if there are any Socket received commands to be dealt with. Can't do this if
	# there is a blocking function to run because that still needs to respond to the socket.
	while not blocking_functions_to_run:
		try:
			socketMessage = socket.recv_json(flags=zmq.NOBLOCK)
			socket_message_handler(socketMessage)
		except zmq.Again as e:
			break
	# Check to see if there are any MQTT set commands waiting to be sent to the thermostat
	if commands_to_send:
		# Send each waiting command
		for cmd in commands_to_send:
			logger.debug('Sending Set Command: %s', cmd)
			t.send_msg(cmd,0)
			commands_to_send.remove(cmd)
	# Check to see if there are any blocking functions which need access to the tstat object
	# (eg. getting or setting schedule which requires multiple writes and reads to accomplish)
	# and will send their response directly back to the socket.
	if blocking_functions_to_run:
		# Run each blocking function
		for func in blocking_functions_to_run:
			logger.debug('Running Blocking Function: %s', func)
			eval(func)
			blocking_functions_to_run.remove(func)
	changes = {}
	# Check to see if there have been any changes to the normal status variables of the thermostat
	normalStatusChanges = check_normal_status()
	if normalStatusChanges:
		changes.update(normalStatusChanges)
	# Check to see if there have been any changes to the schedule control of the thermostat
	scheduleControlChanges = check_schedule_control()
	if scheduleControlChanges:
		changes.update(scheduleControlChanges)
	# Check to see if there have been any changes which require publishing
	if changes:
		#logger.debug('Changes Detected: %s', changes)
		publish_status(changes)
	return
