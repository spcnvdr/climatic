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
# To setup, run this command: pip3 install apscheduler                    #
# To run normally putting the output data in current directory:           #
#    ./collect_data.py                                                    #
# To run in background: ./collect_data.py &                               #
###########################################################################

import argparse
import time
import csv
from os.path import isfile
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import RPi.GPIO as GPIO

# Default file name to store data in
CSV_FILE = "climate_data.csv"

# Columns definitions for the CSV file
COLUMNS = ["Timestamp", "Celsius", "Fahrenheit", "Humidity"]

# Number of seconds in an hour, collect temp/humidity every hour
HOUR = 3600

# The data collection interval in seconds, may be changed on command line
# with the -t/--time option
INTERVAL = HOUR

# Verbose and auto mode options
VERBOSE = False
AUTO = False

# Other globals
outfile = CSV_FILE

# save original filename for appending to in auto mode,
# and the time of the when we started the current CSV output file
original_file = ""
start_time = datetime.now()


# Create a new, unique file name based on the old file name
#  @param filename string the old file name
#  @returns a string consisting of the old filename with the date appended
#    to it
#
def new_filename(filename):
    newfilename = ""
    date = datetime.now()
    # append year, month, day - hour, minute to filename to make it unique
    strdate = date.strftime("%Y%m%d-%H%M")
    if "." in filename:
        temp = filename.split(".")
        newfilename = temp[0] + strdate + "." + temp[1]
    else:
        newfilename = filename + strdate
    return newfilename


# Roll the output file over to a new file
#  @param filename string the original filename
#  @returns the new output file name
#
def rollover_file(filename):
    global start_time

    newfile = new_filename(filename)
    while isfile(newfile):
        # TODO: Come up with a less shitty solution
        # If this file already exists, append Xs until we have a unique name
        if "." in newfile:
            temp = newfile.split(".")
            newfile = temp[0] + "X" + "." + temp[1]
        else:
            newfile += "X"

    # create the new file
    create_csv(newfile)
    # Reset the start time counter
    start_time = datetime.now()
    return newfile


# Convert a temperature in Celsius to Fahrenheit
#  @param temperature the temperature in Celsius to convert
#  @returns temperature as a float
#
def ctof(temperature):
    return ((temperature / 5) * 9) + 32


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
        return THdata
    else:
        # bad checksum, try again...
        time.sleep(1)
        return collect()


# Collect temperature and humidity data every hour
def timed_job():
    global outfile
    days_running = (datetime.now() - start_time).days
    if AUTO and days_running:
        outfile = rollover_file(original_file)

    data = []
    # create timestamp as first column
    data.append(str(datetime.now()))
    # collect data
    dhtdata = collect()
    temp_hum = float(dhtdata[2].strip("%"))
    while(temp_hum > 100):
        dhtdata = collect()
        temp_hum = float(dhtdata[2].strip("%"))

    # append temp in C, F, and humidity as a percentage to CSV file
    data.append(dhtdata[0])
    data.append(dhtdata[1])
    data.append(dhtdata[2])
    append_data(outfile, data)
    if VERBOSE:
        print("%s: temperature: %sC %sF\thumidity: %s" %
              (data[0], data[1], data[2], data[3]))


# Create a new CSV file with the correct column definitions
# called if the CSV file to append to does not exist
#  @param filename the name of CSV file to create
#
def create_csv(filename):
    with open(filename, "a", newline="") as fd:
        writer = csv.writer(fd)
        writer.writerow(COLUMNS)


# Append a row of data to the CSV file, creating it if necessary
#  @param filename string the name of the CSV file to open
#  @param data a list of strings containing the data to append
#  @returns number of bytes successfully stored in the CSV file
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
                                   "store temperature and humidity data in a "
                                   "CSV file\nConnect the DHT11 data pin to "
                                   "Raspberry Pi pin 7")
    argp.add_argument("-a",
                      "--auto", help="Automatically store data in a new CSV "
                      "file every 24 hours", action="store_true")
    argp.add_argument("-o",
                      "--output", help="Store data in a different output file")
    argp.add_argument("-t",
                      "--time", help="Collect data every N seconds",
                      metavar="N", type=int)
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

    # If custom collection interval specified, use it
    if args.time:
        if args.time < 60:
            print("Error: time option CANNOT be less than 60 seconds!")
            exit(1)
        INTERVAL = args.time

    if args.auto:
        # enable auto mode, calculate when to roll over based on record count,
        # and save original filename for later modification
        AUTO = True
        original_file = outfile

    # If output file does not exist, create it
    if not isfile(outfile):
        create_csv(outfile)

    # Start the hourly task
    try:
        sched = BlockingScheduler()
        sched.add_job(timed_job, 'interval', seconds=INTERVAL)
        sched.start()
    except KeyboardInterrupt:
        print("Received Ctrl+c, exiting...")
        sched.shutdown()
        exit(0)
