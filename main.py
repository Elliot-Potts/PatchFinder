"""
TODO
- Add highest interface stat checker & percentage comparison
    - Iterate all interfaces, get packets_in and packets_out
    - Store highest (packets_in+packets_out) in global
    - Iterate all notconnect interfaces, create percentage between highest global
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
    # print(os.environ.get("S_USERNAME"), os.environ.get("S_PASSWORD"))
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

    print("Connected to {}\n".format(get_ip_address))
    switch_uptime = switch_connect.send_command("sh version", use_textfsm=True)[0]['uptime']
    int_status = switch_connect.send_command("sh int status", use_textfsm=True)
    print("Switch uptime is:\t{}\n".format(switch_uptime))

    all_stats = []
    unconnected_switchports = {}

    for interface in int_status:
        get_int_stats = switch_connect.send_command('show int {}'.format(interface['port']), use_textfsm=True)[0]
        get_int_stats = (get_int_stats['input_packets'], get_int_stats['output_packets'])

        if interface['status'] == "notconnect":
            # print("\tInterface [ {sp} ] is notconnect.".format(sp=interface['port']))
            unconnected_switchports[interface['port']] = get_int_stats

        stats_total = int(get_int_stats[0]) + int(get_int_stats[1])
        all_stats.append(stats_total)
    
    print(len(all_stats))
    print(all_stats)

    title = "-"*5 + " Not-connect Switchports " + "-"*5
    print(title + "\nPort\t\tInput\t\tOutput")

    for dc_switchport in unconnected_switchports:
        print("{switch_port}\t\t{input_packets}\t\t{output_packets}".format(
            switch_port=dc_switchport,
            input_packets=unconnected_switchports[dc_switchport][0],
            output_packets=unconnected_switchports[dc_switchport][1]
        ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Exiting via keyboard input.")

