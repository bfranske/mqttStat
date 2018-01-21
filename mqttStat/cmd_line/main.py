#===========================================================================
#
# Command line parsing and main entry point for background daemon.
#
#===========================================================================
import argparse
import sys
from .mqttStat import setup, loop

'''
This file can be used to add argument parsing, reading of configuration file,
etc. before starting the background daemon. These are not yet implemented.
'''

def parse_args(args):
    '''Input is command line arguments w/o arg[0]
    Future functionality, not yet implemented
    '''
    p = argparse.ArgumentParser(prog="mqttStat", description="RCS Thermostat<->MQTT tool")
    p.add_argument("config", metavar="config.yaml", help="Configuration file to use.")
    sub = p.add_subparsers(help="Command help")
    return p.parse_args(args)

#===========================================================================
def main():
    '''
    # Future argument parsing and configuration loading

    args = parse_args(sys.argv[1:])

    # Load the configuration file.
    cfg = config.load(args.config)
    '''

    # Call the setup and loop functions from mqttStat.py
    setup()
    while True:
    	loop()

    return

#===========================================================================
