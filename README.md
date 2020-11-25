# Climatic - Python 3.x.x Group Project Part 2

The purpose of this Git repository and its contents is for the experimentation
and development of the second part of the Internet of Things Group Project
part 2 for the Fall 2020 semester. 
The goal of this project is to create a single Flask web page that 
either allows users to upload a CSV file or to use the current CSV file 
maintained by the web server. The web page will download the CSV file from the 
user, parse its contents, and (if valid) display information about the contents
of the file. The file is to contain information in CSV format, with Linux/UNIX
line endings (LF). The data in the CSV file will contain the current
temperature, humidity, date and time of collection, and any other pertinent 
information that can be gathered and stored by either additional sensors or 
by the Raspberry Pi itself.

**The Software**

The software will use Python 3.x.x and Flask for the web server and WiringPi 
for the Python code that interacts with the DHT11 temperature & humidity 
sensor. The web server will use Bootstrap to style the page, jQuery to 
assist with the JavaScript, and possibly Flot or Morris.js to create 
pretty looking graphs, tables, line charts, etc. 

**To Setup or Run**

Change into the web directory with cd

    cd code/web

Create the virtual environment if this is the first run

    python3 -m venv venv

Enable the virtual environment:

    source venv/bin/activate

Install any Python 3.x.x dependencies

    pip3 install -r requirements.txt 

Then run the main Python 3.x.x script

    ./main

Then open a web browser to port 5000 on the localhost:

    127.0.0.1:5000

By default, the web server will listen on any public IP address and can be 
reached by any device on the same network, so be careful!

The default credentials are:

    username: admin

    password: admin

**To Do**

- [ ] Determine the exact format of CSV files to use
- [ ] Finish the web page that will parse CSV files and display information
- [ ] Make it possible to change the username and password


**Contributing**

Pull requests, new feature suggestions, and bug reports/issues are
welcome.


**Versioning**

This project uses semantic versioning 2.0. Version numbers follow the
MAJOR.MINOR.PATCH format.


**License**

This project is licensed under the 3-Clause BSD License also known as the
*"New BSD License"* or the *"Modified BSD License"*. A copy of the license
can be found in the LICENSE file. A copy can also be found at the
[Open Source Institute](https://opensource.org/licenses/BSD-3-Clause)


**Acknowledgments**

This project makes use of many other open source software. This project would
not be possible without the hard work of other software developers. Below is a 
list of projects that are used by this code and links to their respective 
websites are given as well. This list is NOT exhaustive and in no particular 
order. The list below is subject to change without notice. 

Project - Website

* Python 3.x.x - https://www.python.org/

* Bootstrap 4 - https://getbootstrap.com/

* Popper.js - https://popper.js.org/

* jQuery - https://jquery.com/

* Morris.js - https://morrisjs.github.io/morris.js/

* Raphael - https://dmitrybaranovskiy.github.io/raphael/

* Glyphicons (As part of Bootstrap 4) - https://www.glyphicons.com/


**Security**

All commits will be signed with the following GPG key:
pub   rsa4096 2019-03-30 [SC]
      6E14 F46A EAA6 AE4B EFD5  8AAD 6E42 17B5 682C C50A
uid           [ultimate] Bryan Hawkins <spcnvdrr@protonmail.com>
sub   rsa4096 2019-03-30 [E]

The fingerprint for the signing key is:
6E14F46AEAA6AE4BEFD58AAD6E4217B5682CC50A
