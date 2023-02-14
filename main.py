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
    switch_connect = handle_connection(get_ip_address)

    int_status = switch_connect.send_command("sh int status", use_textfsm=True)

    unconnected_switchports = []

    for interface in int_status:
        if interface['status'] == "notconnect":
            print("Interface [ {sp} ] is notconnect.".format(sp=interface['port']))
            unconnected_switchports.append(interface)


if __name__ == "__main__":
    main()
    print("PatchFinder Done")

