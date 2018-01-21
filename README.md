# RCS Thermostat <-> MQTT bridge

This is a Python 3 package that communicates with an RCS Serial Thermostat (tested RCS TR-60) over a serial link, polls the thermostat for status, writing the restults back to MQTT topics and watches MQTT topics for updates which are transmitted back to the thermostat.  It allows an RCS Serial Thermostat to be integrated into and controlled from anything that can use MQTT. The package also includes command line utilities for obtaining information from the thermostat, setting variables on the thermostat, and loading and saving schedules from/to the thermostat.

This package is based on my previous work on command line python utilities for the RCS Serial Thermostats [pyStat](https://sourceforge.net/p/pystat/code/ci/master/tree/). The pyStat module and supporting example applications have been updated for Python 3, socket based communication, and of course MQTT support. The project has also undergone a name change from pyStat to mqttStat. For details see the [changelog file](changelog.md).

Version: 1.0

# Current Status

This software currently provides very basic functionality. It would probably be fair to consider it alpha or beta software. Some configuration is hard-coded in the Python files (e.g. the MQTT server is fixed to localhost, the serial port name is fixed to /dev/tty-tstat0, etc.), and only Fahrenheit temperatures are supported.

# System Requirements
* \*NIX based system
* Systemd (for provided init/autostart functionality)
* Python 3
* An MQTT broker
* Mosquitto Clients (for MQTT testing)
* GIT (for installation)
* Compatible RCS serial thermostat (tested on RCS TR-60)
* PHP (for web UI example)

# Installation
See the [installation instructions](INSTALL.md).

# Usage
Once the mqttStat daemon is running correctly in the background (see the [installation instructions](INSTALL.md)) you can use MQTT and the command line utilities provided to interact with the thermostat.

## Command Line Interaction
Command line utilities are located in /opt/mqttStat/bin/ (assuming /opt/mqttStat is the directory you installed to). The getStat and setStat commands to read and set basic settings on the thermostat. The schedule can be loaded and saved from your thermostat using the schedStat command. All command have a `-h` option to see basic command line help. Try `getStat -b` to get all basic settings from the thermostat in a human readable format.

## MQTT Interaction
You should also have a `tstat/` topic appearing on your MQTT server which has get and set subtopics.

Use `mosquitto_sub -v -t 'tstat/#'` to see the available tstat/get MQTT topics. Use `mosquitto_pub -t tstat/set/setPoint -m "65"` to attempt to adjust the setpoint on the thermostat to 65 degrees.

Available tstat/set/ MQTT topics are:
* tstat/set/setPoint (takes an integer)
* tstat/set/setPointHeat (takes an integer)
* tstat/set/setPointCool (takes an integer)
* tstat/set/mode (takes a one-letter string "O", "H", "C", or "A")
* tstat/set/fanMode (takes a 0 or 1)
* tstat/set/scheduleControl (takes a 0 or 1)

## WWW Interaction
There are some very basic examples of web based UIs which can be used to adjust settings on the thermostat and read/load schedule data. These are completely insecure and simply pass data back and forth through the command line utilities. You will almost certainly need to update the command line utilities path in the PHP files in order to make these work. If you're writing your own UI a better way to do this is probably to have PHP talk directly to the 0MQ (aka ZMQ) socket which mqttStat is listening on. The example files are in the www-sample directory.

# To Do

* Graceful failure for command line get/set/sched if unable to connect to socket
* Add support for a clock_sync command. If this flag is set in MQTT then add a clock sync to the outgoing message queue every X minutes (store in variable for future YAML configuration)
* Create PIP install files
* Cleanup of pystat.py (what functions are needed in there vs. in the daemon)
* More Documentation!
* Support for YAML configuration (eg. of serial port, mqtt server, tstat model which affects scheduling capability, etc.)
* Support for JINJA2 templating (eg. of MQTT topics)
* Improve schedule entry web UI (eg. am/pm)
* Support for text message/notifications to wall unit, wall unit keypad locking, outside temperature to wall unit, multi-stage heating status
* Deal with Fahrenheit/Celsius (ie. valid setpoint ranges)
* Add timezone support so something other than localtime can be used when setting the clock (store TZ in variable for future YAML configuration).
* Setup a way to disable MQTT and use the socket only
* Improve Web UI demo to talk directly to the zmq socket
