# Patch Finder

A quick tool for identifying available/least used switchports on Cisco IOS.

The program will output all non-connected switchports, as well as their percentage usage relative to the top-talker.

## How it works
1. **Connect to the switch with netmiko**
a. Netmiko connection currently uses two environment variables: <i>S_USERNAME</i> and <i>S_PASSWORD</i> 
2. **Iterate all interfaces**
a. Fetch individual interface information
b. Calculate & store <i>input_packets + output_packets<sup> [1]</sup></i>
c. Store all nonconnect interfaces
3. **Iterate all nonconnect interfaces**
a. Display *interface, input_packets, output_packets* and the result of
<i>(input_packets + output_packets / maximum<sup> [1]</sup>) * 100</i>

The program also displays <strong>Port Description</strong>, <strong>VLAN</strong> and <strong>Last Input</strong>.

## Dependencies

- **Netmiko** <br>pip install netmiko==4.1.2
- **python-dotenv**<br>pip install python-dotenv
- **Rich**<br>pip install rich
