#!/usr/bin/env python3
##########################################################################
# This program interfaces with a DHT11 sensor to collect temperature     #
# and humidity data before appending it to a CSV file. The output file   #
# is created if it does not already exist. By default, the data is       #
# collected and appended to the CSV file every hour by default. In the   #
# future, add ability to change the measurement interval.
#                                                                        #
# When looking at the DHT11 module from the front, the physical          #
# connections are as follows:                                            #
# DHT11 GND (pin 1) to Raspberry Pi ground                               #
# DHT11 DATA (pin 2) to Raspberry Pi pin 7                               #
# DHT11 VCC to 5 volts                                                   #
# NOTE: The above connection scheme is the exact same one as provided in #
# the Kuman kit code examples. Check the documentation for the DHT11     #
# example for more information.                                          #
#                                                                        #
# To use: first install apscheduler system wide because the Rpi.GPIO     #
# library does not work in a virtual environment!!!                      #
# To setup, run this command: pip3 install apscheduler                   #
# To run normally putting the output data in current directory:          #
#    ./collect_data.py                                                   #
# To run in background: ./collect_data.py &                              #
##########################################################################

import argparse, os, sys, time, csv
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import RPi.GPIO as GPIO

# Default file name to store data in
CSV_FILE = "climate_data.csv"

# Number of seconds in an hour, collect temp/humidity every hour
HOUR = 3600
# Verbose mode
VERBOSE = False

# Other globals
sched = BlockingScheduler()
outfile = CSV_FILE


# Interface with DHT11 and return a list of current temp and humidity
#  @returns on success a list is returned which contains two items, 
#  first is the temperature in Celsius and the second item is the 
#  humidity as a percentage. 
#
def collect():
    THdata = []
    channel = 7
    data = []
    GPIO.setmode(GPIO.BOARD)
    time.sleep(2)
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(channel, GPIO.HIGH)
    GPIO.setup(channel, GPIO.IN)
    while GPIO.input(channel) == GPIO.LOW:
        continue
    while GPIO.input(channel) == GPIO.HIGH:
        continue
    j = 0
    while j < 40:
        k = 0
        while GPIO.input(channel) == GPIO.LOW:
            continue
        while GPIO.input(channel) == GPIO.HIGH:
            k += 1
            if k > 100:
                break
        if k < 8:
            data.append(0)
        else:
            data.append(1)
        j += 1

    humidity_bit = data[0:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    check = 0
    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7 - i)
        humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
        temperature += temperature_bit[i] * 2 ** (7 - i)
        temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
        check += check_bit[i] * 2 ** (7 - i)
    tmp = humidity + humidity_point + temperature + temperature_point
    if check == tmp:
        if VERBOSE:
            print("temperature: %d.%d" %(temperature,temperature_point),"C","\thumidity:", humidity, "%")
        THdata.append(str(temperature) + "." + str(temperature_point) + "C")
        THdata.append(str(humidity) + "%")
        return THdata
    else:
        # wrong?
        time.sleep(1)
        return collect()


# Collect temperature and humidity data every hour
@sched.scheduled_job('interval', seconds=HOUR)
def timed_job():
    data = []
    # create timestamp as first column
    data.append(str(datetime.now()))
    # collect data
    dhtdata = collect()
    # append temp in C and humidity as a percentage to CSV file
    data.append(dhtdata[0])
    data.append(dhtdata[1])
    append_data(outfile, data)


# Append a row of data to the CSV file
#  @param filename string the name of the CSV file to open
#  @param data a list of strings containing the data to append
#  @returns number of bytes wrote to the file
#
def append_data(filename, data):
    n = 0
    with open(filename, "a", newline="") as fd:
        f = csv.writer(fd)
        n = f.writerow(data)
    return n


# Main code
if __name__ == "__main__":
    # Set up argument parser
    argp = argparse.ArgumentParser("collect_data.py",
                                   description="Use DHT11 to collect and "
                                   "store temperature and humidity data in a CSV file\n"
                                   "Connect the DHT11 data pin to Raspberry Pi pin 7")
    argp.add_argument("-o",
                      "--output", help="Store data in a different output file")
    argp.add_argument("-v",
                      "--verbose", help="Enable verbose mode",
                      action="store_true")

    # Parse arguments
    args = argp.parse_args()

    # If specified, change output file 
    if args.output is not None:
        outfile = args.output

    # Enable verbose mode if specified
    if args.verbose:
        VERBOSE = True
    
    # Start the hourly task
    try:
        sched.start()
    except KeyboardInterrupt:
        print("Received Ctrl+c, exiting...")
        exit(0)
