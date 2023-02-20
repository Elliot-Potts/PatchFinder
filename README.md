# Patch Finder

A quick tool for identifying available/least used switchports on Cisco IOS.

The program will output all non-connected switchports, as well as their percentage usage relative to the top-talker.

## How it works
1. **Connect to the switch with netmiko**
2. **Iterate all interfaces**
a. Fetch individual interface information
b. Calculate & store *input_packets + output_packets*<sup>1</sup>
c. Store all nonconnect interfaces
3. **Iterate all nonconnect interfaces**
a. Display *interface, input_packets, output_packets* and the result of
*(input_packets + output_packets / maximum<sup>1</sup>) * 100*

## Dependencies

- **Netmiko** <br>pip install netmiko==4.1.2
- **python-dotenv** (for loading username/password via .env files)<br>pip install python-dotenv
