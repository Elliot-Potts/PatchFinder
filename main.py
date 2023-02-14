"""
TODO
- Add stat counter, maybe through sh int <INT> ['packets_in' & 'packets_out']
- Add switch uptime checker, 'show version'
- Add highest interface stat checker & percentage comparison
    - Iterate all interfaces, get packets_in and packets_out
    - Store highest in global
    - Iterate all notconnect interfaces, create percentage between
    - Display lowest percentages
"""

from netmiko import ConnectHandler, exceptions
from ciscoconfparse import CiscoConfParse
from dotenv import load_dotenv
from pprint import pprint
import time
import os


def handle_connection(switch_ip):
    load_dotenv()
    return ConnectHandler(host=switch_ip, username=os.environ.get("S_USERNAME"), password=os.environ.get("S_PASSWORD"), device_type="cisco_ios")


def main():
    get_ip_address = input("Enter switch IP: ")

    try:
        switch_connect = handle_connection(get_ip_address)
    except exceptions.NetmikoAuthenticationException:
        print("[-] Invalid username or password.")
        return
    except exceptions.NetmikoTimeoutException:
        print("[-] Connection timeout.")
        return

    int_status = switch_connect.send_command("sh int status", use_textfsm=True)
    # print(int_status)

    unconnected_switchports = {}

    for interface in int_status:
        if interface['status'] == "notconnect":
            print("\tInterface [ {sp} ] is notconnect.".format(sp=interface['port']))
            get_stats = switch_connect.send_command('show int {}'.format(interface['port']), use_textfsm=True)[0]
            get_stats = (get_stats['input_packets'], get_stats['output_packets'])
            print(get_stats)
            # unconnected_switchports[interface['port']] = switch_connect.send_command('show int {}'.format(interface['port']))

    time.sleep(1)
    print("Loading interface statistics.")

    # for notconnect in unconnected_switchports:



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Exiting via keyboard input.")
    
    print("PatchFinder Done")

