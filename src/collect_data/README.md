# Collect_data - Measure and Record Temperature and Humidity

This program collects the current temperature and humidity and writes it to a
CSV file every hour. This requires a DHT11 module, a Raspberry Pi, and to 
have Rpi.GPIO installed on the Raspberry Pi. The current  version requires a 
user to manually execute this program to begin collecting data for later 
analysis.

**The Software**

The software will use Python 3.x.x and requires the RPi.GPIO library. It also 
depends on the apscheduler library. It is a good idea to install the 
apscheduler library outside of a virtual environment as the RPi.GPIO library 
did not play nicely with virtual environments.

**The Hardware**

A Raspberry Pi and a DHT11 sensor module are required. The physical connections 
are as follows:
DHT11 GND (pin 1) to Raspberry Pi ground (pin 6)
DHT11 DATA (pin 2) to Raspberry Pi pin 7
DHT11 VCC to Raspberry Pi 5 volts (pin 2)

**To Setup or Run**

First, get a copy of this code

    git clone https://github.com/spcnvdr/climatic.git

Change into the data collection directory with cd

    cd climatic/src/collect_data/

Setup a virtual environment to avoid polluting the system's Python packages

    python3 -m venv venv

Activate the virtual environment

    source venv/bin/activate

Install the required packages with Pip3

    pip3 install -r requirements.txt

Then run with --help for information about the arguments

    ./collect_data.py --help

To test the code without having to wait an hour, open the collect_data.py file
and modify the HOUR constant near the top of the file. To collect data every 
10 seconds for testing, change the constant from

    HOUR = 3600

To

    HOUR = 10

The name of the output CSV file can be changed with the -o argument

    ./collect_data.py -o new_data.csv

Verbose mode will print the temperature and humidity to the terminal while 
running

    ./collect_data.py -v

**Running in the Background**

To run the program in the background, append an ampersand to the command

    ./collect_data.py &

To kill a version running in the background, use the fg command to bring
it to the foreground and then send an interrupt with Ctrl+c to shut the program
down

    fg

    Ctrl+c

**To Do**

- [ ] Write column definitions at top of file when new CSV out file used