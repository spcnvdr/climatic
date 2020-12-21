#!/usr/bin/env python3
###########################################################################
# This program interfaces with a DHT11 sensor to collect temperature      #
# and humidity data before appending it to a CSV file. The output file    #
# is created if it does not already exist. By default, the data is        #
# collected and appended to the CSV file every hour by default. In the    #
# future, add ability to change the measurement interval.                 #
#                                                                         #
# The CSV output creates the following columns:                           #
# timestamp, temperature in C, Temperature in F, humidity as a percentage #
#                                                                         #
# When looking at the DHT11 module from the front, the physical           #
# connections are as follows:                                             #
# DHT11 GND (pin 1) to Raspberry Pi ground                                #
# DHT11 DATA (pin 2) to Raspberry Pi pin 7                                #
# DHT11 VCC to 5 volts                                                    #
# NOTE: The above connection scheme is the exact same one as provided in  #
# the Kuman kit code examples. Check the documentation for the DHT11      #
# example for more information.                                           #
#                                                                         #
# To use: first install apscheduler system wide because the Rpi.GPIO      #
# library does not work in a virtual environment!!!                       #
# To setup, run this command: pip3 install apscheduler                    #
# To run normally putting the output data in current directory:           #
#    ./collect_data.py                                                    #
# To run in background: ./collect_data.py &                               #
###########################################################################

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


# Convert a temperature in Celsius to Fahrenheit
#  @param temperature the temperature in Celsius to convert
#  @returns temperature as a float
#
def ctof(temperature):
	return ((temperature / 5) * 9 ) + 32


# Interface with DHT11 and return a list of current temp and humidity
#  @returns on success a list is returned which contains three items, 
#  first is the temperature in Celsius, next is the temperature in Fahrenheit,
#  and the last item is the humidity as a percentage. 
#
def collect():
    THdata = []
    channel = 7
    data = []
    
    # Set up GPIO pin and send start condition
    GPIO.setmode(GPIO.BOARD)
    time.sleep(2)
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(channel, GPIO.HIGH)
    GPIO.setup(channel, GPIO.IN)
    
    # wait for Pi to finish sending start and 
    # wait for ACK from DHT11
    while GPIO.input(channel) == GPIO.LOW:
        continue
    while GPIO.input(channel) == GPIO.HIGH:
        continue
    
    # Begin data transfer, data sent in 40 bit chunks
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
    
    # Convert the raw bits into whole and fractional parts, e.g. 23.8C
    # compute checksum and store in the check variable
    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7 - i)
        humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
        temperature += temperature_bit[i] * 2 ** (7 - i)
        temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
        check += check_bit[i] * 2 ** (7 - i)
    tmp = humidity + humidity_point + temperature + temperature_point
    if check == tmp:
        THdata.append(str(temperature) + "." + str(temperature_point))
        # Convert C to F and append to returned data
        temp = float(THdata[0])
        f = "{:.4}".format(ctof(temp))
        THdata.append(f)
        THdata.append(str(humidity) + "%")
        now = str(datetime.now())
        if VERBOSE:
            print("%s: temperature: %sC %sF\thumidity: %s" % (now, THdata[0], THdata[1], THdata[2]))
        return THdata
    else:
        # bad checksum, try again...
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
    # append temp in C, F, and humidity as a percentage to CSV file
    data.append(dhtdata[0])
    data.append(dhtdata[1])
    data.append(dhtdata[2])
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
