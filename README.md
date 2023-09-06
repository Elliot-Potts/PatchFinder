# Patch Finder

A tool for identifying available/least used switchports on Cisco IOS switches.

The program will output relevant information on all non-connected switchports, as well as their percentage usage relative to the top-talker.

## How it works

1. **Connect to the switch with Netmiko**
2. **Iterate all interfaces**
    1. Fetch individual interface information
    2. Calculate & store <i>input_packets + output_packets<sup> [1]</sup></i>
    3. Store all not-connect interfaces
3. **Iterate all not-connect interfaces**
    1. Display *interface, description, VLAN, last input, input packets, output packets* and the percentage use (result of<br><i>(input_packets + output_packets / maximum<sup> [1]</sup>) * 100</i>)

Additional information such as **Hostname**, **PoE details** and **System uptime** is also outputted.

## CLI Arguments

Optional command line arguments can be provided for faster use.

Usage: patchfinder.py [-h] [-i IP] [-u USERNAME] [-p PASSWORD]

<b>-h, --help</b> 
Show the help message      
<b>-i IP, --ip IP</b>
Address of the Cisco switch        
<b>-u USERNAME, --username USERNAME</b>
(leave empty to use environment PF_USERNAME)    
<b>-p PASSWORD, --password PASSWORD</b>
(leave empty to use environment PF_PASSWORD) 

## Dependencies

Built with Python 3 using:

- **Netmiko** <br>pip install netmiko
- **python-dotenv**<br>pip install python-dotenv
- **Rich**<br>pip install rich
